# Repository instructions

These apply to the whole monorepo. `systems/thor/AGENTS.md` and `systems/rgds/AGENTS.md` add each system's own checks and device rules.

## Changes and merging

Contributions arrive through pull requests so their checks and any requested preview downloads can be reviewed before release. Never commit or push directly to `main`; GitHub protects it for maintainers too. Do not merge until the user authorizes merging. Releases are published only by a manual workflow run on `main` after the PR merges, never from a working branch.

Each system's workflow (`.github/workflows/thor.yml`, `.github/workflows/rgds.yml`, `.github/workflows/odin2.yml`, `.github/workflows/rgds-plus.yml`) runs checks on PRs that touch that system's code or assets, and each runs `tools/check-shared-assets.py`. Run the same checks locally from the system's directory before opening a PR; `CLAUDE.md` lists them.

GitHub always marks one full release as Latest, so the file-less `downloads` release holds that mark and links to every device's releases; no device release may take it, and the release workflows mark `downloads` again after each publish.

Never publish a release from the old `ballardcm/multi-pop-thor` or `ballardcm/multi-pop-rgds` repositories. Devices that have not yet installed 10.28.26.Transition still poll them, and would install anything published there. Every new release comes from this repository, tagged `thor-MM.DD.YY.N`, `rgds-MM.DD.YY.N` or `odin2-MM.DD.YY.N` with a version integer above 20261028001.

The Odin 2 theme (`systems/odin2`, shown on screen as Single Pop) runs on ROCKNIX's stock frontend. It ships no frontend binary or updater, and its checker rejects an Automatic updates setting until an updater exists. Its one device change is `single-pop-touch.service`, installed and removed by the theme's own scripts. The service re-binds the Odin 2 touch controller that ROCKNIX 20261101 probes before the panel is powered. Thor and RG DS updaters must keep ignoring `odin2-` tags and `multi-pop-odin2-` archives. While the Odin 2 has no updater, it alone may publish `odin2-MM.DD.YY.Preview` (a `label` of `Preview` in its `release-version.json`), which the release workflow marks as a prerelease. Give it a numbered revision again before an updater ships.

RG DS Plus releases are tagged `rgds-plus-MM.DD.YY.N`, with the same monotonic
integer rule, and are published only by the manual `rgds-plus.yml` workflow on
main: not a prerelease, and never Latest. Only a Plus updater may consume them;
Thor and original RG DS updaters must keep rejecting the tag and the
`multi-pop-rgds-plus-rocknix-` archive. The pinned `rgds-frontend-plus-*` input
prerelease may be staged as a draft for PR checks; only the manual main workflow
publishes it. `rgds-plus-10.30.26.Preview` was the one prerelease under the
earlier scheme, and its updater follows no published tag.

## Identity and attribution

The repository owner's personal email must stay out of public commit metadata. Use `3799765+ballardcm@users.noreply.github.com` for local commits and pass `--author-email 3799765+ballardcm@users.noreply.github.com` when merging with `gh pr merge`, because GitHub's merge API can otherwise use the account email. Verify the resulting merge commit's author email before publishing a release or changing repository visibility.

Use `ballardcm` for repository-owner attribution and new commit author names. Keep the owner's personal name out of public documentation and new commit metadata; preserve third-party contributor credits, including DekosAnjo's for the systems added in RG DS PR #9.

## Licensing and content

Keep original material under the documented CC BY-NC-SA 4.0 scope and preserve upstream attribution and third-party license exceptions. Disclose AI assistance in user-facing documentation.

Keep credentials, ROMs, BIOS, downloaded game media, device settings and state, firmware and runtime libraries, and compiler caches out of Git and out of release source inventories. RG DS's `.local/` and Thor's `native-build/` are private local storage.

## Shared assets

The hardware illustrations, cards, heroes, logos, fonts, `platforms.json` and the shared UI graphics live once, in `shared/`. Each theme links to them with relative symlinks at the paths its XML uses; change the file in `shared/`, never replace a link with a copy, and run `python3 tools/check-shared-assets.py`. Only `hardware-stage.svg`, `selection.svg` and Odin 2's `preview-panel.svg` in `assets/ui`, and the palettes, are per device. Packaging follows links only into files Git tracks in `shared/`, and downloads always contain real files.

## GitHub artifact storage

PRs run checks without uploading downloads; documentation-only changes skip device workflows. Request a preview by manually running the device workflow on the branch with `preview=true`. Previews contain only the installable ZIP and its checksum and expire after three days. Manual runs on `main` with the default `preview=false` publish full releases directly from the packaging job. Plus draft inputs stay isolated and their temporary artifact is deleted after use, with one-day expiry as a fallback. Cancel superseded PR runs, never active release runs.

Keep Actions artifact and cache usage optimized. Before adding uploads, inspect existing workflow outputs for overlap, especially shared artwork repeated across device packages, nested archives and intermediate bundles. Upload only what downstream jobs or reviewers need, reuse an existing artifact within a run where practical, and set the shortest useful explicit retention. Keep installable release downloads self-contained with real files; reduce CI duplication without breaking that contract. Periodically review storage and remove obsolete artifacts from superseded runs and closed PRs, preserving useful current PR previews and artifacts still needed by active runs. Treat published release assets and pinned frontend inputs separately: do not delete them as routine CI cleanup.

## Releases and the updater

A changed frontend patch or compiler input needs a newly built and validated frontend, registered as a new `thor-frontend-` or `rgds-frontend-` prerelease, rather than reusing the old binary. The installed updaters refuse a release that changes the firmware revision in `frontend/compatibility.json`, the launcher `start_es_thor.sh` on Thor or, on RG DS, the startup helpers `start_es_rgds.sh`, `start_after_reboot.sh` and `multi_pop_rgds_common.sh`; such changes need a reinstall and must be planned as one. See each system's `docs/releases.md`.
