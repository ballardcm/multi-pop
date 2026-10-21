# Prototype 0.1 validation

Target: Anbernic RG DS, ROCKNIX 20261001 (`c445081a59518f37d9776e5412dd7b14910696f7`).

- Local checks: XML and referenced assets, panel bounds, launcher syntax, compiled touch recognizer tests.
- Frontend: source revision `cada856d86e3115fbbf0bce09dd761b0ee8fa9fd`, RG DS geometry patches, matching device libraries, no embedded service credentials.
- Hardware validation is in progress. Controller and touch feel require player feedback; sleep/wake and broad game compatibility are not yet certified.

The prototype preserves stock emulator configuration and provides a restore helper. No ROMs, BIOS, scraped media, runtime libraries, or local connection details belong in the repository.
