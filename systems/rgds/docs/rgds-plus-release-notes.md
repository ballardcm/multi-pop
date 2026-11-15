**RG DS Plus** release for **ROCKNIX 20261001 and 20261101**.

- **Install and remove on ROCKNIX 20261101.** Earlier builds kept running after a
  firmware update to 20261101, but their activation and restore helpers stopped
  with "This release requires ROCKNIX 20261001", so Multi Pop could be neither
  installed fresh nor removed there. Both helpers now accept either firmware.
- Restore, a fresh activation and a reboot were each run on a Plus with ROCKNIX
  20261101. Broad game coverage, suspend/resume, long sessions and the full
  recovery matrix remain unverified.

The theme, frontend and startup helpers are unchanged from 11.14.26.1, so a Plus
with Automatic updates on takes this release by itself; take it before running
restore on 20261101. Thor and original RG DS updaters never install Plus
releases. A Plus still on 10.30.26.Preview does not update itself: install this
release by hand once.

Download **multi-pop-rgds-plus-rocknix-20261001.zip** and **SHA256SUMS**.
The ZIP contains `multi-pop-rgds/`; this is intentional. Restore an existing
installation, including the preview, before copying this release. Do not use the original RG DS
package on the Plus.

[Install, restore, credits and known testing limits](https://github.com/ballardcm/multi-pop/blob/main/systems/rgds/docs/rgds-plus.md)

AI assistance (Codex and Claude) was used for this port and this release. Original artwork remains under
CC BY-NC-SA 4.0; upstream code, fonts and third-party logos retain their licenses
and credits, including DekosAnjo's additional-system contributions.
