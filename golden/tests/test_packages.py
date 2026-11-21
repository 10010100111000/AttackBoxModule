"""Exercise removal policy before invoking a destructive APT transaction."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackagePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.list = Path(self.temp.name) / 'packages.txt'

    def shell(self, body):
        return subprocess.run(['bash', '-euo', 'pipefail', '-c', 'source "$1"\n' + body,
                               '_', str(ROOT / 'packages.sh'), str(self.list)],
                              capture_output=True, text=True)

    def test_list_preserves_names_and_rejects_invalid_or_combined_entries(self):
        self.list.write_text(' # comment\n firefox-esr # explanation\n\tbluez\t\n')
        result = self.shell('read_packages "$2" names; printf "%s\\n" "${names[@]}"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['firefox-esr', 'bluez'])
        for entry in ['firefox bluez', 'firefox*', '-oAPT::Something=true', 'firefox;true']:
            with self.subTest(entry=entry):
                self.list.write_text(entry)
                self.assertNotEqual(self.shell('read_packages "$2" names').returncode, 0)

    def test_absent_packages_do_not_trigger_apt(self):
        self.list.write_text('firefox-esr\n')
        result = self.shell('dpkg-query() { return 1; }; apt-get() { echo UNEXPECTED; }; remove_packages "$2"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('UNEXPECTED', result.stdout)

    def test_unlisted_cascade_blocks_real_purge(self):
        self.list.write_text('firefox-esr\n')
        result = self.shell('''
dpkg-query() { echo installed; }
apt-get() {
  if [[ $1 == -s ]]; then
    printf 'Purg firefox-esr [1.0]\nRemv mate-panel [1.0]\n'
  else
    echo ACTUAL_PURGE
  fi
}
remove_packages "$2"
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('also delete mate-panel', result.stderr)
        self.assertNotIn('ACTUAL_PURGE', result.stdout)

    def test_explicit_removals_are_applied_without_autoremove(self):
        self.list.write_text('firefox-esr\nbluez\n')
        result = self.shell('''
dpkg-query() { echo installed; }
apt-get() {
  if [[ $1 == -s ]]; then
    printf 'Purg firefox-esr:amd64 [1.0]\nRemv bluez [1.0]\n'
  else
    printf 'ACTUAL %s\n' "$*"
  fi
}
remove_packages "$2"
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('ACTUAL purge -y -o APT::Get::AutomaticRemove=false firefox-esr bluez', result.stdout)

    def test_failed_simulation_blocks_real_purge(self):
        self.list.write_text('bluez\n')
        result = self.shell('''
dpkg-query() { echo installed; }
apt-get() { if [[ $1 == -s ]]; then return 1; else echo ACTUAL_PURGE; fi; }
remove_packages "$2"
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('ACTUAL_PURGE', result.stdout)


if __name__ == '__main__':
    unittest.main()
