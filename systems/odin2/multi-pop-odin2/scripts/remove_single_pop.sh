#!/bin/sh
# Remove Single Pop from an AYN Odin 2: its touchscreen boot service, that service's helper and the theme folder.
#
# Choose another theme under UI Settings → Theme Set first; otherwise the frontend would be left selecting a theme that
# no longer exists, so this stops without changing anything. Pass --keep-theme to remove only the touchscreen service.
# The SINGLE_POP_* variables exist only so the tests can run it against a fake device.
set -eu

storage=${SINGLE_POP_STORAGE:-/storage}
here=$(cd "$(dirname "$0")" && pwd)
theme=$(dirname "$here")
helper_dir="$storage/.config/single-pop"
unit="$storage/.config/system.d/single-pop-touch.service"
settings="$storage/.config/emulationstation/es_settings.cfg"

keep_theme=false
case "${1:-}" in
    --keep-theme) keep_theme=true ;;
    "") ;;
    *) echo "Usage: $0 [--keep-theme]" >&2; exit 2 ;;
esac

if ! $keep_theme && grep -q 'name="ThemeSet" value="multi-pop-odin2"' "$settings" 2>/dev/null; then
    echo "multi-pop-odin2 is still the selected theme. Choose another under START → UI Settings → Theme Set," >&2
    echo "then run this again. Nothing was changed." >&2
    exit 1
fi

if [ -e "$unit" ]; then
    systemctl disable single-pop-touch.service || true
    rm -f "$unit"
    systemctl daemon-reload
fi
rm -rf "$helper_dir"
echo "Touchscreen service removed. From the next boot the touchscreen behaves as ROCKNIX leaves it."

if ! $keep_theme; then
    # Delete only a folder that is plainly this theme, never whatever directory the script happens to sit in.
    if [ "$(basename "$theme")" != multi-pop-odin2 ] || [ ! -f "$theme/theme.xml" ]; then
        echo "Not deleting $theme: it does not look like the multi-pop-odin2 theme folder." >&2
        exit 1
    fi
    rm -rf "$theme"
    echo "Theme folder removed: $theme"
fi
