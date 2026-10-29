#!/usr/bin/env python3
"""Fail when the artwork, logos, fonts or platform list differ between the Thor and RG DS themes."""

from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    "thor": ROOT / "systems/thor/multi-pop-thor",
    "rgds": ROOT / "systems/rgds/multi-pop-rgds",
}

# Both themes ship the same hardware illustrations, cards, heroes, logos, fonts and platform list. They are still
# copies until a later change moves them into a single shared/ source, so a fix made in one system has to be copied
# to the other; this check is what makes a forgotten copy fail a pull request instead of reaching one device only.
SHARED = [
    "assets/systems",
    "assets/cards",
    "assets/heroes",
    "assets/logos",
    "assets/fonts",
    "assets/ui",
    "palettes",
    "platforms.json",
]

# These differ on purpose. The UI stage and selection outline are drawn for each device's panel geometry, and RG DS
# palettes carry a selection accent tuned for its smaller screen. A directory entry covers everything inside it.
PER_DEVICE = {
    "assets/ui/hardware-stage.svg",
    "assets/ui/selection.svg",
    "palettes",
}


def per_device(name):
    return any(name == entry or name.startswith(entry + "/") for entry in PER_DEVICE)


def inventory(theme):
    files = {}
    for entry in SHARED:
        path = theme / entry
        candidates = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
        for file in candidates:
            # Finder and Python leave these behind locally; they are never part of either theme.
            if file.name == ".DS_Store" or "__pycache__" in file.parts:
                continue
            name = file.relative_to(theme).as_posix()
            if not per_device(name):
                files[name] = hashlib.sha256(file.read_bytes()).hexdigest()
    return files


def main():
    found = {system: inventory(theme) for system, theme in THEMES.items()}
    thor, rgds = found["thor"], found["rgds"]
    problems = []
    for name in sorted(set(thor) | set(rgds)):
        if name not in rgds:
            problems.append("only in thor: " + name)
        elif name not in thor:
            problems.append("only in rgds: " + name)
        elif thor[name] != rgds[name]:
            problems.append("differs: " + name)
    if problems:
        print("FAIL: shared assets must be byte-identical in systems/thor and systems/rgds", file=sys.stderr)
        for problem in problems:
            print("  " + problem, file=sys.stderr)
        print("Copy the changed files to the other system, or add an intentionally per-device file to PER_DEVICE.",
              file=sys.stderr)
        return 1
    print(f"PASS: {len(thor)} shared asset files are identical in Thor and RG DS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
