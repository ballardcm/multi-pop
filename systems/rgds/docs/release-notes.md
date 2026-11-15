## 11.15.26.1

- **Install and remove on ROCKNIX 20261101.** Earlier releases kept running after a firmware update to 20261101, but their activation and restore helpers stopped with "This release requires ROCKNIX 20261001", so Multi Pop could be neither installed fresh nor removed there. Both helpers now accept 20261001 and 20261101, and no longer mistake the service settings the new firmware ships for another theme's startup override.
- Restore, a fresh activation and a reboot were each run on an RG DS with ROCKNIX 20261101. The full control checklist has not been repeated on that firmware yet.

The theme, frontend and startup helpers are unchanged from 11.14.26.1, so existing installations update automatically when Automatic updates is on. Take this update before running restore on 20261101.
