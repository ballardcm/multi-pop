# Multi Pop

> **AI disclosure:** Multi Pop was developed with the help of AI, and its original system illustrations were AI-generated. Third-party components and their credits are listed in each system's README.

Multi Pop is a colorful dual-screen theme for ROCKNIX EmulationStation on handhelds with two displays. The upper screen shows a system's illustrated hardware, or a gameplay preview of the selected game; the lower screen keeps a three-cover carousel for browsing. Each system ships a patched EmulationStation frontend sized for its displays, an installer that backs up and restores your settings, and an optional updater that installs new releases in the background and rolls back if one fails to start.

## Systems

| System | Device and firmware | Source | Releases |
| --- | --- | --- | --- |
| Thor | AYN Thor, ROCKNIX 20261001 | [`systems/thor`](systems/thor/README.md) | [`thor-` releases](https://github.com/ballardcm/multi-pop/releases?q=thor-) |
| RG DS | Anbernic RG DS, ROCKNIX 20261001 | [`systems/rgds`](systems/rgds/README.md) | [`rgds-` releases](https://github.com/ballardcm/multi-pop/releases?q=rgds-) |
| RG DS Plus (preview) | Anbernic RG DS Plus, ROCKNIX 20261001 | [Plus install guide and testing limits](systems/rgds/docs/rgds-plus-preview.md) | [10.30.26.Preview](https://github.com/ballardcm/multi-pop/releases/tag/rgds-plus-10.30.26.Preview) |

Install from the newest release for your device, following its system README. Both systems publish to the same releases page, so download the installable ZIP and `SHA256SUMS` from a release whose tag names your device. GitHub's automatically generated Source code archives are not installable themes.

## Release tags

- `thor-MM.DD.YY.N` and `rgds-MM.DD.YY.N`, such as `thor-10.28.26.2`, are installable releases: month, day, two-digit year and that day's release revision. These are the only tags the updaters install, and they skip drafts and prereleases.
- `thor-frontend-*` and `rgds-frontend-*` are prereleases holding each system's verified frontend binary and source archives, which packaging downloads. They are not installable themes.
- `rgds-plus-MM.DD.YY.Preview` is a manually installed RG DS Plus prerelease. It is isolated from the existing devices' automatic updates; the Plus source is generated from the RG DS profile with its own pinned frontend inputs.
- `demo-media` is a prerelease holding the demo videos the READMEs link to.
- `legacy/thor/*` and `legacy/rgds/*` are the tags carried over from the old repositories, such as `legacy/thor/build-49a05568ed99` or `legacy/rgds/v0.3.2`. They mark history only; their releases were never copied here.

Releases are published by a maintainer running the system's workflow on `main`; merging a pull request never publishes anything. See [Thor release downloads](systems/thor/docs/releases.md) and [RG DS release maintenance](systems/rgds/docs/releases.md).

## Contributing

Pull requests are welcome for layouts, artwork, compatibility fixes, tools and documentation; for a larger change, open an issue first so we can agree on its scope. `main` changes only through pull requests, including the maintainer's. Each PR that touches a system runs that system's checks and attaches a preview download, so it can be tried on a device before merging. Thor contributors can start from [CONTRIBUTING.md](systems/thor/CONTRIBUTING.md).

The hardware illustrations, cards, heroes, logos, fonts and `platforms.json` are shared by both systems and must stay byte-identical in `systems/thor` and `systems/rgds`; `python3 tools/check-shared-assets.py` fails any PR that changes only one copy. A later change will move them into a single `shared/` source.

Original Multi Pop material is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), and contributions to it are accepted under the same terms. The patched frontend, launch scripts, fonts, logo artwork and other third-party components keep their own licenses, listed in each theme's `LICENSING.md`. Disclose AI assistance in your PR and in user-facing documentation where it applies. Keep ROMs, BIOS, downloaded game media, credentials and personal device settings out of the repository.

## Moved from the per-device repositories

Multi Pop was developed in two repositories, `ballardcm/multi-pop-thor` and `ballardcm/multi-pop-rgds`, until 10.28.26. Their full histories are imported here under `systems/thor` and `systems/rgds`. Their final release, 10.28.26.Transition, pointed installed updaters at this repository; both old repositories are deleted on 2026-11-27, and nothing is published from them any more.

For an existing Thor or original RG DS installation, run **two consecutive upgrades**, rebooting between them: the first installs the transition release and redirects the updater here; the second installs the current monorepo release. Alternatively, install fresh from this repository. Devices already on a monorepo release need no migration.

## Credits

[DekosAnjo](https://github.com/DekosAnjo) contributed the additional systems in [Multi Pop RG DS PR #9](https://github.com/ballardcm/multi-pop-rgds/pull/9), later ported to Thor: Channel F, Odyssey², Famicom Disk System, MSX2, Mega CD, Super Cassette Vision, Mega Duck, Nintendo 64DD, Pokémon Mini, Doom, TIC-80, WASM-4, and Watara Supervision. DekosAnjo reported generating their system illustrations with **Nano Banana 2**; the corresponding cards and hero panels derive from those illustrations. These contributions retain the project's CC BY-NC-SA 4.0 scope where applicable.

The logo artwork comes from HVR88's Monochrome Gaming Logos, the RetroPie Carbon theme and Fabrice Caruso's expanded Carbon collection, and remains the work of those artists and the brand owners. Each system README credits them in full, along with ROCKNIX EmulationStation and the other components Multi Pop builds on.

Multi Pop is by ballardcm.
