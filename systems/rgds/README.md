# Multi Pop for Anbernic RG DS

A work-in-progress adaptation of [Multi Pop by Chris (ballardcm)](https://github.com/ballardcm/multi-pop-thor) for **Anbernic RG DS running ROCKNIX 20261001**. Private during prototyping; intended for public sharing after hardware testing and a source/license review.

The two 640×480 displays show system artwork or a game preview above and a three-card library below. A patched EmulationStation frontend keeps dialogs on the upper display and supports shoulder-button paging and touch gestures. This is a prototype, not a claim of complete device compatibility.

## Install a locally built prototype

Build the frontend as described in [the build notes](frontend-build/README.md), then copy the `multi-pop-rgds` folder to `/roms/themes/` on the RG DS. Keep SSH enabled for recovery.

```sh
bash /roms/themes/multi-pop-rgds/scripts/enable_multi_pop_rgds.sh
```

Activation backs up settings and compositor configuration under `/storage/.config/multi-pop-rgds`. It leaves the stock frontend binary intact. To restore the previous setup:

```sh
bash /roms/themes/multi-pop-rgds/scripts/restore_multi_pop_rgds.sh
```

Do not delete an active theme before restoring it. If its files were removed, stop `essway`, remove only its `multi-pop-rgds.conf` service drop-in, unmount the theme's bind mount on `/usr/bin/start_es.sh` if still present, restore the saved Sway configuration, reload systemd, and reboot.

## Scope

- Artwork and layout derived from Thor commit `43bb7db07d4dcb39bf788db864a60c33f8874015`.
- RG DS geometry: a 1920×480 virtual surface with a 640px hidden left margin, upper display in the middle, lower display at the right.
- Separate frontend built against the RG DS's installed runtime libraries; no Thor firmware libraries are distributed.
- Automatic updates are not shipped in the prototype.
- Game performance is independent of the theme. A conservative transfer policy is documented in [compatibility](docs/compatibility.md).

## Development and publication

Run `python3 tools/check-rgds.py` before deploying. Validate controller navigation, both touchscreens, game launch/return, sleep/wake, reboot, and rollback on hardware. Keep private build outputs, ROMs, BIOS files, game media, credentials, device configuration, and service keys outside Git. Built frontends must be accompanied by matching source and notices before any public release.

Original theme material retains **CC BY-NC-SA 4.0**; frontend and GPL launcher exceptions remain under their existing terms. See [LICENSE](LICENSE) and [licensing details](multi-pop-rgds/LICENSING.md). This adaptation was developed with AI assistance; inherited system illustrations were AI-generated.
