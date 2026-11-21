"""Prepare a non-interactive desktop for each new learner home."""
from pathlib import Path
import configparser
import re
import sys


DIRECTORIES = {
    'DESKTOP': 'Desktop', 'DOWNLOAD': 'Downloads', 'TEMPLATES': 'Templates',
    'PUBLICSHARE': 'Public', 'DOCUMENTS': 'Documents', 'MUSIC': 'Music',
    'PICTURES': 'Pictures', 'VIDEOS': 'Videos',
}

DEFAULT_APPLICATIONS = {
    'chromium.desktop': ('x-scheme-handler/http', 'x-scheme-handler/https', 'text/html'),
    'caja-folder-handler.desktop': ('inode/directory',),
    'geany.desktop': ('text/plain',),
    'eom.desktop': ('image/png', 'image/jpeg', 'image/webp', 'image/gif', 'image/svg+xml'),
    'engrampa.desktop': ('application/zip', 'application/x-tar', 'application/gzip', 'application/x-7z-compressed'),
}

DISABLED_AUTOSTART = (
    'mate-power-manager.desktop', 'mate-screensaver.desktop',
    'nm-applet.desktop', 'user-dirs-update-gtk.desktop',
)


def configure(home: Path, applications: Path):
    config = home / '.config'
    config.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES.values():
        (home / directory).mkdir(exist_ok=True)
    (config / 'user-dirs.dirs').write_text(''.join(
        f'XDG_{key}_DIR="$HOME/{value}"\n' for key, value in DIRECTORIES.items()
    ))
    (config / 'user-dirs.locale').write_text('en_US\n')
    (config / 'mimeapps.list').write_text('[Default Applications]\n' + ''.join(
        f'{mime}={launcher};\n'
        for launcher, types in DEFAULT_APPLICATIONS.items() for mime in types
    ))
    autostart = config / 'autostart'
    autostart.mkdir(exist_ok=True)
    for name in DISABLED_AUTOSTART:
        (autostart / name).write_text('[Desktop Entry]\nType=Application\nHidden=true\n')

    # Parrot's shared skeleton also serves Plasma. Its KDE color reload module
    # does not belong to a MATE session; retain the other GTK preferences.
    gtk_file = config / 'gtk-3.0/settings.ini'
    if gtk_file.is_file():
        gtk = configparser.ConfigParser(interpolation=None, strict=False)
        gtk.read(gtk_file)
        modules = gtk.get('Settings', 'gtk-modules', fallback='').split(':')
        if 'colorreload-gtk-module' in modules:
            gtk['Settings']['gtk-modules'] = ':'.join(module for module in modules if module != 'colorreload-gtk-module')
            with gtk_file.open('w') as stream:
                gtk.write(stream)

    desktop_dir = home / 'Desktop'
    desktop_dir.mkdir(exist_ok=True)
    preferred_launchers = [
        'chromium.desktop',
        'mate-terminal.desktop',
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

    # User-level overrides keep package-owned launchers intact. Chromium is
    # the selected browser; vncconfig runs under the Worker supervisor.
    for desktop in sorted(applications.glob('*.desktop')):
        lines = desktop.read_text().splitlines()
        if desktop.name.startswith('firefox') or any(
            line.startswith('Exec=') and re.search(r'(?<![\w-])vncconfig(?![\w-])', line) for line in lines
        ):
            overrides = home / '.local/share/applications'
            overrides.mkdir(parents=True, exist_ok=True)
            (overrides / desktop.name).write_text('[Desktop Entry]\nType=Application\nHidden=true\n')


if __name__ == '__main__':
    configure(Path(sys.argv[1]), Path(sys.argv[2]))
