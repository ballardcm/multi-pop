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
