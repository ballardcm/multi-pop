# Multi Pop monorepo map

Rules for changes, identity, licensing and releases are in `AGENTS.md`; read it before committing. This file is the map: where things are, what to run, and which files are big enough to read by section.

## Layout

- `systems/thor/` and `systems/rgds/` are the two themes, each the old per-device repository's tree unchanged in shape: the installable theme (`multi-pop-thor/`, `multi-pop-rgds/`), `tools/`, `docs/`, `frontend-build/` and `release-version.json`. Every tool finds its project root from its own path, so run them from the system's directory.
- `.github/workflows/_system-release.yml` is the one release pipeline; `thor.yml` and `rgds.yml` call it with the system name. GitHub ignores workflow files below the root, so none belong under `systems/`.
- `tools/check-shared-assets.py` checks that the shared artwork, logos, fonts and `platforms.json` are byte-identical in both systems. A later change will move them into `shared/`.
- `README.md` is the public front page; each system README carries its install, update and credit details.

## Checks

From `systems/thor`:

```sh
python3 tools/check-multi-pop.py
python3 tools/test-install-multi-pop-media.py
python3 tools/test-package-release.py
python3 tools/test-release-version.py
python3 tools/test-thor-touch.py
python3 tools/test-thor-startup.py
python3 tools/test-auto-update.py
```

From `systems/rgds`:

```sh
python3 tools/check-rgds.py
python3 tools/test-auto-update.py
python3 tools/test-package-release.py
python3 tools/test-release-version.py
python3 tools/test-popup-bounds.py
```

From the root: `python3 tools/check-shared-assets.py`. `check-multi-pop.py` and `check-rgds.py` already run `tools/check-logo-assets.py` with the theme path; run alone, it needs that path as its argument.

The RG DS Plus preview is generated from `systems/rgds` by
`tools/prepare-plus-prototype.py DESTINATION --release`. It has separate pinned
inputs in `frontend-build/plus-release.json`, compatibility data and
`release-version-plus.json`. Run the generated tree's `check-rgds.py` and
`test-popup-bounds.py`, plus the source tree's `test-plus-profile.py DESTINATION`.
`rgds-plus.yml` packages PR previews and publishes only when manually run on main.
Input binaries can be staged as a draft frontend prerelease for PR checks; the
manual main workflow publishes that draft and the installable Plus prerelease.

## Big files

Read these by section (`grep -n` for the symbol, then `sed -n`):

- `systems/thor/multi-pop-thor/scripts/auto_update.py` 435, `systems/rgds/multi-pop-rgds/scripts/auto_update.py` 437: the on-device updaters; release selection is in `thor_release` / `latest_release`.
- `systems/thor/tools/test-auto-update.py` 373, `systems/rgds/tools/test-auto-update.py` 349.
- `systems/thor/tools/install-multi-pop-media.py` 481, `systems/thor/tools/fetch-multi-pop-screenshots.py` 444.
- `systems/thor/tools/install-multi-pop-theme.py` 321, `systems/rgds/tools/install-multi-pop-theme.py` 321: shipped on devices as `scripts/update_theme.py`.
- `systems/thor/tools/build-multi-pop-art.py` 238, `systems/rgds/tools/build-multi-pop-art.py` 256: the `SYSTEMS` table near the top is the platform list.
- `systems/thor/multi-pop-thor/frontend/thor-popup-placement.patch` 546, `systems/rgds/multi-pop-rgds/frontend/rgds-popup-placement.patch` 546: hashed in `frontend-build/release.json`; any edit needs a new verified frontend.
- `systems/thor/multi-pop-thor/assets/logos/catalog.json` 722, `systems/thor/multi-pop-thor/platforms.json` 488, identical in RG DS.
- `systems/thor/README.md` 265, `systems/rgds/README.md` 191, `systems/rgds/docs/releases.md` 116.
- `.github/workflows/_system-release.yml` 167.
- `systems/thor/multi-pop-thor/frontend/licenses/Embedded-source-notices.txt` 3562, `systems/rgds/multi-pop-rgds/frontend/licenses/Embedded-source-notices.txt` 3562: third-party license text; never read it end to end.

## Noisy or slow commands

- `test-auto-update.py` and `test-install-multi-pop-media.py` print every test name and some ResourceWarnings; send them to a file under `$HOME` and grep for `FAIL|Error`.
- `tools/build-multi-pop-art.py` rewrites every card and hero PNG (162 files per system) and Thor's `docs/artwork-grid.png`. Run it in one system only and copy `assets/cards` and `assets/heroes` to the other. Pillow versions render text slightly differently, so a rebuild changes bytes even where nothing was meant to change.
- `tools/package-release.py` writes about 280 MB to `dist/` and needs the verified frontend inputs, which `gh release download` fetches from the `thor-frontend-` or `rgds-frontend-` prerelease.
- `tools/fetch-multi-pop-screenshots.py` and `tools/build-multi-pop-logos.py --fetch` use the network.

## History

`legacy/thor/*` and `legacy/rgds/*` tags are the old repositories' tags. `systems/*/docs/prototype-status.md`, `pr9-systems.md` and the artwork JSON in `systems/thor/docs/` are historical records, not current instructions.
