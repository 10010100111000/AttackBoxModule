import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cleanup', ROOT / 'cleanup.py')
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'rootfs'
        self.write('etc/.attackbox_golden_ready', json.dumps({'format': 1, 'uid': 1001, 'gid': 1013}))

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        return path

    def test_caches_and_other_desktops_removed_but_credentials_and_gui_caches_survive(self):
        discarded = ['tmp/build.data', 'var/cache/apt/archives/archive.deb', 'var/log/build.log',
                     'home/box/.cache/cache.data', 'home/box/.local/share/Trash/files/old.txt',
                     'home/box/.config/mate-session/saved-session/session.desktop',
                     'etc/skel/.local/share/nvim/plugin/data', 'root/.bash_history']
        retained = ['home/box/.java/.userPrefs/burp/prefs.xml',
                    'home/box/.local/share/pki/nssdb/cert9.db',
                    'home/box/.config/autostart/mate-power-manager.desktop',
                    'home/box/.config/gtk-3.0/settings.ini', 'etc/dconf/db/local',
                    'var/cache/fontconfig/fonts.cache', 'usr/share/man/man1/nmap.1',
                    'usr/share/icons/hackthebox/icon-theme.cache', 'var/lib/dpkg/status']
        for path in discarded + retained:
            self.write(path, 'keep-or-remove')
        self.write('etc/machine-id', 'builder-id')
        self.write('tmp/attackbox-build/removed-packages.tsv', 'mate-user-guide\t82021\n')
        self.write('etc/ssh/ssh_host_ed25519_key', 'builder-key')
        report = cleanup.clean(self.root)
        for name in discarded:
            self.assertFalse((self.root / name).exists(), name)
        for name in retained:
            self.assertEqual((self.root / name).read_text(), 'keep-or-remove', name)
        self.assertGreater(report['total_removed_file_bytes'], 0)
        self.assertEqual(report['removed_packages_installed_kib'], 82021)
        self.assertEqual((self.root / 'etc/machine-id').read_text(), '')
        self.assertFalse((self.root / 'etc/ssh/ssh_host_ed25519_key').exists())
        self.assertEqual((self.root / 'tmp').stat().st_mode & 0o7777, 0o1777)
        self.assertEqual(cleanup.clean(self.root)['total_removed_file_bytes'], 0)

    def test_symlink_cache_is_unlinked_without_touching_its_target(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (outside / 'keep').write_text('outside')
        home = self.root / 'home/box'
        home.mkdir(parents=True)
        (home / '.cache').symlink_to(outside, target_is_directory=True)
        cleanup.clean(self.root)
        self.assertEqual((outside / 'keep').read_text(), 'outside')
        self.assertFalse((home / '.cache').exists())

    def test_symlink_parent_rejected_without_following_it(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (outside / 'keep').write_text('outside')
        (self.root / 'var').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink parent'):
            cleanup.clean(self.root)
        self.assertEqual((outside / 'keep').read_text(), 'outside')

    def test_host_and_unconfigured_root_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'host root'):
            cleanup.clean(Path('/'))
        self.write('etc/.attackbox_golden_ready', '{}')
        with self.assertRaisesRegex(ValueError, 'not a configured'):
            cleanup.clean(self.root)


if __name__ == '__main__':
    unittest.main()
