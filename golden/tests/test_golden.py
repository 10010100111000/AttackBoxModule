import importlib.util
import json
from pathlib import Path
import subprocess
import shutil
import ssl
import http.client
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('artifact', ROOT / 'artifact.py')
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.parts = [self.root / f'attackbox-golden.btrfs.zst.part-{i:02d}' for i in range(2)]
        for index, part in enumerate(self.parts):
            part.write_bytes(f'part {index}'.encode())
        self.manifest = artifact.create(self.root, '1.0.0', 'a' * 40)

    def tearDown(self):
        self.temp.cleanup()

    def test_ordered_parts_and_checksums(self):
        self.assertEqual(artifact.verify(self.manifest), self.parts)
        sums = (self.root / 'attackbox-golden.sha256').read_text()
        self.assertIn(artifact.checksum(self.parts[0]), sums)

    def test_corruption_is_rejected_before_receive(self):
        self.parts[0].write_bytes(b'broken')
        with self.assertRaisesRegex(ValueError, 'Checksum'):
            artifact.verify(self.manifest)

    def test_path_traversal_and_reordering_are_rejected(self):
        original = self.manifest.read_text()
        for name in ['../outside', self.parts[1].name]:
            data = json.loads(original)
            data['parts'][0]['name'] = name
            self.manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'name or order'):
                artifact.verify(self.manifest)

    def test_missing_and_symlinked_parts_are_rejected(self):
        self.parts[0].unlink()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            artifact.verify(self.manifest)
        self.parts[0].symlink_to(self.parts[1])
        with self.assertRaisesRegex(ValueError, 'Missing'):
            artifact.verify(self.manifest)

    def test_unlisted_stale_parts_are_not_received(self):
        (self.root / 'attackbox-golden.btrfs.zst.part-99').write_text('stale')
        self.assertEqual(artifact.verify(self.manifest), self.parts)

    def test_empty_artifacts_and_invalid_versions_fail(self):
        for version in ['../escape', '01.0.0', '1.0', 'latest', '1.0.0;false']:
            with self.subTest(version=version), self.assertRaises(ValueError):
                artifact.validate_version(version)
        for path in self.parts:
            path.unlink()
        with self.assertRaisesRegex(ValueError, 'part count'):
            artifact.create(self.root, '1.0.0', 'a' * 40)


class MountTests(unittest.TestCase):
    def shell(self, command):
        return subprocess.run(['bash', '-c', 'source "$1"\n' + command,
                               '_', str(ROOT / 'mounts.sh')], capture_output=True, text=True)

    def test_partial_mount_failure_still_unmounts_prior_mounts_in_reverse(self):
        result = self.shell('''
mount() { [[ "${!#}" != failing ]]; }
mountpoint() { return 0; }
umount() { printf '%s\\n' "$1"; }
mount_image proc first
mount_image sys second
mount_image dev failing || true
unmount_image
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['second', 'first'])

    def test_failed_unmount_is_reported(self):
        result = self.shell('MOUNTS=(busy); mountpoint() { return 0; }; umount() { return 1; }; unmount_image')
        self.assertNotEqual(result.returncode, 0)


class DesktopTests(unittest.TestCase):
    def test_directories_and_menu_overrides(self):
        spec = importlib.util.spec_from_file_location('desktop', ROOT / 'desktop_defaults.py')
        desktop = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(desktop)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / 'box'
            applications = root / 'applications'
            applications.mkdir()
            (applications / 'vncconfig.desktop').write_text('[Desktop Entry]\nExec=vncconfig -iconic\n')
            (applications / 'chromium.desktop').write_text('[Desktop Entry]\nExec=chromium\n')
            desktop.configure(home, applications)
            desktop.configure(home, applications)
            self.assertTrue((home / '.local/share/applications/vncconfig.desktop').exists())
            self.assertFalse((home / '.local/share/applications/chromium.desktop').exists())
            self.assertTrue((home / 'Public').is_dir())
            self.assertIn('XDG_PUBLICSHARE_DIR="$HOME/Public"', (home / '.config/user-dirs.dirs').read_text())
            self.assertEqual((home / '.config/user-dirs.locale').read_text(), 'en_US\n')


class BurpProfileTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('burp_ca', ROOT / 'burp_ca.py')
        self.burp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.burp)

    def test_seed_keeps_ca_and_license_without_device_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            directory = home / '.java/.userPrefs/burp'
            directory.mkdir(parents=True)
            (directory / 'community').mkdir()
            (directory / 'community/window-state').write_text('build only')
            prefs = directory / 'prefs.xml'
            prefs.write_text('<map MAP_XML_VERSION="1.0">'
                             '<entry key="caCert" value="test-private-key"/>'
                             '<entry key="eulacommunity" value="accepted"/>'
                             '<entry key="global.suite.deviceId" value="build-device"/>'
                             '</map>')
            self.burp.retain_seed_preferences(home)
            result = {entry.get('key'): entry.get('value') for entry in ET.parse(prefs).getroot()}
            self.assertEqual(result, {'caCert': 'test-private-key', 'eulacommunity': 'accepted'})
            self.assertEqual(prefs.stat().st_mode & 0o777, 0o600)
            self.assertFalse((directory / 'community').exists())
            self.assertIn('<!DOCTYPE map SYSTEM', prefs.read_text())

    def test_tls_context_only_trusts_selected_ca(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                            '-keyout', str(temp / 'key.pem'), '-out', str(temp / 'ca.pem'),
                            '-days', '1', '-subj', '/CN=Test CA'], check=True, capture_output=True)
            certificate = ssl.PEM_cert_to_DER_cert((temp / 'ca.pem').read_text())
            context = self.burp.trusted_ca_context(certificate)
            self.assertTrue(context.check_hostname)
            self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
            self.assertEqual(context.get_ca_certs(binary_form=True), [certificate])
            with self.burp.https_fixture() as port:
                connection = http.client.HTTPSConnection('localhost', port, timeout=5, context=context)
                try:
                    with self.assertRaises(ssl.SSLCertVerificationError):
                        connection.request('GET', '/')
                finally:
                    connection.close()

    def test_missing_ca_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            directory = home / '.java/.userPrefs/burp'
            directory.mkdir(parents=True)
            (directory / 'prefs.xml').write_text('<map><entry key="eulacommunity" value="accepted"/></map>')
            with self.assertRaisesRegex(RuntimeError, 'did not persist'):
                self.burp.retain_seed_preferences(home)


class SourceTests(unittest.TestCase):
    def test_packages_are_unique_concrete_names(self):
        packages = [line.split('#')[0].strip() for line in (ROOT / 'packages.txt').read_text().splitlines()]
        packages = [name for name in packages if name]
        self.assertEqual(len(packages), len(set(packages)))
        for name in packages:
            self.assertRegex(name, r'^[a-z0-9][a-z0-9+.-]+$')

    def test_selected_toolset_and_browser(self):
        packages = {line.split('#')[0].strip() for line in (ROOT / 'packages.txt').read_text().splitlines()}
        self.assertTrue({'chromium', 'chromium-sandbox', 'burpsuite', 'geany', 'freerdp3-x11',
                         'postgresql-client', 'golang-go', 'nodejs', 'npm', 'enum4linux-ng'} <= packages)
        self.assertFalse({'firefox-esr', 'webext-foxyproxy', 'parrot-interface-common',
                          'parrot-menu', 'parrot-updater', 'caido', 'bloodhound',
                          'remmina', 'enum4linux', 'kerberoast'} & packages)

    def test_browser_policies_install_distinct_extensions(self):
        policy = json.loads((ROOT / 'chromium-policy.json').read_text())
        entries = policy['ExtensionInstallForcelist']
        ids = [entry.split(';')[0] for entry in entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 3)
        for entry in entries:
            self.assertRegex(entry, r'^[a-p]{32};https://clients2\.google\.com/service/update2/crx$')
        self.assertFalse(policy['BackgroundModeEnabled'])
        self.assertEqual(policy['BrowserSignin'], 0)

    @unittest.skipUnless(shutil.which('dconf'), 'dconf compiler is unavailable')
    def test_mate_defaults_compile(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            source = path / 'defaults'
            source.mkdir()
            shutil.copyfile(ROOT / 'mate-defaults.ini', source / 'attackbox')
            subprocess.run(['dconf', 'compile', str(path / 'compiled'), str(source)], check=True)

    def test_shell_syntax(self):
        for script in [*ROOT.glob('*.sh'), *ROOT.joinpath('skel').iterdir(), *ROOT.joinpath('bin').iterdir()]:
            subprocess.run(['bash', '-n', str(script)], check=True)


if __name__ == '__main__':
    unittest.main()
