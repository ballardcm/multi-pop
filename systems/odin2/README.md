# Multi Pop Odin 2 ("Single Pop")

> **AI disclosure:** This theme was developed with the help of AI (Claude Code), and its original system illustrations were AI-generated. Third-party components and their credits are listed in the [theme README](multi-pop-odin2/README.md) and [LICENSING.md](multi-pop-odin2/LICENSING.md).

A single-screen edition of Multi Pop for the AYN Odin 2 running ROCKNIX EmulationStation. It uses the same hardware illustrations, palettes and logos as the Thor and RG DS themes, laid out for one 1920×1080 display. On screen it calls itself **Single Pop**.

**[Install](#install) · [Remove](#remove) · [Touchscreen fix](#touchscreen-fix) · [What's different from Thor](#whats-different-from-thor)**

**Status: preview.** The first release, `odin2-11.22.26.Preview`, is published as a prerelease. It has been tested on the original Odin 2 on ROCKNIX 20261101, but **not on the Odin 2 Portal**. The Portal shares the resolution and chip, but its touchscreen may differ, so the touchscreen fix is unproven there. The 1280×720 Odin 2 Mini is untested as well. Reports and pull requests are welcome.

## Layout

- **Systems:** a colored rail on the left gives the maker, the system and its launch year, with the game count, SINGLE POP and the installed version below them. The rest of the screen is a tinted stage holding the system's hardware illustration. Swipe across the stage, or press left and right, to change system; the hardware follows your finger, and the rail and stage crossfade to the next system's colors. Tap the stage or press A to open it.
- **Games:** the rail stays, with a small copy of the hardware. A vertical cover carousel runs down the middle, with the selected cover framed in the system's color. The right-hand panel shows the gameplay preview (a screenshot, then the video after three seconds, muted), the title, genre, year and publisher, and a description that scrolls when it is long. Swipe the covers, or press up and down, to browse. Tap the rail, or press B, to go back to the systems.

## Install

You need an AYN Odin 2 running ROCKNIX with SSH turned on (START → System Settings → Network Settings → Enable SSH), and a computer on the same Wi-Fi network with `ssh` and `scp`. SSH is needed to install the [touchscreen fix](#touchscreen-fix) that Single Pop's touch controls rely on.

### 1. Download and check the release

From the newest Odin 2 release, tagged `odin2-` (the current one is the `odin2-11.22.26.Preview` prerelease), on the [Multi Pop releases page](https://github.com/ballardcm/multi-pop/releases?q=odin2-), download `multi-pop-odin2-rocknix-theme.zip` and `SHA256SUMS` into the same folder. Check the download from that folder:

```sh
shasum -a 256 --check --ignore-missing SHA256SUMS
```

On Linux use `sha256sum` in place of `shasum -a 256`. It should print `multi-pop-odin2-rocknix-theme.zip: OK`. Extract the ZIP, which gives you a `multi-pop-odin2` folder.

### 2. Copy the folder to the Odin 2

Put the `multi-pop-odin2` folder inside the `themes` folder of the ROCKNIX games storage, so that `themes/multi-pop-odin2/theme.xml` exists. Over SSH, with the device's address in place of `ODIN2_IP`:

```sh
scp -r \
  multi-pop-odin2 \
  root@ODIN2_IP:/storage/roms/themes/
```

### 3. Install the touchscreen fix

Run the installer from the copied folder:

```sh
ssh root@ODIN2_IP \
  sh /storage/roms/themes/multi-pop-odin2/scripts/install_single_pop.sh
```

It adds a small boot service, `single-pop-touch.service`, and runs it once, so the touchscreen works straight away and after every reboot. It refuses to run on anything but an Odin 2. See [Touchscreen fix](#touchscreen-fix) for what it does.

### 4. Choose it

On the Odin 2, press START and open UI Settings → Theme Set, then choose `multi-pop-odin2`. Leave Game List View Style on Automatic: libraries then open in the carousel layout.

## Update

Download the newer release, replace the `multi-pop-odin2` folder with the new one, and run `install_single_pop.sh` again as in step 3; it replaces the boot service with the release's copy. The version appears in the rail and under UI Settings → Theme Configuration. Automatic updates, as on Thor, aren't part of this edition yet.

## Remove

Choose another theme under UI Settings → Theme Set first, then run the remover:

```sh
ssh root@ODIN2_IP \
  sh /storage/roms/themes/multi-pop-odin2/scripts/remove_single_pop.sh
```

It disables and deletes `single-pop-touch.service` and its helper in `/storage/.config/single-pop/`, then deletes the theme folder. While Single Pop is still the selected theme it stops without changing anything. Add `--keep-theme` to remove only the touchscreen service. Nothing else on the device was changed. From the next boot the touchscreen behaves as ROCKNIX leaves it, which on 20261101 often means not at all.

## Touchscreen fix

On ROCKNIX 20261101 the Odin 2's touchscreen often doesn't work at all, with any theme. Its Synaptics touch controller is powered through the display panel. ROCKNIX probes for it at boot before the panel is on, the probe fails (`rmi4_i2c 4-0020: rmi_set_page: set page failed: -6` in `dmesg`), and the touchscreen never appears.

`install_single_pop.sh` copies `odin2_touch.sh` to `/storage/.config/single-pop/` and adds `single-pop-touch.service` to `/storage/.config/system.d/`. At boot, after the compositor has started and the panel is on, the service checks for a touch controller that no driver has claimed and asks the driver to bind it again, retrying for up to 30 seconds. When the touchscreen is already working it does nothing, so it stays harmless if a later ROCKNIX fixes the probe. `remove_single_pop.sh` takes it away again.

To see whether it worked, `systemctl status single-pop-touch.service` should show a clean exit, and `grep Synaptics /proc/bus/input/devices` should list `Synaptics TD4328`.

## What's different from Thor

Multi Pop for Thor ships its own EmulationStation build, which adds paging by three games, its touch gestures, and dialogs kept on the upper screen. It also includes startup scripts and an updater. With a single screen none of that is needed. This edition runs on the frontend ROCKNIX already provides. That frontend's own touch support handles dragging and tapping the carousels, and the theme makes the library rail a back button with the frontend's standard `onclick` action. The system screen has no tap-to-move arrows, because the stock frontend doesn't connect tap actions on that screen. Its only change to the device is the [touchscreen fix](#touchscreen-fix).

## Building a release

From `systems/odin2`:

```sh
python3 tools/check-odin2.py
python3 tools/test-odin2-scripts.py
python3 tools/test-package-release.py
python3 tools/test-release-version.py
python3 tools/package-release.py
```

The last command writes the installable ZIP, a source ZIP and `SHA256SUMS` to `dist/`. Releases are published by the `Odin 2` workflow when a maintainer runs it on `main`; see [docs/releases.md](docs/releases.md).

## License

Original material is offered under CC BY-NC-SA 4.0, with third-party exceptions; see [LICENSE](LICENSE) and [LICENSING.md](multi-pop-odin2/LICENSING.md).
