## 11.14.26.1

- **Lower screen on ROCKNIX 20261101.** After updating ROCKNIX to 20261101 the Thor's lower screen stayed dark under Multi Pop, because that firmware powers the lower panel off two seconds after startup. Multi Pop now waits for that step and turns the panel back on, so both screens come up at every start. Activation and restore also accept the configuration the new firmware generates.
- **Steam games in the library.** Steam shortcuts under the Steam system now show their cover, a screenshot, a muted trailer preview and their description, genre, developer, publisher and release date. The cover comes from Steam's own cache on the Thor; the rest is downloaded from the Steam store after Multi Pop starts and appears from the next start.

The bundled frontend is unchanged and was built for ROCKNIX 20261001; on 20261101 it starts and both displays work, and the full control checklist has not been repeated there yet. Existing installations update automatically when Automatic updates is on.
