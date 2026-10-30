# Repository instructions

These apply to the whole monorepo. `systems/thor/AGENTS.md` and `systems/rgds/AGENTS.md` add each system's own checks and device rules.

## Changes and merging

Contributions arrive through pull requests so their checks and preview downloads can be reviewed before release. Never commit or push directly to `main`; GitHub protects it for maintainers too. Do not merge until the user authorizes merging. Releases are published only by a manual workflow run on `main` after the PR merges, never from a working branch.

Each system's workflow (`.github/workflows/thor.yml`, `.github/workflows/rgds.yml`) runs on PRs that touch that system, and both run `tools/check-shared-assets.py`. Run the same checks locally from the system's directory before opening a PR; `CLAUDE.md` lists them.

Never publish a release from the old `ballardcm/multi-pop-thor` or `ballardcm/multi-pop-rgds` repositories. Devices that have not yet installed 10.28.26.Transition still poll them, and would install anything published there. Every new release comes from this repository, tagged `thor-MM.DD.YY.N` or `rgds-MM.DD.YY.N` with a version integer above 20261028001.

The RG DS Plus preview is an explicit exception: `rgds-plus-MM.DD.YY.Preview`,
marked as a prerelease and never Latest, with the same monotonic integer rule.
It is published only by the manual `rgds-plus.yml` workflow on main. Its pinned
`rgds-frontend-plus-*` input prerelease may be staged as a draft for PR checks;
only the manual main workflow publishes it. Existing device updaters must never
consume Plus previews.

## Identity and attribution

The repository owner's personal email must stay out of public commit metadata. Use `3799765+ballardcm@users.noreply.github.com` for local commits and pass `--author-email 3799765+ballardcm@users.noreply.github.com` when merging with `gh pr merge`, because GitHub's merge API can otherwise use the account email. Verify the resulting merge commit's author email before publishing a release or changing repository visibility.

Use `ballardcm` for repository-owner attribution and new commit author names. Keep the owner's personal name out of public documentation and new commit metadata; preserve third-party contributor credits, including DekosAnjo's for the systems added in RG DS PR #9.

## Licensing and content

Keep original material under the documented CC BY-NC-SA 4.0 scope and preserve upstream attribution and third-party license exceptions. Disclose AI assistance in user-facing documentation.

Keep credentials, ROMs, BIOS, downloaded game media, device settings and state, firmware and runtime libraries, and compiler caches out of Git and out of release source inventories. RG DS's `.local/` and Thor's `native-build/` are private local storage.

## Shared assets

The hardware illustrations, cards, heroes, logos, fonts and `platforms.json` must stay byte-identical between `systems/thor` and `systems/rgds` until they move into `shared/`. Change them in one system, copy the bytes to the other, and run `python3 tools/check-shared-assets.py`. Only the files in its `PER_DEVICE` list may differ.

## Releases and the updater

A changed frontend patch or compiler input needs a newly built and validated frontend, registered as a new `thor-frontend-` or `rgds-frontend-` prerelease, rather than reusing the old binary. The installed updaters refuse a release that changes the firmware revision in `frontend/compatibility.json` or, on RG DS, the startup helpers `start_es_rgds.sh`, `start_after_reboot.sh` and `multi_pop_rgds_common.sh`; such changes need a reinstall and must be planned as one. See each system's `docs/releases.md`.
