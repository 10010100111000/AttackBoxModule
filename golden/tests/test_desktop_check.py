import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('desktop_check', ROOT / 'desktop_check.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class PanelContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in ['etc/dconf/db/local.d', 'usr/share/mate-panel/layouts',
                     'usr/share/mate-panel/applets', 'usr/libexec']:
            (self.root / path).mkdir(parents=True)
        self.defaults = self.root / 'etc/dconf/db/local.d'
        (self.defaults / 'attackbox').write_text("[org/mate/panel/general]\ndefault-layout='attackbox'\n")
        self.layout = self.root / 'usr/share/mate-panel/layouts/attackbox.layout'
        self.layout.write_text('[Toplevel top]\norientation=top\n'
                               '[Object clock]\nobject-type=applet\ntoplevel-id=top\n'
                               'applet-iid=ClockAppletFactory::ClockApplet\n')
        (self.root / 'usr/share/mate-panel/applets/clock.mate-panel-applet').write_text(
            '[Applet Factory]\nId=ClockAppletFactory\nInProcess=false\n'
            'Location=/usr/libexec/clock-applet\n[ClockApplet]\nName=Clock\n')
        self.binary = self.root / 'usr/libexec/clock-applet'
        self.binary.write_text('fixture')
        self.binary.chmod(0o755)

    def test_installed_applet_and_layout_are_valid(self):
        check.validate_static(self.root)

    def test_uninstalled_applet_is_rejected(self):
        self.layout.write_text(self.layout.read_text().replace(
            'ClockAppletFactory::ClockApplet', 'BriskMenuFactory::BriskMenu'))
        with self.assertRaisesRegex(ValueError, 'applet is not installed: BriskMenu'):
            check.validate_static(self.root)

    def test_installed_brisk_menu_is_supported(self):
        binary = self.root / 'usr/libexec/brisk-menu'
        binary.write_text('fixture')
        binary.chmod(0o755)
        (self.root / 'usr/share/mate-panel/applets/brisk.mate-panel-applet').write_text(
            '[Applet Factory]\nId=BriskMenuFactory\nLocation=/usr/libexec/brisk-menu\n[BriskMenu]\nName=Menu\n')
        self.layout.write_text(self.layout.read_text().replace(
            'ClockAppletFactory::ClockApplet', 'BriskMenuFactory::BriskMenu'))
        check.validate_static(self.root)

    def test_missing_factory_binary_is_rejected(self):
        self.binary.unlink()
        with self.assertRaisesRegex(ValueError, 'missing applet implementation'):
            check.validate_static(self.root)

    def test_inherited_panel_objects_are_rejected(self):
        (self.defaults / 'htb-config').write_text(
            "[org/mate/panel/objects/old-menu]\napplet-iid='BriskMenuFactory::BriskMenu'\n")
        with self.assertRaisesRegex(ValueError, 'panel objects must be defined'):
            check.validate_static(self.root)

    def test_missing_launcher_is_rejected(self):
        self.layout.write_text(self.layout.read_text() +
                               '[Object browser]\nobject-type=launcher\ntoplevel-id=top\n'
                               'launcher-location=/usr/share/applications/missing.desktop\n')
        with self.assertRaisesRegex(ValueError, 'missing desktop launcher'):
            check.validate_static(self.root)

    def test_unknown_panel_is_rejected(self):
        self.layout.write_text(self.layout.read_text().replace('toplevel-id=top', 'toplevel-id=unknown'))
        with self.assertRaisesRegex(ValueError, 'unknown panel'):
            check.validate_static(self.root)

    def test_theme_extraction_does_not_inherit_desktop_structure(self):
        source, dest = self.root / 'vendor', self.root / 'theme'
        source.write_text("[org/mate/desktop/interface]\ngtk-theme='Old'\ngtk-theme='Parrot'\n"
                          "[org/mate/panel/general]\nobject-id-list=['old-menu']\n"
                          "[org/mate/panel/objects/old-menu]\napplet-iid='BriskMenuFactory::BriskMenu'\n"
                          "[org/mate/desktop/keybindings/custom1]\naction='missing-app'\n")
        check.write_theme(source, dest)
        theme = check.read_ini(dest)
        self.assertEqual(theme.sections(), ['org/mate/desktop/interface'])
        self.assertEqual(theme['org/mate/desktop/interface']['gtk-theme'], "'Parrot'")


class ErrorWindowTests(unittest.TestCase):
    owners = {'mate-panel', 'clock-applet'}

    def window(self, title, wmclass='mate-panel.Mate-panel', kind='DIALOG'):
        return {'title': title, 'class': wmclass, 'process': '',
                'properties': '_NET_WM_WINDOW_TYPE_' + kind}

    def test_panel_dialog_is_rejected_even_without_error_in_title(self):
        self.assertTrue(check.is_error_window(self.window('Panel'), self.owners))

    def test_panel_problem_without_dialog_type_is_rejected(self):
        self.assertTrue(check.is_error_window(self.window('There was a problem loading an applet', kind='NORMAL'), self.owners))

    def test_browser_article_with_error_in_title_is_not_rejected(self):
        self.assertFalse(check.is_error_window(self.window('Error handling and problem solving', 'chromium.Chromium', 'NORMAL'), self.owners))

    def test_generic_error_dialog_is_rejected(self):
        self.assertTrue(check.is_error_window(self.window('Error', 'zenity.Zenity'), self.owners))

    def test_normal_panel_is_not_rejected(self):
        self.assertFalse(check.is_error_window(self.window('Top Panel', kind='DOCK'), self.owners))

    def test_window_closing_during_inspection_is_not_a_failure(self):
        results = [subprocess.CompletedProcess([], 0, '0x01 0 999999 mate-panel.Mate-panel host Top Panel\n0x02 0 999998 chromium.Chromium host\n', ''),
                   subprocess.CompletedProcess([], 1, '', 'X Error: BadWindow'),
                   subprocess.CompletedProcess([], 0, '_NET_WM_WINDOW_TYPE_NORMAL', '')]
        with patch.object(check.subprocess, 'run', side_effect=results):
            windows = check.inspect_windows(self.owners)
        self.assertEqual([window['id'] for window in windows], ['0x02'])

    def test_empty_startup_client_list_is_valid(self):
        results = [subprocess.CompletedProcess([], 1, '', 'Cannot get client list properties. (_NET_CLIENT_LIST or _WIN_CLIENT_LIST)'),
                   subprocess.CompletedProcess([], 0, '_NET_CLIENT_LIST: not found.', '')]
        with patch.object(check.subprocess, 'run', side_effect=results):
            self.assertEqual(check.inspect_windows(self.owners), [])

    def test_wmctrl_failure_with_existing_clients_is_rejected(self):
        results = [subprocess.CompletedProcess([], 1, '', 'Cannot get client list properties. (_NET_CLIENT_LIST or _WIN_CLIENT_LIST)'),
                   subprocess.CompletedProcess([], 0, '_NET_CLIENT_LIST(WINDOW): window id # 0x1234', '')]
        with patch.object(check.subprocess, 'run', side_effect=results):
            with self.assertRaisesRegex(RuntimeError, 'wmctrl failed'):
                check.inspect_windows(self.owners)

    def test_x11_connection_failure_is_not_ignored(self):
        results = [subprocess.CompletedProcess([], 0, '0x01 0 999999 mate-panel.Mate-panel host Panel\n', ''),
                   subprocess.CompletedProcess([], 1, '', 'Unable to open display')]
        with patch.object(check.subprocess, 'run', side_effect=results):
            with self.assertRaisesRegex(RuntimeError, 'Unable to open display'):
                check.inspect_windows(self.owners)


if __name__ == '__main__':
    unittest.main()
