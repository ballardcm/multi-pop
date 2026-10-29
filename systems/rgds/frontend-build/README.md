# Build the RG DS frontend

Requires Python 3, OpenSSH, patch, and Docker with Linux ARM64 support. Source archives and dependencies are pinned in `release.json`; runtime libraries are collected privately from an RG DS running ROCKNIX 20261001.

```sh
python3 frontend-build/build.py --target root@RGDS_ADDRESS \
  --work "$PWD/frontend-build/private/build-01" --log "$PWD/frontend-build/private/build-01.log"
```

Add `--ssh-option ControlPath=/absolute/path/to/socket` to reuse an authenticated connection. Use a new work directory for each build. The output is `multi-pop-rgds/frontend/emulationstation`, ignored by Git. The build applies the RG DS patches, compiles with networking disabled, and validates the loader and help command against the collected runtime. No online service keys are compiled in; the existing on-device integration helper uses the stock frontend at activation.

Before publishing a binary, provide its exact upstream sources, patches, build inputs, hashes, and third-party notices. Successful compilation does not replace hardware testing.
