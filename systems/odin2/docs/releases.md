# Odin 2 releases

Odin 2 releases are tagged `odin2-MM.DD.YY.N`. The number comes from `release-version.json`: set `date` to the release day and `revision` to 1, or to one more than the last release published that day. Make that change in the pull request that prepares the release, and put that release's notes in `docs/release-notes.md` if it has any.

While the edition is in preview, `release-version.json` may also carry `"label": "Preview"`. The release is then tagged `odin2-MM.DD.YY.Preview`, shows that label on the device, and the workflow publishes it as a prerelease. The label replaces only the displayed revision, so ordering still follows date and revision. Only the Odin 2 may do this, because it has no updater; drop the label for a normal release.

Merging never publishes. After the PR is merged, a maintainer runs the `Odin 2` workflow on `main`. It runs the checks, packages `dist/` and creates the release, then marks the file-less `downloads` release as Latest again so that no device's release takes that mark.

The release holds three files:

- `multi-pop-odin2-rocknix-theme.zip`: the installable `multi-pop-odin2` folder, with `version.json` and an `install-manifest.json` of SHA-256 digests.
- `multi-pop-odin2-source.zip`: every tracked source file for the system.
- `SHA256SUMS`.

There is no frontend binary and no updater. The theme ships three scripts in `scripts/`: `install_single_pop.sh` and `remove_single_pop.sh`, which add and remove the touchscreen boot service, and `odin2_touch.sh`, which that service runs. Packaging marks them executable, and `tools/test-odin2-scripts.py` runs all three against a fake device. `version.json` already carries the same ordering integer as the other devices (`YYYYMMDD` × 1000 + revision), so an updater added later can compare against releases from the very first one. Thor and RG DS updaters match only their own tag prefixes and archive names, so they ignore `odin2-` releases.
