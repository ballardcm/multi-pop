#!/bin/sh
# Bring up the AYN Odin 2 touchscreen when ROCKNIX's boot-time probe missed it.
#
# On ROCKNIX 20261101 the Odin 2's Synaptics touch controller (rmi4 over I2C) is probed before the display panel has
# powered it. The probe fails with "rmi_set_page: set page failed: -6" and the touchscreen never appears, whatever the
# theme. Asking the driver to bind the same device again once the panel is on brings it up. single-pop-touch.service
# runs this at boot; it does nothing when the touchscreen is already working, so it stays harmless on firmware that
# fixes the probe. The variables below exist only so the tests can point it at a fake sysfs.
sysfs=${SINGLE_POP_SYSFS:-/sys}
tries=${SINGLE_POP_TRIES:-15}
pause=${SINGLE_POP_WAIT:-2}

# Print each rmi4 touch controller that the kernel knows about but no driver has claimed.
unbound() {
    for device in "$sysfs"/bus/i2c/devices/*; do
        [ "$(cat "$device/name" 2>/dev/null)" = rmi4-i2c ] || continue
        [ -e "$device/driver" ] && continue
        basename "$device"
    done
}

attempt=0
while :; do
    missing=$(unbound)
    [ -z "$missing" ] && exit 0
    attempt=$((attempt + 1))
    if [ "$attempt" -gt "$tries" ]; then
        echo "single-pop: the touchscreen is still missing after $tries attempts: $missing" >&2
        exit 1
    fi
    # A failed bind is expected while the panel is still powering up; the next pass tries again.
    for device in $missing; do
        echo "$device" > "$sysfs/bus/i2c/drivers/rmi4_i2c/bind" 2>/dev/null
    done
    sleep "$pause"
done
