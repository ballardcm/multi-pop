#!/usr/bin/env python3
"""Fetch hash-pinned Plus inputs and package the generated preview source tree."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    root, inputs, output = (p.resolve() for p in (args.source, args.inputs, args.output))
    config = json.loads((root / 'frontend-build/release.json').read_text())
    inputs.mkdir(parents=True, exist_ok=True)
    keys = ('frontend', 'upstream_source', 'sdl_source', 'pugixml_source')
    if args.fetch:
        command = ['gh', 'release', 'download', config['release_tag'], '--repo', config['release_repo'],
                   '--dir', str(inputs), '--skip-existing']
        for key in keys:
            command.extend(['--pattern', config[key]['asset']])
        subprocess.run(command, check=True)
    for key in keys:
        if digest(inputs / config[key]['asset']) != config[key]['sha256']:
            raise ValueError('Plus release input checksum mismatch: ' + key)
    command = [sys.executable, str(root / 'tools/package-release.py'), '--output', str(output)]
    for flag, key in (('--frontend', 'frontend'), ('--upstream-source', 'upstream_source'), ('--sdl-source', 'sdl_source')):
        command.extend([flag, str(inputs / config[key]['asset'])])
    subprocess.run(command, cwd=root, check=True)
    # The installed theme retains its existing path; device-specific download
    # names prevent confusion with the original RG DS package.
    archives = []
    for name in ('multi-pop-rgds-rocknix-' + config['firmware_version'] + '.zip', 'multi-pop-rgds-source.zip'):
        source = output / name
        target = output / name.replace('multi-pop-rgds-', 'multi-pop-rgds-plus-', 1)
        source.replace(target)
        archives.append(target)
    (output / 'SHA256SUMS').write_text(''.join(digest(p) + '  ' + p.name + '\n' for p in archives))


if __name__ == '__main__':
    main()
