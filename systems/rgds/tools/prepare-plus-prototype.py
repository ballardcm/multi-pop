#!/usr/bin/env python3
"""Stage an isolated, native-resolution RG DS Plus prototype for hardware testing.

AI assistance: Codex. This is not a registered release artifact. Original RG DS
release inputs remain unchanged; build and validate the staged frontend anew.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def replace_numbers(text, values):
    return re.sub(r'(?<![\w.])-?\d+(?:\.0)?(?![a-eg-zA-Z0-9_.])',
                  lambda m: values.get(m[0], m[0]), text)


def prepare(destination, release=False):
    if destination.exists():
        raise ValueError('Use a new destination')
    destination.mkdir(parents=True)
    files = subprocess.check_output(['git', 'ls-files', '-z', '.'], cwd=ROOT).decode().split('\0')
    for name in filter(None, files):
        source = ROOT / name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # Preserve unified-diff line counts and upstream context: scale additions only.
    dimensions = {'640': '1024', '480': '768', '1280': '2048', '1920': '3072',
                  '640.0': '1024.0', '600.0': '960.0', '960.0': '1536.0'}
    gesture = {'649': '1038', '695': '1112', '1294': '2070', '1364': '2182',
               '7': '11', '52': '83', '10': '16', '48': '77'}
    theme = destination / 'multi-pop-rgds'
    for name in ('system.xml', 'games.xml'):
        layout = theme / 'layouts' / name
        text = layout.read_text()
        text = re.sub(r'    <text name="(?:hero-instruction|top-touch-hints)"[^>]*>.*?\n    </text>\n',
                      '', text, flags=re.S)
        text = re.sub(r'(<text name="top-library-back"[^>]*>.*?)(</text>\s*<text name="top-game-system")',
                      r'\1  <visible>false</visible>\n    \2', text, flags=re.S)
        layout.write_text(text)
    for name in ('rgds-popup-placement.patch', 'rgds-game-paging.patch'):
        path = theme / 'frontend' / name
        lines = path.read_text().splitlines(keepends=True)
        in_gesture = False
        for index, line in enumerate(lines):
            if line.startswith('+++ b/es-core/src/components/ThorTouchGesture.h'):
                in_gesture = True
            if line.startswith('+') and not line.startswith('+++'):
                lines[index] = replace_numbers(line, dimensions | (gesture if in_gesture else {}))
        path.write_text(''.join(lines))
    for name in ('enable_multi_pop_rgds.sh', 'start_es_rgds.sh'):
        path = theme / 'scripts' / name
        path.write_text(replace_numbers(path.read_text(), dimensions | {'-640': '-1024'}))
    common = theme / 'scripts/multi_pop_rgds_common.sh'
    common.write_text(common.read_text().replace("== 'Anbernic RG DS'", "== 'Anbernic RG DS Plus'")
                      .replace('requires Anbernic RG DS hardware', 'requires Anbernic RG DS Plus hardware'))
    # A private test build must never consume an original-RG-DS automatic update.
    updater = theme / 'scripts/auto_update.py'
    updater.write_text(updater.read_text().replace("r'rgds-(", "r'rgds-plus-prototype-("))
    report = theme / 'frontend/compatibility.json'
    report.write_text(json.dumps({'hardware': 'Anbernic RG DS Plus', 'architecture': 'aarch64',
        'firmware': '20261001', 'canvas': [3072, 768], 'panel': [1024, 768],
        'device_validation': 'Pending prototype build and hardware validation'}, indent=2) + '\n')
    version = theme / 'version.json'
    data = json.loads(version.read_text())
    data['display_version'] = 'RG DS Plus test 1'
    version.write_text(json.dumps(data) + '\n')
    version_xml = theme / 'version.xml'
    version_xml.write_text(re.sub(r'(<multiPopVersion>).*?(</multiPopVersion>)',
                                 r'\g<1>RG DS Plus test 1\g<2>', version_xml.read_text()))
    # Exercise the actual generated gesture and popup code at Plus coordinates.
    checks = destination / 'tools/check-rgds.py'
    coordinate_map = {str(n): str(round(n * 1.6)) for n in
        (660, 20, 1310, 1400, 1500, 200, 1505, 202, 250, 1279, 800, 640, 1280, 750, 1300, 100, 150, 1350, 120)}
    text = checks.read_text()
    start = text.index("int main() {")
    end = text.index("}''')", start)
    text = text[:start] + replace_numbers(text[start:end], coordinate_map) + text[end:]
    # Gesture timestamps remain internally consistent; expected swipe step counts
    # remain unchanged because coordinates and thresholds scale together.
    checks.write_text(text)
    popup = destination / 'tools/test-popup-bounds.py'
    popup.write_text(replace_numbers(popup.read_text(), dimensions | {'600': '960'})
                     .replace('upper640px', 'upper1024px'))
    if release:
        shutil.copy2(ROOT / 'frontend-build/plus-release.json', destination / 'frontend-build/release.json')
        shutil.copy2(ROOT / 'frontend-build/plus-compatibility.json', report)
        shutil.copy2(ROOT / 'release-version-plus.json', destination / 'release-version.json')
        config = json.loads((destination / 'frontend-build/release.json').read_text())
        for name, expected in config['build_inputs'].items():
            if hashlib.sha256((destination / name).read_bytes()).hexdigest() != expected:
                raise ValueError('Plus compiler input changed; rebuild and validate a new frontend: ' + name)
        shutil.copy2(destination / 'README.md', destination / 'docs/original-rgds-readme.md')
        shutil.copy2(ROOT / 'docs/rgds-plus-preview.md', destination / 'README.md')
        shutil.copy2(ROOT / 'docs/rgds-plus-preview.md', theme / 'README.md')
        # Reuse the standard packager's Git-only source inventory in an isolated
        # index. No commits, identities, runtime libraries or build caches enter it.
        subprocess.run(['git', 'init', '--quiet', str(destination)], check=True)
        subprocess.run(['git', '-C', str(destination), 'add', '.'], check=True)
    print(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--release', action='store_true', help='Use the pinned Plus preview release metadata')
    args = parser.parse_args()
    prepare(args.destination.resolve(), args.release)
