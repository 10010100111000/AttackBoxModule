"""Prepare a non-interactive desktop for each new learner home."""
from pathlib import Path
import configparser
import shlex
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
    'mate-user-share.desktop', 'mate-user-share-webdav.desktop',
    'mate-user-share-obexpush.desktop', 'mate-user-share-obexftp.desktop',
)


def hide_desktop_entry(source, destination, *, autostart=False):
    entry = configparser.ConfigParser(interpolation=None, strict=False)
    entry.optionxform = str
    entry.read(source)
    entry['Desktop Entry']['Hidden'] = 'true'
    if autostart:
        entry['Desktop Entry']['X-MATE-Autostart-enabled'] = 'false'
    with destination.open('w') as stream:
        entry.write(stream, space_around_delimiters=False)


def configure(home: Path, applications: Path, *, autostart_sources=Path('/etc/xdg/autostart')):
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
        source = autostart_sources / name
        if not source.is_file():
            source = autostart / name
        if source.is_file():
            hide_desktop_entry(source, autostart / name, autostart=True)

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

    configure_applications(home, applications)


def configure_applications(home, applications):
    # XDG user entries override system entries by desktop-file ID. Apply the
    # same policy to that effective set, including launchers inherited in skel.
    overrides = home / '.local/share/applications'
    entries = {path.name: (path, False) for path in applications.glob('*.desktop')}
    entries.update({path.name: (path, True) for path in overrides.glob('*.desktop')})
    for name, (source, local) in sorted(entries.items()):
        metadata = configparser.ConfigParser(interpolation=None, strict=False)
        metadata.optionxform = str
        metadata.read(source)
        entry = metadata['Desktop Entry']
        command = shlex.split(entry.get('Exec', ''))
        executable = Path(command[0]).name if command else ''
        changed = False
        if name.startswith('firefox') or executable in {'firefox', 'firefox-esr', 'firefox-selector', 'vncconfig'}:
            entry['Hidden'] = 'true'
            changed = True
        elif local and command and 'TryExec' not in entry:
            # Preserve useful inherited launchers while letting the menu hide
            # applications that are not installed in this desktop.
            entry['TryExec'] = command[0]
            changed = True
        if name == 'parrot-burpsuite.desktop':
            canonical = configparser.ConfigParser(interpolation=None)
            canonical.optionxform = str
            canonical.read(applications / 'burpsuite.desktop')
            entry['Exec'] = canonical['Desktop Entry']['Exec']
            changed = True
        if changed:
            overrides.mkdir(parents=True, exist_ok=True)
            with (overrides / name).open('w') as stream:
                metadata.write(stream, space_around_delimiters=False)


if __name__ == '__main__':
    configure(Path(sys.argv[1]), Path(sys.argv[2]))
