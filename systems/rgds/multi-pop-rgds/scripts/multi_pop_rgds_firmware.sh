#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later

# What activation and restore need to run on ROCKNIX 20261101 as well as 20261001. The two tests below replace the
# ones in multi_pop_rgds_common.sh, which refused both a fresh install and a restore on 20261101. They live here
# rather than in that file because installed updaters refuse a release that changes it, and a device already on
# 20261101 can receive this only through an automatic update: a reinstall begins with restore, which the old tests
# refuse there. Fold this back into the common helper in the next release that is planned as a reinstall.

OS_RELEASE=/etc/os-release
# ROCKNIX names a build by the commit it was made from; these are the tags 20261001 and 20261101.
SUPPORTED_BUILDS=(c445081a59518f37d9776e5412dd7b14910696f7 cefc14339a4ae18c02bb69888f27835e50664b60)

check_firmware() {
    local build
    for build in "${SUPPORTED_BUILDS[@]}"; do
        if grep -q "^BUILD_ID=\"$build\"" "$OS_RELEASE"; then
            return
        fi
    done
    fail 'This release requires ROCKNIX 20261001 or 20261101.'
}

# check_host keeps every other test. Should its firmware line ever stop matching here, it stays in place and the
# helpers go on refusing other firmware, which is the safe way for this to fail.
eval "$(declare -f check_host | sed '/BUILD_ID=/d')"

# ROCKNIX 20261101 ships drop-ins of its own under /usr/lib/systemd, one for every service and one for essway, and
# systemd lists them among essway's. They are part of the read-only firmware image, not another theme's startup
# override, so only the entries outside /usr are held against this activation.
guard_startup_override() {
    local overrides entry
    overrides=$(systemctl show essway --property=DropInPaths --value)
    for entry in $overrides; do
        [[ "$entry" != /usr/* ]] || continue
        [[ "$entry" == "$SERVICE_OVERRIDE" ]] || fail "Another essway service override exists: $entry. It was preserved."
    done
    if [[ -e "$SERVICE_OVERRIDE" || -L "$SERVICE_OVERRIDE" ]]; then
        [[ ! -L "$SERVICE_OVERRIDE" && -f "$STATE/installed.service" ]] &&
        cmp -s "$SERVICE_OVERRIDE" "$STATE/installed.service" ||
            fail 'The startup override is not owned by this activation. It was preserved.'
    elif [[ -f "$STATE/installed.service" ]]; then
        fail 'The startup override was removed after activation. Inspect its activation record first.'
    fi
}
