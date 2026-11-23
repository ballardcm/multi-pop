#!/usr/bin/env python3
"""Exercise the Odin 2 release package: its contents, version stamping and private-file exclusion."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load('release', 'package-release.py')


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='single-pop-release-')
        self.addCleanup(self.temp.cleanup)
        # The fixture repository mirrors the monorepo: this system under systems/odin2, artwork under shared/.
        self.top = Path(self.temp.name)
        self.root = self.top / 'systems/odin2'
        self.root.mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(self.top)], check=True)
        files = {'.gitignore': 'private/\ndist/\n', 'multi-pop-odin2/theme.xml': '<theme/>',
                 'multi-pop-odin2/README.md': 'Install instructions', 'multi-pop-odin2/LICENSE': 'License',
                 'multi-pop-odin2/LICENSING.md': 'Scope',
                 'multi-pop-odin2/version.xml': '<variables><multiPopVersion>DEVELOPMENT</multiPopVersion></variables>',
                 'private/secret.env': 'Must not ship'}
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def package(self, version=7):
        return release.package(self.root, self.root / 'dist', version)

    def test_manifest_matches_contents_and_private_files_stay_out(self):
        ready, source, sums = self.package()
        with zipfile.ZipFile(ready) as archive:
            manifest = json.loads(archive.read('install-manifest.json'))
            for name, digest in manifest.items():
                self.assertEqual(hashlib.sha256(archive.read('multi-pop-odin2/' + name)).hexdigest(), digest)
            self.assertEqual(json.loads(archive.read('multi-pop-odin2/version.json')), {'version': 7})
            self.assertIn(b'<multiPopVersion>7</multiPopVersion>', archive.read('multi-pop-odin2/version.xml'))
            # The stock frontend runs the theme, so no binary may ever be bundled into the Odin 2 download.
            self.assertFalse(any('/frontend/' in name for name in archive.namelist()))
        with zipfile.ZipFile(source) as archive:
            self.assertFalse(any('private/' in name for name in archive.namelist()))
        self.assertIn(release.sha256(ready), sums.read_text())

    def test_missing_required_file_is_rejected(self):
        (self.root / 'multi-pop-odin2/LICENSING.md').unlink()
        with self.assertRaisesRegex(ValueError, 'missing required files'):
            self.package()

    def test_symlink_cannot_import_outside_file(self):
        (self.root / 'multi-pop-odin2/external.txt').symlink_to(self.root / 'private/secret.env')
        with self.assertRaisesRegex(ValueError, 'only into the shared folder'):
            self.package()

    def test_links_into_shared_are_packaged_as_files(self):
        # The theme links to the one copy of the artwork in shared/; the download must carry the files themselves.
        artwork = self.top / 'shared/assets/systems'
        artwork.mkdir(parents=True)
        (artwork / 'snes.png').write_bytes(b'Shared artwork')
        (self.top / 'shared/platforms.json').write_text('{}')
        subprocess.run(['git', 'add', 'shared'], cwd=self.top, check=True)
        (self.root / 'multi-pop-odin2/assets').mkdir()
        (self.root / 'multi-pop-odin2/assets/systems').symlink_to('../../../../shared/assets/systems')
        (self.root / 'multi-pop-odin2/platforms.json').symlink_to('../../../shared/platforms.json')
        ready, source, _ = self.package()
        with zipfile.ZipFile(ready) as archive:
            self.assertEqual(archive.read('multi-pop-odin2/assets/systems/snes.png'), b'Shared artwork')
            self.assertEqual(archive.read('multi-pop-odin2/platforms.json'), b'{}')
            self.assertIn('assets/systems/snes.png', json.loads(archive.read('install-manifest.json')))
        with zipfile.ZipFile(source) as archive:
            self.assertEqual(archive.read('multi-pop-odin2-source/multi-pop-odin2/assets/systems/snes.png'), b'Shared artwork')

    def test_link_to_untracked_shared_file_is_rejected(self):
        (self.top / 'shared').mkdir()
        (self.top / 'shared/draft.png').write_bytes(b'Not committed')
        (self.root / 'multi-pop-odin2/draft.png').symlink_to('../../../shared/draft.png')
        with self.assertRaisesRegex(ValueError, 'files Git tracks'):
            self.package()

    def test_repeated_packages_are_identical(self):
        first = {path.name: path.read_bytes() for path in self.package()}
        second = {path.name: path.read_bytes() for path in self.package()}
        self.assertEqual(first, second)

    def test_date_label_is_packaged_separately_from_update_order(self):
        (self.root / 'release-version.json').write_text(json.dumps({'schema_version': 1, 'date': '2026-11-22', 'revision': 1}))
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        self.assertEqual(release.release_version(self.root), 20261122001)
        ready, _, _ = self.package(20261122001)
        with zipfile.ZipFile(ready) as archive:
            self.assertEqual(json.loads(archive.read('multi-pop-odin2/version.json')),
                             {'version': 20261122001, 'display_version': '11.22.26.1'})
            self.assertIn(b'<multiPopVersion>11.22.26.1</multiPopVersion>', archive.read('multi-pop-odin2/version.xml'))
        with self.assertRaisesRegex(ValueError, 'configured date release'):
            self.package(25)


if __name__ == '__main__':
    unittest.main(verbosity=2)
