import importlib.util
from pathlib import Path
import subprocess
import shutil
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

    def test_missing_theme_resource_is_rejected(self):
        (self.defaults / 'theme').write_text("[org/mate/desktop/interface]\ngtk-theme='Missing'\n")
        with self.assertRaisesRegex(ValueError, 'missing theme resource: Missing'):
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

    def test_theme_does_not_copy_session_tuning_or_obsolete_keys(self):
        source, dest = self.root / 'vendor', self.root / 'theme'
        source.write_text("[org/mate/marco/general]\ntheme='Parrot'\nside-by-side-tiling=true\n"
                          "compositing-manager=true\n[org/mate/terminal/profiles/default]\n"
                          "foreground-color='#ffffff'\nscrollback-unlimited=true\n")
        check.write_theme(source, dest)
        theme = check.read_ini(dest)
        self.assertEqual(dict(theme['org/mate/marco/general']), {'theme': "'Parrot'"})
        self.assertEqual(dict(theme['org/mate/terminal/profiles/default']), {'foreground-color': "'#ffffff'"})


@unittest.skipUnless(shutil.which('gsettings') and shutil.which('glib-compile-schemas'), 'GLib tools unavailable')
class SettingsContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.schemas = self.root / 'usr/share/glib-2.0/schemas'
        self.schemas.mkdir(parents=True)
        (self.schemas / 'test.gschema.xml').write_text(
            '<schemalist><schema id="org.attackbox.test" path="/org/attackbox/test/">'
            '<key name="animations" type="b"><default>true</default></key></schema></schemalist>')
        subprocess.run(['glib-compile-schemas', str(self.schemas)], check=True)
        self.defaults = self.root / 'etc/dconf/db/local.d'
        self.defaults.mkdir(parents=True)

    def test_valid_settings_are_accepted(self):
        (self.defaults / 'test').write_text('[org/attackbox/test]\nanimations=false\n')
        check.validate_settings(self.root)

    def test_wrong_path_key_and_type_are_rejected(self):
        for section, key, value, message in (
            ('org/attackbox/wrong', 'animations', 'false', 'no installed schema'),
            ('org/attackbox/test', 'wrong', 'false', 'No such key'),
            ('org/attackbox/test', 'animations', "'false'", 'value'),
        ):
            with self.subTest(section=section, key=key, value=value):
                (self.defaults / 'test').write_text(f'[{section}]\n{key}={value}\n')
                with self.assertRaisesRegex(ValueError, message):
                    check.validate_settings(self.root)

    def test_project_settings_do_not_claim_distribution_relocatable_settings(self):
        (self.defaults / 'project').write_text('[org/attackbox/test]\nanimations=false\n')
        (self.defaults / 'distribution').write_text('[org/gnome/desktop/app-folders/folders/info]\nname=\'Information\'\n')
        check.validate_settings(self.root, sources=('project',))
        with self.assertRaises(FileNotFoundError):
            check.validate_settings(self.root, sources=('missing-project',))


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

    def test_unnamed_keyring_prompt_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            owners = check.desktop_owners(Path(temp))
        self.assertTrue(check.is_error_window(self.window('', 'gcr-prompter.Gcr-prompter'), owners))

    def test_normal_panel_is_not_rejected(self):
        self.assertFalse(check.is_error_window(self.window('Top Panel', kind='DOCK'), self.owners))

    def properties(self, wmclass='mate-panel', title='Top Panel', kind='DOCK'):
        return (f'_NET_WM_PID(CARDINAL) = 999999\nWM_CLASS(STRING) = "{wmclass}", "{wmclass}"\n'
                f'_NET_WM_NAME(UTF8_STRING) = "{title}"\n_NET_WM_WINDOW_TYPE(ATOM) = _NET_WM_WINDOW_TYPE_{kind}\n')

    def test_window_closing_during_inspection_is_not_a_failure(self):
        results = [subprocess.CompletedProcess([], 0, '_NET_CLIENT_LIST(WINDOW): window id # 0x01, 0x02', ''),
                   subprocess.CompletedProcess([], 1, self.properties(title='Error'), 'X Error: BadWindow'),
                   subprocess.CompletedProcess([], 0, self.properties(wmclass='chromium', title='Page', kind='NORMAL'), '')]
        with patch.object(check.subprocess, 'run', side_effect=results):
            windows = check.inspect_windows(self.owners)
        self.assertEqual([window['id'] for window in windows], ['0x02'])

    def test_empty_startup_client_list_is_valid(self):
        result = subprocess.CompletedProcess([], 0, '_NET_CLIENT_LIST: not found.', '')
        with patch.object(check.subprocess, 'run', return_value=result):
            self.assertEqual(check.inspect_windows(self.owners), [])

    def test_root_query_failure_is_rejected_even_if_badwindow(self):
        for message in ['Unable to open display', 'X Error: BadWindow']:
            with self.subTest(message=message):
                result = subprocess.CompletedProcess([], 1, '', message)
                with patch.object(check.subprocess, 'run', return_value=result):
                    with self.assertRaisesRegex(RuntimeError, 'X11 client list failed'):
                        check.inspect_windows(self.owners)

    def test_x11_connection_failure_is_not_ignored(self):
        results = [subprocess.CompletedProcess([], 0, '_NET_CLIENT_LIST(WINDOW): window id # 0x01', ''),
                   subprocess.CompletedProcess([], 1, '', 'Unable to open display')]
        with patch.object(check.subprocess, 'run', side_effect=results):
            with self.assertRaisesRegex(RuntimeError, 'Unable to open display'):
                check.inspect_windows(self.owners)

    def test_closed_window_does_not_hide_a_surviving_error_dialog(self):
        results = [subprocess.CompletedProcess([], 0, '_NET_CLIENT_LIST(WINDOW): window id # 0x01, 0x02', ''),
                   subprocess.CompletedProcess([], 1, '', 'X Error: BadWindow'),
                   subprocess.CompletedProcess([], 0, self.properties(title='Panel problem', kind='DIALOG'), '')]
        with patch.object(check.subprocess, 'run', side_effect=results):
            with self.assertRaises(check.DesktopDialogError) as error:
                check.inspect_windows(self.owners)
        self.assertEqual(error.exception.windows[0]['id'], '0x02')

    def test_titles_and_classes_are_read_as_properties_not_whitespace_columns(self):
        result = self.properties(wmclass='chromium (/tmp/profile)', title='中文 title', kind='NORMAL')
        result = result.replace('_NET_WM_NAME(UTF8_STRING)', 'WM_NAME(STRING)')
        with patch.object(check.subprocess, 'run', side_effect=[
            subprocess.CompletedProcess([], 0, '_NET_CLIENT_LIST(WINDOW): window id # 0x01', ''),
            subprocess.CompletedProcess([], 0, result, ''),
        ]):
            window = check.list_windows()[0]
        self.assertEqual(window['title'], '中文 title')
        self.assertEqual(window['class'], 'chromium (/tmp/profile).chromium (/tmp/profile)')


if __name__ == '__main__':
    unittest.main()
