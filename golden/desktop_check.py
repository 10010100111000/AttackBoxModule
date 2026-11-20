"""Validate the configured panel and observe desktop startup error dialogs."""
import ast
import configparser
import json
from pathlib import Path
import re
import subprocess
import sys
import time

THEME_SECTIONS = {
    'org/gtk/settings/file-chooser',
    'org/mate/desktop/interface',
    'org/mate/interface',
    'org/mate/desktop/background',
    'org/mate/marco/general',
    'org/mate/terminal/profiles/default',
}
ERROR_TITLE = re.compile(r'\b(error|warning|problem|failed|failure|missing|unable|could not)\b|错误|警告|问题|失败|无法', re.I)


class DesktopDialogError(RuntimeError):
    def __init__(self, windows):
        self.windows = windows
        super().__init__('Unexpected desktop error window: ' + json.dumps(windows, ensure_ascii=False))


def read_ini(path, *, strict=True):
    parser = configparser.ConfigParser(interpolation=None, delimiters=('=',), strict=strict)
    parser.optionxform = str
    with path.open() as stream:
        parser.read_file(stream)
    return parser


def write_theme(source, destination):
    # GLib key files permit duplicate keys; their last value wins.
    vendor = read_ini(source, strict=False)
    theme = configparser.ConfigParser(interpolation=None, delimiters=('=',))
    theme.optionxform = str
    for section in vendor.sections():
        if section in THEME_SECTIONS:
            theme[section] = dict(vendor[section])
    if not theme.sections():
        raise ValueError(f'No supported theme settings in {source}')
    with destination.open('w') as stream:
        theme.write(stream)


def applet_registry(root):
    registry = {}
    for file in sorted((root / 'usr/share/mate-panel/applets').glob('*.mate-panel-applet')):
        metadata = read_ini(file)
        factory = metadata['Applet Factory']
        for section in metadata.sections():
            if section != 'Applet Factory':
                iid = f'{factory["Id"]}::{section}'
                if iid in registry:
                    raise ValueError(f'Duplicate applet registration: {iid}')
                registry[iid] = (factory['Location'], factory.getboolean('InProcess', fallback=False))
    return registry


def validate_static(root):
    settings = configparser.ConfigParser(interpolation=None, delimiters=('=',))
    settings.optionxform = str
    for file in sorted((root / 'etc/dconf/db/local.d').iterdir()):
        if not file.is_file() or file.name.startswith('.'):
            continue
        defaults = read_ini(file)
        for section in defaults.sections():
            if section.startswith('org/mate/panel/'):
                if section != 'org/mate/panel/general' or any(
                    key in defaults[section] for key in ('object-id-list', 'toplevel-id-list')
                ):
                    raise ValueError(f'{file.name}: panel objects must be defined by the selected layout: {section}')
            if not settings.has_section(section):
                settings.add_section(section)
            settings[section].update(defaults[section])
    layout_name = ast.literal_eval(settings['org/mate/panel/general']['default-layout'])
    if not isinstance(layout_name, str) or not re.fullmatch(r'[\w-]+', layout_name):
        raise ValueError('Invalid default panel layout name')
    layout_path = root / f'usr/share/mate-panel/layouts/{layout_name}.layout'
    layout = read_ini(layout_path)
    panels = {section.removeprefix('Toplevel ') for section in layout.sections()
              if section.startswith('Toplevel ')}
    if not panels:
        raise ValueError(f'No panels in {layout_path}')
    registry = applet_registry(root)
    for section in layout.sections():
        if not section.startswith('Object '):
            continue
        obj = layout[section]
        if obj.get('toplevel-id') not in panels:
            raise ValueError(f'{section}: unknown panel {obj.get("toplevel-id")}')
        if obj.get('object-type') == 'applet':
            iid = obj['applet-iid']
            if iid not in registry:
                raise ValueError(f'{section}: applet is not installed: {iid}')
            location, in_process = registry[iid]
            implementation = root / location.lstrip('/')
            if not location.startswith('/') or not implementation.is_file():
                raise ValueError(f'{iid}: missing applet implementation: {location}')
            if not in_process and not implementation.stat().st_mode & 0o111:
                raise ValueError(f'{iid}: applet implementation is not executable: {location}')
        elif obj.get('object-type') == 'launcher':
            location = obj['launcher-location']
            if not location.startswith('/') or not (root / location.lstrip('/')).is_file():
                raise ValueError(f'{section}: missing desktop launcher: {location}')
    print(f'Panel layout validated: {layout_name}, {len(panels)} panels')


def desktop_owners(root):
    owners = {'mate-panel', 'mate-session', 'marco', 'caja', 'mate-settings-d'}
    for location, _ in applet_registry(root).values():
        owners.add(Path(location).name[:15])
    return owners


def is_error_window(window, owners):
    classes = set(window['class'].lower().split('.'))
    owned = bool(classes & owners) or window.get('process') in owners
    dialog = '_NET_WM_WINDOW_TYPE_DIALOG' in window['properties']
    error = bool(ERROR_TITLE.search(window['title']))
    return (dialog and (owned or error)) or (owned and error)


def list_windows():
    result = subprocess.run(['wmctrl', '-lpx'], check=True, capture_output=True, text=True)
    windows = []
    for line in result.stdout.splitlines():
        fields = line.split(None, 5)
        if len(fields) == 5:
            fields.append('')
        if len(fields) != 6 or not re.fullmatch(r'0x[0-9a-fA-F]+', fields[0]):
            raise ValueError(f'Unexpected wmctrl window record: {line}')
        identifier, _, pid, wmclass, _, title = fields
        result = subprocess.run(['xprop', '-id', identifier, '_NET_WM_WINDOW_TYPE'],
                                capture_output=True, text=True)
        if result.returncode:
            # Windows can close between enumeration and property lookup.
            if 'BadWindow' in result.stderr:
                continue
            raise RuntimeError(f'xprop failed for {identifier}: {result.stderr.strip()}')
        properties = result.stdout
        try:
            process = Path(f'/proc/{int(pid)}/comm').read_text().strip()
        except (OSError, ValueError):
            process = ''
        windows.append({'id': identifier, 'pid': pid, 'class': wmclass, 'title': title,
                        'process': process, 'properties': properties.strip()})
    return windows


def inspect_windows(owners):
    windows = list_windows()
    errors = [window for window in windows if is_error_window(window, owners)]
    if errors:
        raise DesktopDialogError(errors)
    return windows


def probe_error_dialog(owners):
    # Prove detection against a real X11 window, with a neutral title. The
    # fixture is confined to the disposable acceptance desktop.
    title = f'Desktop detector probe {time.monotonic_ns()}'
    process = subprocess.Popen(['xmessage', '-name', 'mate-panel', '-title', title,
                                '-buttons', 'OK:0', 'Synthetic applet startup failure'])
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            candidates = [window for window in list_windows() if window['title'] == title]
            if candidates:
                identifier = candidates[0]['id']
                break
            if process.poll() is not None:
                raise RuntimeError('X11 detector probe exited before mapping its window')
            time.sleep(0.1)
        else:
            raise RuntimeError('X11 detector probe did not map its window')
        subprocess.run(['xprop', '-id', identifier, '-f', '_NET_WM_WINDOW_TYPE', '32a',
                        '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DIALOG'], check=True)
        try:
            inspect_windows(owners)
        except DesktopDialogError as error:
            if not any(window['id'] == identifier for window in error.windows):
                raise
        else:
            raise RuntimeError('Desktop error dialog detector accepted the injected dialog')
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    deadline = time.monotonic() + 5
    while any(window['title'] == title for window in list_windows()):
        if time.monotonic() > deadline:
            raise RuntimeError('Detector probe window did not close')
        time.sleep(0.1)
    print('Injected desktop dialog was rejected; real desktop monitoring started', flush=True)


def watch_windows(stop_file):
    owners = desktop_owners(Path('/'))
    deadline = time.monotonic() + 20
    while True:
        wm = subprocess.run(['wmctrl', '-m'], capture_output=True, text=True)
        name = next((line.partition(':')[2].strip() for line in wm.stdout.splitlines()
                     if line.startswith('Name:')), '')
        if wm.returncode == 0 and name not in {'', 'N/A'}:
            break
        if time.monotonic() > deadline:
            raise RuntimeError('Window manager did not become ready')
        time.sleep(0.25)
    inspect_windows(owners)
    probe_error_dialog(owners)
    while True:
        windows = inspect_windows(owners)
        if stop_file.exists():
            print(json.dumps(windows, ensure_ascii=False, indent=2))
            return
        time.sleep(0.25)


if __name__ == '__main__':
    if sys.argv[1:2] == ['theme'] and len(sys.argv) == 4:
        write_theme(Path(sys.argv[2]), Path(sys.argv[3]))
    elif sys.argv[1:2] == ['static'] and len(sys.argv) == 3:
        validate_static(Path(sys.argv[2]))
    elif sys.argv[1:2] == ['watch'] and len(sys.argv) == 3:
        watch_windows(Path(sys.argv[2]))
    else:
        raise SystemExit('Usage: desktop_check.py theme SOURCE DESTINATION | static ROOTFS | watch STOP_FILE')
