"""Prepare a non-interactive desktop for each new learner home."""
from pathlib import Path
import re
import sys


DIRECTORIES = {
    'DESKTOP': 'Desktop', 'DOWNLOAD': 'Downloads', 'TEMPLATES': 'Templates',
    'PUBLICSHARE': 'Public', 'DOCUMENTS': 'Documents', 'MUSIC': 'Music',
    'PICTURES': 'Pictures', 'VIDEOS': 'Videos',
}


def configure(home: Path, applications: Path):
    config = home / '.config'
    config.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES.values():
        (home / directory).mkdir(exist_ok=True)
    (config / 'user-dirs.dirs').write_text(''.join(
        f'XDG_{key}_DIR="$HOME/{value}"\n' for key, value in DIRECTORIES.items()
    ))
    (config / 'user-dirs.locale').write_text('en_US\n')

    desktop_dir = home / 'Desktop'
    desktop_dir.mkdir(exist_ok=True)
    preferred_launchers = [
        'chromium.desktop',
        'mate-terminal.desktop',
        'attackbox-burpsuite.desktop',
        'burpsuite.desktop',
        'caja.desktop',
        'geany.desktop',
        'wireshark.desktop',
    ]
    for name in preferred_launchers:
        source = applications / name
        if source.is_file():
            target = desktop_dir / name
            target.write_text(source.read_text())
            target.chmod(0o755)

    # vncconfig remains available to the Worker for clipboard synchronization,
    # but learners do not need its low-level configuration launcher in the menu.
    for desktop in sorted(applications.glob('*.desktop')):
        lines = desktop.read_text().splitlines()
        if any(line.startswith('Exec=') and re.search(r'(?<![\w-])vncconfig(?![\w-])', line) for line in lines):
            overrides = home / '.local/share/applications'
            overrides.mkdir(parents=True, exist_ok=True)
            (overrides / desktop.name).write_text('[Desktop Entry]\nType=Application\nHidden=true\n')


if __name__ == '__main__':
    configure(Path(sys.argv[1]), Path(sys.argv[2]))
