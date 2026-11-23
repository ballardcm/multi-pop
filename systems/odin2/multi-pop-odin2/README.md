# Multi Pop for AYN Odin 2 ("Single Pop")

> **AI disclosure:** This theme was developed with the help of AI (Claude Code), and its original system illustrations were AI-generated. Third-party components and their credits are listed below and in [LICENSING.md](LICENSING.md).

Multi Pop is a ROCKNIX EmulationStation theme built around original hardware illustrations. This is its single-screen edition for the AYN Odin 2. On screen it calls itself **Single Pop**: it's the same theme, on one screen.

- **Systems:** a colored rail on the left shows the maker, the system and its launch year. The rest of the screen is a softly tinted stage holding the system's hardware illustration. Swipe across the stage, tap the ‹ › arrows, or press left and right to move between systems; tap the stage or press A to open one.
- **Games:** the rail stays put. A vertical cover carousel sits in the middle, and the right-hand panel shows a gameplay preview with the game's title, genre, year, publisher and description. A screenshot appears first, and a video, if there is one, starts after three seconds with the sound off. Missing covers fall back to the game's image, then to the system's card. Tap the rail, or press B, to go back.

It runs on the Odin 2's own ROCKNIX EmulationStation; unlike Multi Pop for Thor, there is no replacement frontend. Its one change to the device is a touchscreen fix. ROCKNIX 20261101 often fails to bring up the Odin 2's touchscreen at boot, and `scripts/install_single_pop.sh` adds a small boot service that brings it up.

Battery and Wi-Fi appear at the top right and follow the frontend's own indicator settings. UI Settings → Theme Configuration shows the installed version.

## Install

Copy this `multi-pop-odin2` folder into the `themes` folder of the Odin 2's ROCKNIX storage (`/storage/roms/themes/`). Run `sh /storage/roms/themes/multi-pop-odin2/scripts/install_single_pop.sh` over SSH to install the touchscreen fix. Then press START and pick `multi-pop-odin2` under UI Settings → Theme Set. Leave Game List View Style on Automatic, and libraries open in the carousel layout described above. Step-by-step instructions are in the [project README](https://github.com/ballardcm/multi-pop/tree/main/systems/odin2#install).

To remove it, choose another theme under Theme Set, then run `sh /storage/roms/themes/multi-pop-odin2/scripts/remove_single_pop.sh`. It removes the touchscreen service and deletes this folder.

## Credits

The sidebar marks come from [HVR88's Monochrome Gaming Logos](https://github.com/HVR88/Monochrome-Gaming-Logos) and [Rookervik and the RetroPie Carbon contributors](https://github.com/RetroPie/es-theme-carbon), building on Nils Bonenberger's Simple theme. The FinalBurn Neo phoenix comes from [Fabrice Caruso's expanded Carbon collection](https://github.com/fabricecaruso/es-theme-carbon). These logos are third-party artwork, not AI-generated Multi Pop illustrations; full acknowledgments, source records and original notices are in [assets/logos/README.md](assets/logos/README.md).

[DekosAnjo](https://github.com/DekosAnjo) contributed the additional systems first added to Multi Pop RG DS: Channel F, Odyssey², Famicom Disk System, MSX2, Mega CD, Super Cassette Vision, Mega Duck, Nintendo 64DD, Pokémon Mini, Doom, TIC-80, WASM-4 and Watara Supervision.

Roboto and Roboto Condensed are used under the Apache 2.0 license; see `assets/fonts/`. Licensing for everything else is in [LICENSING.md](LICENSING.md).
