"""Headless packaged hook entry: never import Qt or create a pet window."""
import os
from pathlib import Path
import runpy
import sys


def main():
    try:
        # Windows windowed PyInstaller builds set Python streams to None even when
        # their parent supplies redirected handles. Reopen those supplied pipes.
        if sys.platform == 'win32' and (sys.stdin is None or sys.stdout is None):
            import ctypes
            from ctypes import wintypes
            import msvcrt
            get_handle = ctypes.windll.kernel32.GetStdHandle
            get_handle.argtypes = [wintypes.DWORD]
            get_handle.restype = wintypes.HANDLE
            for name, code, flags, mode in [('stdin', -10, os.O_RDONLY, 'r'), ('stdout', -11, os.O_WRONLY, 'w')]:
                if getattr(sys, name) is None:
                    handle = get_handle(code)
                    if handle in (None, 0, ctypes.c_void_p(-1).value):
                        return 0
                    fd = msvcrt.open_osfhandle(handle, flags)
                    setattr(sys, name, os.fdopen(fd, mode, encoding='utf-8'))
        root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
        runpy.run_path(str(root / 'integrations/dsh-pet-codex/scripts/bridge.py'), run_name='__main__')
    except SystemExit as exc:
        return exc.code or 0
    except Exception:
        if sys.stdout is not None:
            print('{}')
    return 0
