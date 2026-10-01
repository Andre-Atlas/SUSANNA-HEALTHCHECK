"""Private per-user directory for temporary internet-demo credentials and logs."""
import os
from pathlib import Path


def state_dir():
    if os.name == 'nt':
        root = Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData/Local')
    elif sys_platform() == 'darwin':
        root = Path.home() / 'Library/Application Support'
    else:
        root = Path(os.environ.get('XDG_STATE_HOME') or Path.home() / '.local/state')
    folder = root / 'SUSANNA-HEALTHCHECK' / 'internet'
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name != 'nt':
        folder.chmod(0o700)
    return folder


def sys_platform():
    import sys
    return sys.platform
