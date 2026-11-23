#!/usr/bin/env python3
"""Package the Odin 2 theme and its sources for a Multi Pop release."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import zipfile
from release_version import read_release

ROOT = Path(__file__).resolve().parents[1]
THEME = "multi-pop-odin2"
# Single Pop runs on the Odin 2's stock frontend, so unlike Thor and RG DS there is no binary or upstream source
# archive to verify; the download is the theme folder alone.
REQUIRED = {"theme.xml", "README.md", "LICENSE", "LICENSING.md", "version.xml"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_files(root):
    # Git's inventory excludes local media, device settings and anything else left untracked.
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
    )
    names = sorted(set(name.decode() for name in output.split(b"\0") if name))
    # The artwork, logos, fonts and platform list live once in the repository's shared/ folder, and each theme links to
    # them. A link is followed only into that folder, and only to files Git tracks there, so a stray link can never pull
    # an outside or untracked file into a download. The packages hold real files; devices never see a link.
    shared = (root.parents[1] / "shared").resolve()
    tracked = []
    if shared.is_dir():
        listed = subprocess.check_output(["git", "ls-files", "--cached", "-z"], cwd=shared)
        tracked = sorted(entry.decode() for entry in listed.split(b"\0") if entry)
    files = {}
    for name in names:
        path = root / name
        if path.is_symlink():
            target = path.resolve()
            if not target.is_relative_to(shared):
                raise ValueError("Release sources may link only into the shared folder: " + name)
            within = target.relative_to(shared).as_posix()
            if within in tracked:
                files[name] = target
                continue
            inside = [item for item in tracked if item.startswith(within + "/")]
            if not inside:
                raise ValueError("Release sources may link only to files Git tracks in the shared folder: " + name)
            for item in inside:
                files[name + item[len(within):]] = shared / item
        elif path.is_file():
            files[name] = path
    return files


def release_version(root):
    dated = read_release(root)
    if dated:
        return dated[0]
    return int(subprocess.check_output(["git", "rev-list", "--count", "--first-parent", "HEAD"], cwd=root))


def add_file(archive, name, data, executable=False):
    # Fixed metadata makes the same files produce the same download regardless of checkout times.
    entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.create_system = 3
    entry.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    entry.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(entry, data)


def package(root, output, version):
    if not isinstance(version, int) or version < 1:
        raise ValueError("Release version must be a positive integer")
    files = repository_files(root)
    theme_files = {name[len(THEME) + 1:]: path.read_bytes() for name, path in files.items()
                   if name.startswith(THEME + "/")}
    if not REQUIRED.issubset(theme_files):
        raise ValueError("Installable theme is missing required files")
    # version.json is what a future updater will compare, so every release carries it from the first one on.
    dated = read_release(root)
    if dated and version != dated[0]:
        raise ValueError("Package version must match the configured date release")
    display = dated[1] if dated else str(version)
    version_data = {"version": version}
    if dated:
        version_data["display_version"] = display
    theme_files["version.json"] = (json.dumps(version_data) + "\n").encode()
    # Show the human-readable date label, never the ordering sequence.
    theme_files["version.xml"] = re.sub(rb"<multiPopVersion>[^<]*</multiPopVersion>",
                                        ("<multiPopVersion>" + display + "</multiPopVersion>").encode(),
                                        theme_files["version.xml"])
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(theme_files.items())}
    output.mkdir(parents=True, exist_ok=True)
    # The same "-rocknix-theme.zip" shape as the other devices keeps the release workflow's checks uniform.
    ready = output / (THEME + "-rocknix-theme.zip")
    source = output / (THEME + "-source.zip")
    with zipfile.ZipFile(ready, "w") as archive:
        for name, data in sorted(theme_files.items()):
            add_file(archive, THEME + "/" + name, data, name.endswith(".sh"))
        add_file(archive, "install-manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    with zipfile.ZipFile(source, "w") as archive:
        for name, path in files.items():
            add_file(archive, THEME + "-source/" + name, path.read_bytes(), name.endswith(".sh"))
    sums = output / "SHA256SUMS"
    sums.write_text("".join(sha256(path) + "  " + path.name + "\n" for path in (ready, source)))
    return ready, source, sums


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--version", type=int, help="internal ordering value; defaults to the configured date release")
    args = parser.parse_args()
    version = args.version if args.version is not None else release_version(ROOT)
    for path in package(ROOT, args.output, version):
        print(path)


if __name__ == "__main__":
    main()
