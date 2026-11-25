# Multi Pop

> **AI disclosure:** Multi Pop was developed with the help of AI, and its original system illustrations were AI-generated. Third-party components and their credits are listed in each system's README.

Multi Pop is a colorful theme for ROCKNIX EmulationStation, built for handhelds with two displays. The upper screen shows a system's illustrated hardware, or a gameplay preview of the selected game; the lower screen keeps a three-cover carousel for browsing. Each dual-screen system ships a patched EmulationStation frontend sized for its displays, an installer that backs up and restores your settings, and an optional updater that installs new releases in the background and rolls back if one fails to start.

The AYN Odin 2 edition, which calls itself **Single Pop** on screen and is currently a preview, puts the same artwork on one display. The hardware sits on a stage you swipe between, and each library pairs a cover carousel with the preview. It runs on the Odin 2's stock frontend; its only device change is a boot fix for the Odin 2 touchscreen.

## Systems

| System | Device and firmware | Source | Releases |
| --- | --- | --- | --- |
| Thor | AYN Thor, ROCKNIX 20261001 or 20261101 | [`systems/thor`](systems/thor/README.md) | [`thor-` releases](https://github.com/ballardcm/multi-pop/releases?q=thor-) |
| RG DS | Anbernic RG DS, ROCKNIX 20261001 or 20261101 | [`systems/rgds`](systems/rgds/README.md) | [`rgds-` releases](https://github.com/ballardcm/multi-pop/releases?q=rgds-) |
| RG DS Plus | Anbernic RG DS Plus, ROCKNIX 20261001 or 20261101 | [Plus install guide and testing limits](systems/rgds/docs/rgds-plus.md) | [`rgds-plus-` releases](https://github.com/ballardcm/multi-pop/releases?q=rgds-plus-) |
| Odin 2 (Single Pop), preview | AYN Odin 2 on ROCKNIX 20261101, stock EmulationStation; not tested on the Odin 2 Portal | [`systems/odin2`](systems/odin2/README.md) | [`odin2-` releases](https://github.com/ballardcm/multi-pop/releases?q=odin2-) |

The bundled frontends were built for ROCKNIX 20261001 and also run on 20261101. Installing and removing work on 20261101 from Thor 11.14.26.1 and from RG DS and RG DS Plus 11.15.26.1; earlier RG DS and Plus releases refuse both there, so update before removing one. The full control checklist has not been repeated on 20261101 for any device.

Install from the newest release for your device, following its system README. Every device publishes to the same releases page, so download the installable ZIP and `SHA256SUMS` from a release whose tag names your device. GitHub's automatically generated Source code archives are not installable themes.

## Release tags

- `thor-MM.DD.YY.N`, `rgds-MM.DD.YY.N`, `rgds-plus-MM.DD.YY.N` and `odin2-MM.DD.YY.N`, such as `thor-11.14.26.1`, are installable releases: month, day, two-digit year and that day's release revision. These are the only tags the updaters install, each device only its own, and they skip drafts and prereleases. The Odin 2 edition has no updater yet.
- `odin2-11.22.26.Preview` is the Odin 2's first release, a prerelease published while the edition is in preview. Only the Odin 2 may publish a worded `Preview` label, because it has no updater to confuse.
- `thor-frontend-*` and `rgds-frontend-*` are prereleases holding each system's verified frontend binary and source archives, which packaging downloads. They are not installable themes.
- `rgds-plus-10.30.26.Preview` is the earlier RG DS Plus prerelease, installed by hand; its updater follows no published tag. The Plus source is generated from the RG DS profile with its own pinned frontend inputs, held in `rgds-frontend-plus-*` prereleases.
- `downloads` has no files. It is the release GitHub shows as Latest, and it points to each device's releases, so that link never leads to another device's download. The release workflows keep it marked; its text is `.github/downloads-release.md`.
- `demo-media` is a prerelease holding the demo videos the READMEs link to.
- `legacy/thor/*` and `legacy/rgds/*` are the tags carried over from the old repositories, such as `legacy/thor/build-49a05568ed99` or `legacy/rgds/v0.3.2`. They mark history only; their releases were never copied here.

Releases are published by a maintainer running the system's workflow on `main`; merging a pull request never publishes anything. See [Thor release downloads](systems/thor/docs/releases.md), [RG DS release maintenance](systems/rgds/docs/releases.md) and [Odin 2 releases](systems/odin2/docs/releases.md).

## Contributing

Pull requests are welcome for layouts, artwork, compatibility fixes, tools and documentation; for a larger change, open an issue first so we can agree on its scope. `main` changes only through pull requests, including the maintainer's. PRs that change a system's code or assets run that system's checks; documentation-only changes skip device workflows. Downloadable device previews are requested explicitly and expire after three days. Thor contributors can start from [CONTRIBUTING.md](systems/thor/CONTRIBUTING.md).

To request a preview, open the device workflow under Actions, choose **Run workflow**, select the PR branch, and enable **preview**. With the CLI, for example:

```sh
gh workflow run thor.yml --repo ballardcm/multi-pop --ref YOUR_BRANCH -f preview=true
```

Use `rgds.yml`, `rgds-plus.yml` or `odin2.yml` for the other devices. The artifact contains the self-contained installable ZIP and a `SHA256SUMS` covering that ZIP. Full source ZIPs are retained in published releases; frontend sources and build descriptors remain available in the pinned frontend prereleases and repository. A manual run on `main` with **preview** left disabled publishes a release. A preview run, including on `main`, never publishes.

The hardware illustrations, cards, heroes, logos, fonts and `platforms.json` live once, in `shared/`, and each theme reaches them through relative symlinks at the paths its XML uses. A change there reaches every system, and packaging puts the real files into each download. `python3 tools/check-shared-assets.py` fails a PR that replaces a link with a copy. On Windows, clone with symlinks enabled (`git config --global core.symlinks true` with Developer Mode on), or the links check out as small text files.

Original Multi Pop material is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), and contributions to it are accepted under the same terms. The patched frontend, launch scripts, fonts, logo artwork and other third-party components keep their own licenses, listed in each theme's `LICENSING.md`. Disclose AI assistance in your PR and in user-facing documentation where it applies. Keep ROMs, BIOS, downloaded game media, credentials and personal device settings out of the repository.

## Moved from the per-device repositories

Multi Pop was developed in two repositories, `ballardcm/multi-pop-thor` and `ballardcm/multi-pop-rgds`, until 10.28.26. Their full histories are imported here under `systems/thor` and `systems/rgds`. Their final release, 10.28.26.Transition, pointed installed updaters at this repository; both old repositories are scheduled for deletion on 2026-11-27, and nothing is published from them any more.

For an existing Thor or original RG DS installation, run **two consecutive upgrades**, rebooting between them: the first installs the transition release and redirects the updater here; the second installs the current monorepo release. Alternatively, install fresh from this repository; after 2026-11-27 the transition release is gone with the old repositories, so a fresh install is the only route. Devices already on a monorepo release need no migration.

## Credits

[DekosAnjo](https://github.com/DekosAnjo) contributed the additional systems in Multi Pop RG DS PR #9, [recorded here](systems/rgds/docs/pr9-systems.md) and later ported to Thor: Channel F, Odyssey², Famicom Disk System, MSX2, Mega CD, Super Cassette Vision, Mega Duck, Nintendo 64DD, Pokémon Mini, Doom, TIC-80, WASM-4, and Watara Supervision. DekosAnjo reported generating their system illustrations with **Nano Banana 2**; the corresponding cards and hero panels derive from those illustrations. These contributions retain the project's CC BY-NC-SA 4.0 scope where applicable.

The logo artwork comes from HVR88's Monochrome Gaming Logos, the RetroPie Carbon theme and Fabrice Caruso's expanded Carbon collection, and remains the work of those artists and the brand owners. Each system README credits them in full, along with ROCKNIX EmulationStation and the other components Multi Pop builds on.

Multi Pop is by ballardcm.
