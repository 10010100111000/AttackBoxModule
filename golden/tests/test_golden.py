import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


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


class SourceTests(unittest.TestCase):
    def test_packages_are_unique_concrete_names(self):
        packages = [line.split('#')[0].strip() for line in (ROOT / 'packages.txt').read_text().splitlines()]
        packages = [name for name in packages if name]
        self.assertEqual(len(packages), len(set(packages)))
        for name in packages:
            self.assertRegex(name, r'^[a-z0-9][a-z0-9+.-]+$')

    def test_shell_syntax(self):
        for script in ROOT.glob('*.sh'):
            subprocess.run(['bash', '-n', str(script)], check=True)


if __name__ == '__main__':
    unittest.main()
