# RG DS repository instructions

Keep ROMs, BIOS, game media, credentials, runtime libraries, device state, and build caches out of Git and public releases. `.local/` is private operational storage.
Use `3799765+ballardcm@users.noreply.github.com` in commit metadata.
Use `ballardcm` for repository-owner attribution and new commit author names. Keep the owner’s personal name out of public documentation and new commit metadata; preserve third-party contributor credits.
Preserve upstream attribution, CC BY-NC-SA scope and third-party license exceptions. Disclose AI assistance.
Run `python3 tools/check-rgds.py` and validate changed runtime behavior on an RG DS. Use pull requests for subsequent changes after the initial repository seed. Prototype deployment is allowed when the user requests it; public release and visibility changes require explicit authorization.
