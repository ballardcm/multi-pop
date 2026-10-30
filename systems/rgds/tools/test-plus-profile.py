#!/usr/bin/env python3
"""Check safety boundaries of the generated RG DS Plus release profile."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1]).resolve()
theme = root / 'multi-pop-rgds'
config = json.loads((root / 'frontend-build/release.json').read_text())
report = json.loads((theme / 'frontend/compatibility.json').read_text())
assert report['hardware'] == 'Anbernic RG DS Plus'
assert report['canvas'] == [3072, 768] and report['panel'] == [1024, 768]
assert report['artifact_sha256'] == config['frontend']['sha256']
for name, expected in config['build_inputs'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
guard = (theme / 'scripts/multi_pop_rgds_common.sh').read_text()
assert "== 'Anbernic RG DS Plus'" in guard and "== 'Anbernic RG DS'" not in guard
for layout in ('system.xml', 'games.xml'):
    tree = ET.parse(theme / 'layouts' / layout)
    for name in ('hero-instruction', 'top-touch-hints'):
        assert tree.find(f'.//text[@name="{name}"]') is None
    back = tree.find('.//text[@name="top-library-back"]')
    assert back is None or back.findtext('visible') == 'false'
spec = importlib.util.spec_from_file_location('plus_updater_test', theme / 'scripts/auto_update.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
for tag in ('rgds-10.30.26.1', 'thor-10.30.26.1', 'rgds-plus-10.30.26.Preview'):
    assert module.TAG.fullmatch(tag) is None, tag
assert module.Config().theme == Path('/roms/themes/multi-pop-rgds')
print('PASS: Plus firmware inputs, hardware guard, lower-only touch UI and update-feed isolation')
