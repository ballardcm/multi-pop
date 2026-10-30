# RG DS Plus hardware prototype

AI assistance: Codex prepared this prototype workflow and its native-resolution adaptation.

The Plus has two 1024×768 panels. This private test stages the original RG DS
theme with a 3072×768 frontend canvas: one hidden panel-width margin, the upper
display, then the lower display. Popup bounds, touch coordinates and swipe
thresholds scale with the panels. The existing per-device Goodix calibration
matrix remains in place. Only the lower screen has touch hardware; upper-screen
touch hints and the upper touch-back control are removed or replaced accordingly.

From `systems/rgds`, stage a new private directory:

```sh
python3 tools/prepare-plus-prototype.py .local/plus-test/source
cd .local/plus-test/source
python3 tools/check-rgds.py
python3 tools/test-popup-bounds.py
python3 frontend-build/build.py --target root@DEVICE \
  --ssh-option ControlPath=/absolute/path/to/authenticated/socket \
  --work "$PWD/../build" --log "$PWD/../build.log"
```

Use the actual Plus as the runtime-library source. Confirm its device-tree model
is `Anbernic RG DS Plus` and its firmware revision matches the pinned ROCKNIX
20261001 revision before deployment. Compilation applies the generated patches
to pinned upstream sources and runs the target loader/help check.

The staged theme retains the `multi-pop-rgds` installation path for its existing
activation/restore mechanism. Its hardware guard accepts only the Plus. It shows
`RG DS Plus test 1` and uses an isolated prototype update-tag pattern; original
RG DS releases cannot become update candidates. Keep automatic updates off.

After a successful build, copy the staged theme to `/roms/themes/multi-pop-rgds`
on a clean device and run its `scripts/enable_multi_pop_rgds.sh`. Do not overwrite
an active installation; use the documented restore procedure first. Validate
both screens, menus, touch, buttons, game launch/return and reboot persistence.

To restore the previous frontend, run on the handheld:

```sh
bash /roms/themes/multi-pop-rgds/scripts/restore_multi_pop_rgds.sh
```

This is a local hardware test, not a public release. Before distribution, the
new binary needs hardware validation, complete build-input hashes, matching
source archives and registration as a new `rgds-frontend-` prerelease. Its changed
startup helpers require a clean installation, not an original-RG-DS automatic
update. Keep runtime libraries, credentials and device state under `.local/`.
