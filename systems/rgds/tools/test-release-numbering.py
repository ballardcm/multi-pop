"""Exercise the legacy-302 migration and first-parent release numbering."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release', Path(__file__).with_name('package-release.py'))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class NumberingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.commit('legacy release')
        self.anchor = self.git('rev-parse', 'HEAD').strip()
        self.config = {'schema_version': 1, 'base_version': 302, 'base_commit': self.anchor}
        self.write_config()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True, stderr=subprocess.DEVNULL)

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-q', '--allow-empty', '-m', message)

    def write_config(self):
        (self.root / 'release-numbering.json').write_text(json.dumps(self.config))

    def test_first_numbered_release_advances_legacy302(self):
        self.commit('numbering migration')
        self.assertEqual(release.release_version(self.root), 303)

    def test_merge_number_ignores_topic_commit_count(self):
        self.git('checkout', '-q', '-b', 'topic')
        self.commit('first change')
        self.commit('second change')
        self.assertEqual(release.release_version(self.root), 304)
        self.git('checkout', '-q', 'main')
        self.git('merge', '-q', '--no-ff', 'topic', '-m', 'reviewed merge')
        self.assertEqual(release.release_version(self.root), 303)
        self.commit('another reviewed change')
        self.assertEqual(release.release_version(self.root), 304)

    def test_missing_history_is_not_silently_renumbered(self):
        self.config['base_commit'] = 'f' * 40
        self.write_config()
        self.assertRaisesRegex(ValueError, 'first-parent history', release.release_version, self.root)

    def test_invalid_baseline_is_rejected(self):
        self.config['base_version'] = True
        self.write_config()
        self.assertRaisesRegex(ValueError, 'baseline', release.release_version, self.root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
