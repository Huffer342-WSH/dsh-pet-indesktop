"""Read a bounded local session snapshot without replaying historical alerts."""
from __future__ import annotations

import json
import math
from pathlib import Path
import time

MAX_BYTES = 1024 * 1024
STALE_SECONDS = 1800
STATES = {'thinking', 'working', 'waiting', 'stopped', 'interrupted', 'closed'}


class SnapshotReader:
    def __init__(self, path, *, clock=time.time):
        self.path = Path(path).expanduser()
        self.clock = clock
        self._signature = None
        self._records = {}
        self._previous = None
        self._seen = None
        self._started_at = clock()

    def read(self):
        now = self.clock()
        try:
            stat = self.path.stat()
            signature = (stat.st_ino, stat.st_size, stat.st_mtime_ns)
            if signature != self._signature:
                with self.path.open('rb') as stream:
                    raw = stream.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise ValueError('snapshot too large')
                data = json.loads(raw)
                records = data['sessions']
                if data['version'] != 1 or not isinstance(records, dict) or len(records) > 128:
                    raise ValueError('unsupported snapshot')
                for record in records.values():
                    stamp = record['updated_at']
                    if record['state'] not in STATES or not isinstance(stamp, (int, float)) or not math.isfinite(stamp):
                        raise ValueError('invalid session')
                self._records, self._signature = records, signature
            records = self._records
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            # Missing, malformed or unreadable is not successful completion.
            self._signature = None
            if self._seen is None:
                self._seen = {}
            return self._changed({'busy': 0, 'waiting': 0, 'unknown': 1,
                                  'thinking': 0, 'tool': '', 'ended': []})
        summary = dict(busy=0, waiting=0, unknown=0, thinking=0, tool='', ended=[])
        seen = {}
        for key, entry in records.items():
            state = entry['state']
            seen[key] = state
            if state in {'thinking', 'working', 'waiting'}:
                if now - entry['updated_at'] > STALE_SECONDS or entry['updated_at'] > now + 60:
                    summary['unknown'] += 1
                elif state == 'waiting':
                    summary['waiting'] += 1
                else:
                    summary['busy'] += 1
                    summary['thinking'] += state == 'thinking'
                    summary['tool'] = str(entry.get('tool') or '')[:64]
            elif self._seen is not None and self._seen.get(key) not in {'stopped', 'interrupted', 'closed'}:
                if key in self._seen or entry['updated_at'] >= self._started_at:
                    summary['ended'].append(state)
        self._seen = seen
        return self._changed(summary)

    def _changed(self, summary):
        stable = {key: value for key, value in summary.items() if key != 'ended'}
        if stable == self._previous and not summary['ended']:
            return None
        self._previous = stable
        return summary
