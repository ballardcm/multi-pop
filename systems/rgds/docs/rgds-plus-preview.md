# Multi Pop for RG DS Plus — 10.30.26.Preview

> **Preview:** Early hardware-tested build for **Anbernic RG DS Plus on ROCKNIX
> 20261001**. It is not fully tested. Please report issues with the device model,
> firmware version and steps to reproduce.
>
> **AI disclosure:** AI assistance (Codex) was used for this adaptation, build and
> validation. Original system illustrations were AI-generated. Upstream code,
> fonts and logo artwork retain their existing credits and license exceptions.

This version uses both 1024×768 displays at native resolution: artwork or a game
preview above, and the three-card library below. **Only the lower screen is
touch-sensitive on RG DS Plus.** Lower-screen swipe and tap have been tested.
The original RG DS is a different device; use its own release instead.

The frontend builds from the pinned RG DS sources with Plus-specific popup and
touch geometry. The source generator lives under `systems/rgds`; the original
RG DS frontend and release inputs remain unchanged. Shared artwork is reused
without modifying its bytes.

## What has been checked

- Installed and running on RG DS Plus with ROCKNIX 20261001.
- Native dual-screen layout, visible version and lower-screen swipe/tap.
- Reboot persistence: frontend and both panels return; Wi-Fi and Tailscale reconnect.
- Target runtime loader/help checks, generated gesture and popup-bound tests,
  source and binary checksums, and original RG DS regression checks.

Broad game/emulator compatibility, suspend/resume, long sessions and the full
recovery matrix are not yet validated. This release is marked as a GitHub
prerelease and is not offered to existing Thor or RG DS automatic updaters.
Preview updates are manual; leave automatic updates off.

## Install

1. Download **multi-pop-rgds-plus-rocknix-20261001.zip** and **SHA256SUMS** from
   [the Plus preview release](https://github.com/ballardcm/multi-pop/releases/tag/rgds-plus-10.30.26.Preview).
   Verify the ZIP with `shasum -a 256` (macOS) or `sha256sum` (Linux).
   Do not install the source ZIP or GitHub's automatically generated source archives.
2. Extract the ZIP. It deliberately contains a folder named **multi-pop-rgds**,
   plus `install-manifest.json`; the Plus hardware guard prevents activation on
   the original RG DS.
3. On the Plus, enable SSH in Network Settings. For USB, enable USB gadget mode
   **Network**, exit settings, then connect a data cable. Use the device's IP or
   USB hostname. The default root password is `rocknix` unless changed.
4. Copy the folder from your computer:

   ```sh
   scp -r multi-pop-rgds root@DEVICE:/roms/themes/
   ```

5. Close any game, connect with `ssh root@DEVICE`, and activate:

   ```sh
   bash /roms/themes/multi-pop-rgds/scripts/enable_multi_pop_rgds.sh
   ```

Activation backs up the existing frontend settings and Sway configuration under
`/storage/.config/multi-pop-rgds/`. It retains the stock frontend. Test the lower
touchscreen, A/B navigation, START menu, a game launch/return and reboot.

If a previous Multi Pop test is installed, **restore it before copying this
release**. Do not overwrite an active installation. If another theme owns
startup, use that theme's removal instructions first.

## Restore the previous frontend

Run over SSH before deleting the theme:

```sh
bash /roms/themes/multi-pop-rgds/scripts/restore_multi_pop_rgds.sh
```

Confirm the stock frontend works before removing `/roms/themes/multi-pop-rgds`.
ROMs, BIOS, saves and emulator settings are not included in the download or
changed by this installer. Keep the activation backups for recovery.

## Credits and license

Multi Pop is by **ballardcm**. The original RG DS port, its inherited code and
assets, and **DekosAnjo's additional-system contributions** remain credited in
the [RG DS README](https://github.com/ballardcm/multi-pop/tree/main/systems/rgds#development-and-license).
The principal logo sources are **HVR88's Monochrome Gaming Logos**, **Rookervik
and the RetroPie Carbon contributors**, and **Fabrice Caruso's Carbon
contributors**. Their bundled notices and per-file catalog remain intact.

Original Multi Pop material remains under **CC BY-NC-SA 4.0**. Frontend code,
launchers, fonts and third-party artwork retain their separate licenses. See
the included `LICENSING.md`, frontend notices and logo attribution files.
