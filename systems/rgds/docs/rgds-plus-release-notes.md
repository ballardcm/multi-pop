First **RG DS Plus preview**, for **ROCKNIX 20261001**. This is an early build,
not a fully tested stable release.

- Native 1024×768 dual-screen layout, with system artwork/game previews above
  and a three-card library below.
- Lower-screen swipe/tap support. The Plus's top screen is not touch-sensitive.
- Plus-specific frontend, checked source/binary hashes and matching source ZIP.
- Restore helper and activation backups; stock frontend retained.

Basic layout, lower touch and reboot persistence have been tested on hardware. Broad game coverage,
suspend/resume, long sessions and the full recovery matrix remain unverified.
Automatic updates do not install this preview on Thor or the original RG DS.

Download **multi-pop-rgds-plus-rocknix-20261001.zip** and **SHA256SUMS**.
The ZIP contains `multi-pop-rgds/`; this is intentional. Restore an existing
test installation before copying this release. Do not use the original RG DS
package on the Plus.

[Install, restore, credits and known testing limits](https://github.com/ballardcm/multi-pop/blob/main/systems/rgds/docs/rgds-plus-preview.md)

Multi Pop has moved to [ballardcm/multi-pop](https://github.com/ballardcm/multi-pop).
Existing Thor/original RG DS users can run **two consecutive upgrades**, rebooting
between them: first the transition release points the updater here, then the next
upgrade installs the current monorepo release. A fresh installation from this
repository also works. Already on a monorepo release? No migration is needed.

AI assistance (Codex) was used for this port. Original artwork remains under
CC BY-NC-SA 4.0; upstream code, fonts and third-party logos retain their licenses
and credits, including DekosAnjo's additional-system contributions.
