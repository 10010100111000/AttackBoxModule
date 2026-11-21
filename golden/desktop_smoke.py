"""Exercise everyday desktop functions inside the disposable acceptance session."""
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import time

from desktop_check import list_windows, read_ini
from desktop_defaults import DEFAULT_APPLICATIONS


def run(*args, **kwargs):
    result = subprocess.run(args, capture_output=True, timeout=15, **kwargs)
    if result.returncode:
        raise RuntimeError(f'{shlex.join(args)}: {result.stderr.decode(errors="replace").strip()}')
    return result


def wait_for(check, description):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(0.1)
    raise RuntimeError(f'Desktop function did not become ready: {description}')


def clipboard(target):
    result = subprocess.run(['xclip', '-selection', 'clipboard', '-out', '-target', target],
                            capture_output=True, timeout=3)
    return result.stdout if result.returncode == 0 else b''


def validate_handlers():
    for launcher, types in DEFAULT_APPLICATIONS.items():
        entry = read_ini(Path('/usr/share/applications') / launcher)['Desktop Entry']
        for key in ('Exec', 'TryExec'):
            if key in entry and not shutil.which(shlex.split(entry[key])[0]):
                raise RuntimeError(f'{launcher}: missing program in {key}')
        for mime in types:
            default = run('xdg-mime', 'query', 'default', mime).stdout.decode().strip()
            if default != launcher:
                raise RuntimeError(f'{mime}: expected {launcher}, got {default}')


def open_document(path, application):
    # Launched GUI applications may inherit their parent's streams and keep
    # them open. Do not wait for those streams to close before checking X11.
    subprocess.run(['gio', 'open', str(path)], check=True, timeout=15)
    def mapped():
        return any(application in window['class'].lower().split('.') for window in list_windows())
    wait_for(mapped, f'{path.name} opened with {application}')
    for window in list_windows():
        if application in window['class'].lower().split('.'):
            run('wmctrl', '-ic', window['id'])


def verify_desktop():
    validate_handlers()
    with tempfile.TemporaryDirectory(prefix='desktop-smoke-', dir=Path.home()) as temp:
        root = Path(temp)
        # Use the real screenshot tool and X11 clipboard, without a save dialog.
        screenshot = subprocess.Popen(['mate-screenshot', '--clipboard'])
        try:
            def has_image():
                image = clipboard('image/png')
                if not image.startswith(b'\x89PNG\r\n\x1a\n'):
                    return False
                (root / 'screenshot.png').write_bytes(image)
                return True
            wait_for(has_image, 'screenshot on clipboard')
            open_document(root / 'screenshot.png', 'eom')
        finally:
            if screenshot.poll() is None:
                screenshot.terminate()
            screenshot.wait(timeout=5)

        owner = subprocess.Popen(['xclip', '-selection', 'clipboard', '-in', '-quiet'], stdin=subprocess.PIPE)
        try:
            owner.stdin.write(b'AttackBox clipboard check')
            owner.stdin.close()
            wait_for(lambda: clipboard('UTF8_STRING') == b'AttackBox clipboard check',
                     'text clipboard')
        finally:
            if owner.poll() is None:
                owner.terminate()
            owner.wait(timeout=5)

        text = root / 'note.txt'
        text.write_text('AttackBox desktop acceptance\n')
        open_document(text, 'geany')
        marker = root / 'terminal.ok'
        command = shlex.join(['/usr/bin/touch', str(marker)])
        run('mate-terminal', '--disable-factory', '-x', '/bin/sh', '-c', command)
        wait_for(marker.is_file, 'terminal command')
        run('zip', '-j', str(root / 'note.zip'), str(text))
        if run('unzip', '-p', str(root / 'note.zip'), 'note.txt').stdout != text.read_bytes():
            raise RuntimeError('Archive roundtrip changed the document')
        run('gio', 'trash', str(marker))
        if marker.exists():
            raise RuntimeError('GIO trash did not remove the test file')
    print('Desktop handlers, screenshot, image viewer, editor, terminal, clipboard, archive and trash passed')


if __name__ == '__main__':
    verify_desktop()
