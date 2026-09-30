#!/usr/bin/env python3
"""Fail-open Codex hook writer. Standard library only; never emits model context."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

MAX_BYTES = 1024 * 1024
MAX_SESSIONS = 128
TERMINAL = {'stopped', 'interrupted', 'closed'}
EVENTS = {'UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'PermissionRequest',
          'Stop', 'Interrupt', 'SessionEnd'}


def directory() -> Path:
    override = os.environ.get('DSH_PET_BRIDGE_DIR')
    if override:
        return Path(override).expanduser()
    # Shared by the three local clients; independent of plugin cache/version.
    return Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex') / 'dsh-pet-bridge'


@contextmanager
def locked(path):
    with path.open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        deadline = time.monotonic() + 0.5
        while True:
            try:
                if os.name == 'nt':
                    import msvcrt
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError('bridge lock busy')
                time.sleep(0.005)
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def record(payload: dict, root: Path) -> None:
    event = payload.get('hook_event_name')
    session = str(payload.get('session_id') or '')[:200]
    turn = str(payload.get('turn_id') or '')[:200]
    if event not in EVENTS or not session or (not turn and event != 'SessionEnd'):
        return
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with locked(root / 'state.lock'):
        path = root / 'state.json'
        try:
            with path.open('rb') as stream:
                data = json.loads(stream.read(MAX_BYTES + 1))
            if data.get('version') != 1 or not isinstance(data.get('sessions'), dict):
                return  # A newer/corrupt schema must not be silently overwritten.
        except FileNotFoundError:
            data = {'version': 1, 'sessions': {}}
        sessions = data['sessions']
        session_key = hashlib.sha256(session.encode()).hexdigest()[:32]
        key = hashlib.sha256((session + '\0' + turn).encode()).hexdigest()[:32]
        now = time.time()
        if event == 'SessionEnd':
            for entry in sessions.values():
                if entry['session'] == session_key and entry['state'] not in TERMINAL:
                    entry.update(state='closed', updated_at=now, event=event)
        else:
            entry = sessions.get(key)
            if entry is None:
                # Ignore child/tool events without a root prompt. This also avoids
                # treating a late completion from before installation as a new task.
                if event != 'UserPromptSubmit':
                    return
                entry = {'session': session_key, 'state': 'thinking', 'calls': {}, 'tool': ''}
                sessions[key] = entry
            elif entry['state'] in TERMINAL:
                return  # A delayed tool hook must not revive a terminal turn.
            elif event == 'UserPromptSubmit':
                return  # Duplicate delivery must not reset work or waiting.
            call_id = str(payload.get('tool_use_id') or '')
            call = hashlib.sha256(call_id.encode()).hexdigest()[:32] if call_id else ''
            tool = str(payload.get('tool_name') or '').lower()
            tool = {'bash': 'bash', 'apply_patch': 'edit', 'read': 'read',
                    'web_search': 'search'}.get(tool, 'tool')
            if event == 'UserPromptSubmit':
                entry['state'] = 'thinking'
            elif event == 'PreToolUse':
                if call and len(entry['calls']) < 128:
                    entry['calls'][call] = tool
                entry.update(state='working', tool=tool)
            elif event == 'PostToolUse':
                entry['calls'].pop(call, None)
                entry.update(state='working' if entry['calls'] else 'thinking', tool='')
            elif event == 'PermissionRequest':
                entry.update(state='waiting', tool=tool)
            else:
                entry.update(state='stopped' if event == 'Stop' else 'interrupted', calls={}, tool='')
            entry.update(event=event, updated_at=now)
        # Bounded snapshot: keep the most recently updated turns, never transcripts.
        data['sessions'] = dict(sorted(sessions.items(), key=lambda item: item[1]['updated_at'])[-MAX_SESSIONS:])
        fd, temporary = tempfile.mkstemp(prefix='.state-', dir=root)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                json.dump(data, stream, ensure_ascii=False, separators=(',', ':'))
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(raw) <= MAX_BYTES:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                record(payload, directory())
    except Exception:
        # Telemetry must never reject a prompt, tool or permission request.
        pass
    print('{}')  # Stop hooks require JSON; no decisions or additionalContext.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
