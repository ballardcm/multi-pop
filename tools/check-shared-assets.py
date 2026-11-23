#!/usr/bin/env python3
"""Fail unless every theme takes its artwork, logos, fonts and platform list from the one copy in shared/."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared"
THEMES = {
    "thor": ROOT / "systems/thor/multi-pop-thor",
    "rgds": ROOT / "systems/rgds/multi-pop-rgds",
    "odin2": ROOT / "systems/odin2/multi-pop-odin2",
}

# The hardware illustrations, cards, heroes, logos, fonts and platform list exist once, in shared/. Each theme reaches
# them through a relative link at the path its XML already uses, so a fix lands in every system at once and packaging
# copies the real files into each download. These are the linked paths, relative to a theme folder.
LINKED_FOLDERS = ["assets/systems", "assets/cards", "assets/heroes", "assets/logos", "assets/fonts"]
LINKED_FILES = ["platforms.json"]

# assets/ui mixes both kinds: these are drawn for each device's panel geometry and stay real files in each theme, while
# every other file in it is linked one by one. Palettes are per device too (RG DS tunes its selection accent) and are
# not shared at all.
# preview-panel.svg exists only in the Odin 2 theme, so it is per device by construction.
PER_DEVICE_UI = {"hardware-stage.svg", "selection.svg", "preview-panel.svg"}


def check(system, theme, problems):
    shared_ui = sorted(p.name for p in (SHARED / "assets/ui").iterdir() if p.name != ".DS_Store")
    expected = LINKED_FOLDERS + LINKED_FILES + ["assets/ui/" + name for name in shared_ui]
    for name in expected:
        path = theme / name
        if not path.is_symlink():
            problems.append(f"{system}: {name} must link into shared/, not be a copy")
            continue
        if path.resolve() != (SHARED / name).resolve():
            problems.append(f"{system}: {name} links to {path.readlink()}, not shared/{name}")
    for name in PER_DEVICE_UI:
        path = theme / "assets/ui" / name
        if path.is_symlink():
            problems.append(f"{system}: assets/ui/{name} is drawn per device and must be a real file")
        if (SHARED / "assets/ui" / name).exists():
            problems.append(f"shared/assets/ui/{name} is per device and belongs in each theme instead")
    # A file added beside the links, such as a new UI graphic, has to be either per device or moved into shared/.
    for path in sorted((theme / "assets/ui").iterdir()):
        if path.name not in PER_DEVICE_UI and path.name != ".DS_Store" and not path.is_symlink():
            problems.append(f"{system}: assets/ui/{path.name} is neither linked to shared/ nor listed as per device")


def main():
    problems = []
    for system, theme in THEMES.items():
        check(system, theme, problems)
    if problems:
        print("FAIL: themes must take their shared assets from shared/", file=sys.stderr)
        for problem in problems:
            print("  " + problem, file=sys.stderr)
        print("Move the file into shared/ and link it from each theme, or add an intentionally per-device UI file to "
              "PER_DEVICE_UI.", file=sys.stderr)
        return 1
    count = sum(1 for p in SHARED.rglob("*") if p.is_file() and p.name != ".DS_Store")
    print(f"PASS: {count} shared files in shared/, linked from " + ", ".join(THEMES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
