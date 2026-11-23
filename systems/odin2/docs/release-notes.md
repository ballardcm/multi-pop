**Preview.** This is the first release of Single Pop, Multi Pop's single-screen edition for the AYN Odin 2. It is published as a prerelease while it gets wider testing.

- **Tested on:** the original AYN Odin 2 on ROCKNIX 20261101, with the stock EmulationStation. Installing, both views, swiping between systems and covers, tapping to open, tapping the rail to go back, and the touchscreen fix all work there.
- **Not tested on the Odin 2 Portal.** It has the same 1920×1080 resolution and chip, so the theme should look the same. Its touchscreen may use a different controller, though, and whether the touchscreen fix is needed or does anything there is unknown. The Odin 2 Mini, with its smaller 1280×720 screen, hasn't been tried either. Reports from either are welcome.
- **Touchscreen fix:** ROCKNIX 20261101 often fails to bring up the Odin 2's touchscreen at boot, with any theme. `scripts/install_single_pop.sh` adds a boot service that brings it up, and `scripts/remove_single_pop.sh` takes it away again.
- **No automatic updates yet:** to update, replace the folder and run the installer again.
