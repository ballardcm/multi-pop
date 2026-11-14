#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/multi_pop_thor_common.sh"

# A fresh --prepare activation owns a live mount and needs the full canvas for theme selection.
# After reboot that mount is gone, so other themes return to the normal frontend.
# The stock launcher runs in its own shell because ROCKNIX's profile scripts fail under this script's strict mode.
if ! grep -q 'name="ThemeSet" value="multi-pop-thor"' /storage/.config/emulationstation/es_settings.cfg && ! owns_launcher_mount; then
    exec /usr/bin/start_es.sh
fi

# ROCKNIX regenerates this configuration at boot, so restore the Thor display and touch layout.
config=/storage/.config/sway/config
fragment=/storage/.config/sway/multi-pop-thor.conf
find_theme
# A downloaded update is swapped in before the frontend starts, so an update never restarts the frontend under the player.
auto_update="$THEME/scripts/auto_update.py"
if [[ "$THEME" == /roms/themes/multi-pop-thor && -f "$auto_update" ]]; then
    python3 "$auto_update" apply || true
fi
# Steam shortcuts get their cover, preview and details written into the game list here, while no frontend is running
# to overwrite it. This pass uses only files already on the Thor, so it cannot delay the start.
steam_library="$THEME/scripts/steam_library.py"
if [[ -f "$steam_library" ]]; then
    python3 "$steam_library" merge || true
fi
launcher="$THEME/scripts/start_es_thor.sh"
[[ -f "$fragment" && -x "$launcher" ]]
export SWAYSOCK=/run/0-runtime-dir/sway-ipc.0.sock
for attempt in {1..30}; do
    [[ -S "$SWAYSOCK" ]] && swaymsg -t get_outputs >/dev/null 2>&1 && break
    sleep 1
done
swaymsg -t get_outputs >/dev/null
# ROCKNIX 20261101 starts Sway with a one-shot that powers the lower panel on, rotates it and powers it off again two
# seconds later. Sway launched it from the configuration as ROCKNIX generated it, before this script could remove the
# line, so its power-off would land after the panel is turned on below and leave the lower screen dark. Waiting for it
# to appear and then to end lets that power-off go first. The fragment already rotates and powers the panel.
if grep -Eq "$STOCK_LOWER_ROTATION" "$config" && command -v pgrep >/dev/null 2>&1; then
    for attempt in {1..15}; do
        pgrep -f "$STOCK_LOWER_ROTATION" >/dev/null && break
        sleep 0.2
    done
    for attempt in {1..50}; do
        pgrep -f "$STOCK_LOWER_ROTATION" >/dev/null || break
        sleep 0.2
    done
fi
staged=$(mktemp "$config.multi-pop-startup.XXXXXX")
trap 'rm -f "$staged"' EXIT
awk -v rotation="$STOCK_LOWER_ROTATION" '
    /^[[:space:]]*output DSI-1 power off[[:space:]]*$/ { next }
    # A restart of Sway alone rereads this file, and must not run the one-shot against the prepared layout.
    $0 ~ "^[[:space:]]*exec[[:space:]]" && $0 ~ rotation { next }
    /^[[:space:]]*exec_always[[:space:]]+swaymsg[[:space:]]+input[[:space:]]+"0:0:bottom_touchscreen"[[:space:]]+events[[:space:]]+disabled[[:space:]]*$/ { next }
    /^exec_always swaymsg/ {
        sub(/,[[:space:]]*output DSI-1 power off[[:space:]]*$/, "")
    }
    { print }
' "$config" > "$staged"
if ! grep -Fxq "$INCLUDE_LINE" "$staged"; then
    printf '\n# The Multi Pop Thor fragment keeps the dual-screen layout separate from the base configuration.\n%s\n' "$INCLUDE_LINE" >> "$staged"
fi
if ! cmp -s "$config" "$staged"; then
    # Preserve each generated configuration before changing its display and lower-touchscreen directives.
    cp -p "$config" "/storage/.config/multi-pop-thor/sway-before-startup-$(date -u +%Y%m%dT%H%M%SZ).conf"
    chmod 644 "$staged"
    if [[ -f "$STATE/active" ]] && ! grep -Fxq "$INCLUDE_LINE" "$config"; then
        # A configuration without the include is fresh from ROCKNIX, and a firmware update changes what it generates.
        # Recording it as the original, and its prepared form as the installed one, keeps a later activation or
        # restore from refusing a configuration that only the firmware changed.
        cp -p "$config" "$STATE/sway.backup"
        cp -p "$staged" "$STATE/installed.sway"
    fi
    mv "$staged" "$config"
fi
# A restart without a reboot keeps the old launcher mount, so an updated launcher must replace it.
if owns_launcher_mount && ! cmp -s "$LAUNCHER_TARGET" "$launcher"; then
    umount "$LAUNCHER_TARGET"
fi
# A file bind mount disappears at reboot; recording its new identity also keeps updates and restoration usable.
guard_launcher_mount
if ! owns_launcher_mount; then
    mount --bind "$launcher" "$LAUNCHER_TARGET"
    stat -c '%d:%i' "$LAUNCHER_TARGET" > "$STATE/launcher.identity"
fi
# Refreshing the keys at each boot follows firmware updates; a failure only disables scraping and achievements.
write_integration_keys || true
swaymsg reload >/dev/null
swaymsg 'output * power on' >/dev/null
for panel in /sys/class/backlight/*; do
    [[ -f "$panel/bl_power" ]] && printf '0\n' > "$panel/bl_power"
done
# Sway can leave the workspace focused when the frontend's window appears, and SDL then ignores the gamepad, so focus it once it exists.
# A second focus follows the layout rules that move the window after it maps. Both panels are powered once more then,
# so a firmware startup command this script does not yet know cannot leave the lower screen dark.
setsid bash -c 'for attempt in {1..60}; do sleep 1; if swaymsg "[app_id=\"^emulationstation$\"] focus" >/dev/null 2>&1; then sleep 3; swaymsg "[app_id=\"^emulationstation$\"] focus" >/dev/null 2>&1; swaymsg "output * power on" >/dev/null 2>&1; exit 0; fi; done' </dev/null >/dev/null 2>&1 &
# The background check confirms a just-applied update and stages any newer release for the next start.
if [[ "$THEME" == /roms/themes/multi-pop-thor && -f "$auto_update" ]]; then
    setsid python3 "$auto_update" background </dev/null >/dev/null 2>&1 &
fi
# ROCKNIX 20261101 lets a game render below the panel's size by scaling the output, and its own launcher undoes that
# scaling when a game ended without doing so. The Multi Pop launcher cannot change without a reinstall, so the reset
# runs here, in its own shell because ROCKNIX's profile scripts fail under this script's strict mode.
bash -c '. /etc/profile >/dev/null 2>&1; declare -F scanout_reset_stale >/dev/null && scanout_reset_stale' >/dev/null 2>&1 || true
# Descriptions, screenshots and trailers come from the Steam store once the network is up, for the next start to show.
if [[ -f "$steam_library" ]]; then
    setsid python3 "$steam_library" fetch </dev/null >/dev/null 2>&1 &
fi
exec "$launcher"
