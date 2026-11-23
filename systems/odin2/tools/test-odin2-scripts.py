#!/usr/bin/env python3
"""Run Single Pop's touchscreen helper, installer and remover against a fake Odin 2."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'multi-pop-odin2/scripts'


class OdinScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='single-pop-device-')
        self.addCleanup(self.temp.cleanup)
        self.top = Path(self.temp.name)
        self.storage = self.top / 'storage'
        (self.storage / '.config/emulationstation').mkdir(parents=True)
        # The theme is installed as a copy, as it would be on the device, so the remover may delete it.
        self.theme = self.storage / 'roms/themes/multi-pop-odin2'
        (self.theme / 'scripts').mkdir(parents=True)
        (self.theme / 'theme.xml').write_text('<theme/>')
        for script in SCRIPTS.glob('*.sh'):
            shutil.copy2(script, self.theme / 'scripts' / script.name)
        self.model = self.top / 'model'
        self.model.write_bytes(b'AYN Odin 2\x00')
        # systemctl is replaced by a stub that records each call instead of touching the host.
        self.bin = self.top / 'bin'
        self.bin.mkdir()
        self.calls = self.top / 'systemctl.log'
        stub = self.bin / 'systemctl'
        stub.write_text(f'#!/bin/sh\necho "$*" >> "{self.calls}"\n')
        stub.chmod(0o755)
        self.env = dict(os.environ, PATH=f'{self.bin}:{os.environ["PATH"]}', SINGLE_POP_STORAGE=str(self.storage),
                        SINGLE_POP_MODEL=str(self.model))

    def run_script(self, name, *args, env=None):
        return subprocess.run(['sh', str(self.theme / 'scripts' / name), *args], env=env or self.env,
                              capture_output=True, text=True)

    def systemctl(self):
        return self.calls.read_text().splitlines() if self.calls.exists() else []

    def fake_sysfs(self, bound):
        sysfs = self.top / 'sys'
        device = sysfs / 'bus/i2c/devices/4-0020'
        device.mkdir(parents=True)
        (device / 'name').write_text('rmi4-i2c\n')
        other = sysfs / 'bus/i2c/devices/1-0034'
        other.mkdir(parents=True)
        (other / 'name').write_text('aw88166\n')
        driver = sysfs / 'bus/i2c/drivers/rmi4_i2c'
        driver.mkdir(parents=True)
        (driver / 'bind').write_text('')
        if bound:
            (device / 'driver').symlink_to(driver)
        return sysfs

    def touch(self, sysfs):
        env = dict(self.env, SINGLE_POP_SYSFS=str(sysfs), SINGLE_POP_TRIES='2', SINGLE_POP_WAIT='0')
        return self.run_script('odin2_touch.sh', env=env)

    def test_touch_helper_rebinds_only_an_unclaimed_controller(self):
        sysfs = self.fake_sysfs(bound=False)
        result = self.touch(sysfs)
        # The fake bind cannot bring the device up, so the helper gives up after its tries and says so.
        self.assertEqual(result.returncode, 1)
        self.assertIn('still missing', result.stderr)
        self.assertEqual((sysfs / 'bus/i2c/drivers/rmi4_i2c/bind').read_text(), '4-0020\n')

    def test_touch_helper_leaves_a_working_touchscreen_alone(self):
        sysfs = self.fake_sysfs(bound=True)
        result = self.touch(sysfs)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((sysfs / 'bus/i2c/drivers/rmi4_i2c/bind').read_text(), '')

    def test_install_adds_and_starts_the_boot_service(self):
        result = self.run_script('install_single_pop.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        unit = (self.storage / '.config/system.d/single-pop-touch.service').read_text()
        helper = self.storage / '.config/single-pop/odin2_touch.sh'
        self.assertIn('After=sway.service', unit)
        self.assertIn(f'ExecStart=/bin/sh {helper}', unit)
        self.assertIn('WantedBy=multi-user.target', unit)
        self.assertTrue(os.access(helper, os.X_OK))
        self.assertEqual(self.systemctl(), ['daemon-reload', 'enable single-pop-touch.service',
                                            'start single-pop-touch.service'])
        self.assertIn('Theme Set', result.stdout)

    def test_install_refuses_other_devices(self):
        self.model.write_bytes(b'AYN Thor\x00')
        result = self.run_script('install_single_pop.sh')
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.storage / '.config/system.d').exists())
        self.assertEqual(self.systemctl(), [])

    def test_remove_waits_until_another_theme_is_selected(self):
        self.run_script('install_single_pop.sh')
        settings = self.storage / '.config/emulationstation/es_settings.cfg'
        settings.write_text('<config>\n\t<string name="ThemeSet" value="multi-pop-odin2" />\n</config>\n')
        result = self.run_script('remove_single_pop.sh')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Nothing was changed', result.stderr)
        self.assertTrue((self.storage / '.config/system.d/single-pop-touch.service').exists())
        self.assertTrue(self.theme.is_dir())

    def test_remove_undoes_the_install_and_deletes_the_theme(self):
        self.run_script('install_single_pop.sh')
        result = self.run_script('remove_single_pop.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.storage / '.config/system.d/single-pop-touch.service').exists())
        self.assertFalse((self.storage / '.config/single-pop').exists())
        self.assertFalse(self.theme.exists())
        self.assertEqual(self.systemctl()[-2:], ['disable single-pop-touch.service', 'daemon-reload'])

    def test_remove_can_keep_the_theme(self):
        self.run_script('install_single_pop.sh')
        settings = self.storage / '.config/emulationstation/es_settings.cfg'
        settings.write_text('<config>\n\t<string name="ThemeSet" value="multi-pop-odin2" />\n</config>\n')
        result = self.run_script('remove_single_pop.sh', '--keep-theme')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.storage / '.config/system.d/single-pop-touch.service').exists())
        self.assertTrue((self.theme / 'theme.xml').is_file())


if __name__ == '__main__':
    unittest.main(verbosity=2)
