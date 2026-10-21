# Release maintenance and update testing

A release has an installable `multi-pop-rgds-rocknix-20261001.zip`, a matching `multi-pop-rgds-source.zip`, and `SHA256SUMS`. The source download contains the tracked project files, pinned upstream frontend sources, SDL headers source, and pugixml source. Firmware libraries, credentials, user data and compiler caches are excluded. Install manifests hash every shipped theme file. The packager rejects unverified binaries, changed build inputs, substituted source archives, symlinks and embedded service-key literals.

## Build and package

Follow `frontend-build/README.md`. Register the validated binary hash, source/firmware revisions, and exact compiled input hashes in `frontend-build/release.json` and `multi-pop-rgds/frontend/compatibility.json`. Any frontend patch or compiler change requires rebuilding and testing a new binary. Theme-only updates may reuse that binary.

Update `multi-pop-rgds/version.json` with a strictly increasing integer `version` and semantic `display_version`; keep `version.xml` consistent. For example, 300 / 0.3.0 followed by 301 / 0.3.1. A source-only change still needs its own release number if published. The updater accepts `vMAJOR.MINOR.PATCH` tags. No downgrade installs automatically.

Stage all intended source changes in Git, run the checks, and package:

```sh
python3 tools/check-rgds.py
python3 tools/test-auto-update.py
python3 tools/test-package-release.py
python3 tools/package-release.py \
  --frontend multi-pop-rgds/frontend/emulationstation \
  --upstream-source /path/to/emulationstation-source.tar.gz \
  --sdl-source /path/to/SDL2-source.tar.gz \
  --output .local/release
```

The matching `pugixml-source.tar.gz` must be next to the upstream archive. All three archives are pinned in `frontend-build/release.json`. The packager inventories Git-tracked files, not ignored local storage. Make the final release from the reviewed merge commit on the default branch. Verify noreply commit metadata and retain the corresponding source download with every binary.

## Public automatic updates

An Internet-connected device checks GitHub directly. Checks run after frontend startup when Automatic updates is On, at most every six hours. A manual Check for updates bypasses that interval and the Off setting. Downloads are validated, staged and applied only on the next frontend start. A started update is confirmed only when the installed theme frontend is the process serving the local API and its binary hash matches. After repeated unconfirmed starts, the old theme is restored. One backup is retained.

Do not change activation scripts via an automatic update. Such releases need explicit removal/reinstallation because the on-device startup override and backup records also need updating. This restriction is checked during apply. The updater runs under a process lock, preserves settings, and never restarts gameplay to apply an update.

## Private releases or USB-only devices

Before public launch, GitHub requires authentication. For local testing, use the Mac's authenticated GitHub CLI through a loopback-only relay; no token is copied to the handheld. The same relay is useful when a handheld has USB networking but no Internet.

On the computer with this source checkout and `gh auth login` completed:

```sh
python3 tools/release-relay.py
```

In another computer terminal, keep this SSH tunnel running (replace the destination):

```sh
ssh -N -R 127.0.0.1:18765:127.0.0.1:18765 root@RK3566.local
```

On the RG DS:

```sh
mkdir -p /storage/.config/multi-pop-rgds
printf '%s\n' '{"release_api":"http://127.0.0.1:18765/release"}' \
  > /storage/.config/multi-pop-rgds/update-source.json
```

The relay serves only this repository's latest release and its approved install assets. Keep both the computer relay and SSH tunnel alive during checks/downloads. For the normal public Internet path, delete the override:

```sh
rm -f /storage/.config/multi-pop-rgds/update-source.json
```

A missing relay or failed network check leaves the installed version running. It does not establish Internet sharing for games or scrapers.

## End-to-end acceptance

Install release A using the README, with automatic updates enabled. Publish a newer release B containing identical activation helpers. Start the frontend normally (after the six-hour interval, or clear the local `update/last-check` marker in a controlled test), observe B staged, then restart the frontend. Confirm its displayed version, `update/installed.json`, every release-manifest hash, active service, correct executable and 1920×480 canvas, both powered panels, unchanged game data/settings, and no pending update. Test corrupted archives and rollback separately with the automated suite.

## Manual rollback

Turn automatic updates Off first. Download the desired release's installable ZIP and SHA256SUMS, verify it on your computer, and copy it to `/storage/downloads/` on the RG DS. While the frontend is idle, run:

```sh
python3 /roms/themes/multi-pop-rgds/scripts/update_theme.py \
  /storage/downloads/multi-pop-rgds-rocknix-20261001.zip EXPECTED_SHA256
```

This checks the archive and activation records, keeps a backup, and restarts only an idle frontend. If it refuses a changed startup helper or firmware mismatch, use the full remove/install procedure instead. Do not remove the running theme folder manually.
