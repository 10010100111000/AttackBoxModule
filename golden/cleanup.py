"""Finalize a configured, unmounted golden rootfs before making it read-only."""
import json
from pathlib import Path
import sys


SYSTEM_CACHE = (
    'boot', 'usr/lib/modules', 'usr/lib/firmware', 'tmp', 'var/tmp', 'run',
    'var/log', 'var/lib/apt/lists', 'var/cache/apt/archives',
)
USER_CACHE = ('.cache', '.local/state', '.local/share/Trash', '.local/share/gvfs-metadata')
OTHER_DESKTOP = (
    '.config/xfce4', '.config/lxqt', '.config/pcmanfm-qt', '.config/openbox',
    '.config/lxpanel', '.config/i3', '.config/polybar',
    '.local/share/konsole', '.local/share/plasma-systemmonitor',
    '.config/nvim', '.local/share/nvim', '.mozilla',
)
USER_HISTORY = (
    '.bash_history', '.python_history', '.lesshst', '.viminfo', '.wget-hsts',
    '.local/share/recently-used.xbel', '.config/mate-session/saved-session',
)


def checked_path(root, relative):
    path = root / relative
    for parent in path.parents:
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError(f'Cleanup path has a symlink parent: {relative}')
    return path


def remove(path):
    """Return logical bytes of removed files, without following symlinks."""
    if path.is_symlink():
        path.unlink()
        return 0
    if path.is_dir():
        size = sum(remove(child) for child in path.iterdir())
        path.rmdir()
        return size
    if path.exists():
        size = path.stat().st_size
        path.unlink()
        return size
    return 0


def clean(root):
    root = root.resolve(strict=True)
    if root == Path('/'):
        raise ValueError('Cleanup requires a golden rootfs, not the host root')
    marker = root / 'etc/.attackbox_golden_ready'
    if json.loads(marker.read_text()) != {'format': 1, 'uid': 1001, 'gid': 1013}:
        raise ValueError('Rootfs is not a configured AttackBox golden image')
    report = {'format': 1, 'removed_packages': [], 'removed_file_bytes': {}}
    packages = checked_path(root, 'tmp/attackbox-build/removed-packages.tsv')
    if packages.is_file():
        for line in packages.read_text().splitlines():
            name, size = line.split('\t')
            report['removed_packages'].append({'name': name, 'installed_size_kib': int(size)})
    report['removed_packages_installed_kib'] = sum(
        item['installed_size_kib'] for item in report['removed_packages'])

    for relative in SYSTEM_CACHE:
        directory = checked_path(root, relative)
        size = remove(directory)
        directory.mkdir(parents=True, exist_ok=True)
        if relative in ('tmp', 'var/tmp'):
            directory.chmod(0o1777)
        report['removed_file_bytes'][relative] = size

    for home in ('etc/skel', 'root', 'home/box'):
        for relative in (*USER_CACHE, *OTHER_DESKTOP, *USER_HISTORY):
            path = f'{home}/{relative}'
            size = remove(checked_path(root, path))
            if size:
                report['removed_file_bytes'][path] = size

    for relative in ('etc/machine-id', 'var/lib/dbus/machine-id'):
        path = checked_path(root, relative)
        remove(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(mode=0o644)
    for pattern in ('etc/ssh/ssh_host_*',):
        for path in root.glob(pattern):
            remove(checked_path(root, str(path.relative_to(root))))
    for relative in ('etc/passwd-', 'etc/group-', 'etc/shadow-', 'etc/gshadow-',
                     'var/lib/systemd/random-seed', 'var/lib/urandom/random-seed'):
        remove(checked_path(root, relative))

    report['total_removed_file_bytes'] = sum(report['removed_file_bytes'].values())
    output = checked_path(root, 'usr/share/attackbox/cleanup-report.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: cleanup.py ROOTFS')
    report = clean(Path(sys.argv[1]))
    print(f"Removed packages: {report['removed_packages_installed_kib'] / 1024:.1f} MiB installed size; "
          f"cleaned file contents: {report['total_removed_file_bytes'] / 1024**2:.1f} MiB")
