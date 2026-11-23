#!/bin/sh
# Install the one device change Single Pop relies on: the AYN Odin 2 touchscreen fix.
#
# The theme itself is only its folder. Its touch controls, though, need the touchscreen that ROCKNIX 20261101 often
# fails to bring up at boot (see odin2_touch.sh), so installing adds a small boot service that brings it up and runs
# it once now. remove_single_pop.sh undoes this. Run it over SSH from the installed theme folder. The SINGLE_POP_*
# variables exist only so the tests can run it against a fake device.
set -eu

storage=${SINGLE_POP_STORAGE:-/storage}
here=$(cd "$(dirname "$0")" && pwd)
helper_dir="$storage/.config/single-pop"
unit="$storage/.config/system.d/single-pop-touch.service"

# The fix binds a device that only the Odin 2 has; anywhere else it would do nothing useful.
model=$(tr -d '\000' < "${SINGLE_POP_MODEL:-/proc/device-tree/model}" 2>/dev/null || true)
case "$model" in
    *"Odin 2"*) ;;
    *)
        echo "Single Pop is for the AYN Odin 2; this device reports: ${model:-unknown}" >&2
        exit 1
        ;;
esac

mkdir -p "$helper_dir" "$(dirname "$unit")"
# The helper is copied out of the theme folder, so replacing or deleting the folder never leaves the service broken.
cp "$here/odin2_touch.sh" "$helper_dir/odin2_touch.sh"
chmod 755 "$helper_dir/odin2_touch.sh"
cat > "$unit" <<EOF
[Unit]
Description=Single Pop: bring up the AYN Odin 2 touchscreen if the boot probe missed it
# The touch controller is powered through the display panel, which is on once the compositor has started.
After=sway.service

[Service]
Type=oneshot
ExecStart=/bin/sh $helper_dir/odin2_touch.sh

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable single-pop-touch.service
# Running it now as well means the touchscreen works without a reboot.
if ! systemctl start single-pop-touch.service; then
    echo "The touchscreen did not come up yet; the service tries again at every boot." >&2
fi
echo "Touchscreen fix installed. Now choose multi-pop-odin2 under START → UI Settings → Theme Set."
