# Prototype 0.2 validation

Target: Anbernic RG DS, ROCKNIX 20261001 (`c445081a59518f37d9776e5412dd7b14910696f7`).

Validated:
- XML, referenced assets, panel bounds, launcher syntax, and compiled touch-recognizer tests.
- ARM64 frontend built from pinned revision `cada856d86e3115fbbf0bce09dd761b0ee8fa9fd` against RG DS runtime libraries; loader and help checks passed.
- Screenshots of both physical panels, including the native Start menu on the upper panel.
- Stock frontend restoration and prototype reactivation.
- User confirmed touch returned after restoring the stock `seat1` assignment. Both Goodix panels share one identifier; their individual half-width calibration matrices are retained.

The screenshot-led revision removes the narrow sidebar and baked-in hero text, centers transparent hardware artwork, adds native manufacturer/system/year text, smooths scaled artwork, and restores the X Game info hint. Matching headers and a hardware backdrop use the system palette. Larger status icons remain above; Multi Pop v0.2 appears on the right of the lower header. Top-screen instructions retain swipe/tap navigation on either screen.

Prototype 0.2 applies the independent review: a light palette-tinted stage replaces the heavy backdrop and oval; smaller hardware has more breathing room; the system title sits above secondary manufacturer/year text; selection outlines meet a 3:1 contrast ratio against the theme paper. Colored headers retain the visual identity. The user accepted this design. Settled SNES system-view and NES game-view screenshots were checked on both physical displays, including the X Game info footer. Temporary startup overrides used for those captures were restored. The X action itself still requires validation.

Still requiring testing: reboot, sleep/wake, extended gameplay and return across multiple emulators, and touch feel across all views. A readable menu does not establish whole-library game compatibility.

The prototype preserves stock emulator configuration and provides a restore helper. No ROMs, BIOS, scraped media, runtime libraries, or local connection details belong in the repository.

## Release 0.3.0 acceptance

The documented restore-first removal was run on the RG DS, the theme folder was removed, the service override and launcher bind mount were absent, and `/usr/bin/emulationstation` ran successfully. The release ZIP and source ZIP checksums were verified; the installable ZIP was extracted, copied with SCP, and activated using the README commands. Version 0.3.0 ran from the theme frontend.

Physical upper/lower screenshots verified the main menu, Network Settings, hostname on-screen keyboard, an update message box, game options, and savestate manager. Dialog controls stayed on the 640×480 upper panel; only the dimmed backdrop extended across the lower panel. Hostname entry was cancelled without edits. Theme Configuration showed Installed version 0.3.0, Automatic updates Off, and Check for updates.

The automatic-update acceptance test is tracked in the release notes. Unit/integration coverage includes checksum rejection, incompatible firmware, older versions, startup-helper changes, staging/apply/confirmation, retry rollback, opt-out behavior and local-network failures. Packaging checks reject private inputs and unverified binaries and verify deterministic archives.


## Thor design-language preview

Adapted the approved Thor system browser to a 160px sidebar and a pale hardware stage on the 640×480 upper panel. The manufacturer and platform marks are palette-tinted and attributed. The lower header carries MULTI POP and the installed version; Library replaces its generic heading with the system identity. Full-width gameplay preview geometry remains unchanged. Carousel defaults are now instant with 100ms motion, replacing the implicit 500ms default.

Validated locally on ROCKNIX 20261001: live system and Library screens, collection text/blank-year fallback, original controller select mapping, and passwordless SSH. Recordings are being reviewed. No public release or version bump is made by this PR; see releases.md for the planned numbering migration.
