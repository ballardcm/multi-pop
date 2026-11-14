#!/usr/bin/env python3
"""Give the Steam games in the library their cover, screenshot, trailer and details.

ROCKNIX lists every shortcut Steam writes to /storage/.local/share/applications under its Steam system, but nothing
describes those shortcuts to the frontend, so each one appears as a bare name. `merge` runs before the frontend starts:
it copies the artwork Steam has already cached on the device and writes the shortcuts' entries in that folder's
gamelist.xml, using no network so a start is never held up. `fetch` runs in the background after the frontend starts
and downloads what only the Steam store has, the description, a screenshot and a trailer, for the next start to pick up.
`sync` does both at once for a manual run while the frontend is stopped.
"""

import argparse
from dataclasses import dataclass
import fcntl
import html
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# Steam writes `Exec=steam steam://rungameid/<appid>` into each shortcut; the id is all that ties it to the store.
SHORTCUT_APP = re.compile(r'^Exec=.*steam://rungameid/(\d+)\s*$', re.MULTILINE)
SHORTCUT_NAME = re.compile(r'^Name=(.+)$', re.MULTILINE)
# Paths below this folder are the ones this script wrote, so they are the only media references it may replace.
OWNED = './media/steam/'
# Steam has named its cached library artwork two ways: a folder per game, and before that one flat folder.
COVER_NAMES = ('library_capsule.jpg', 'library_600x900.jpg')
HERO_NAMES = ('library_hero.jpg',)
MONTHS = {name: number for number, name in enumerate(
    ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'), 1)}
# The preview well is 938 by 695 pixels, which a 16:9 trailer fills at 528 lines; a taller rendition only costs storage.
TRAILER_HEIGHT = 528
# A preview loops while a game is selected, so the opening minute is enough and keeps each trailer near 20 MB.
TRAILER_SECONDS = 60
TRAILER_BYTES = 64 * 1024 * 1024
IMAGE_BYTES = 16 * 1024 * 1024
TEXT_BYTES = 2 * 1024 * 1024


@dataclass
class Config:
    applications: Path = Path('/storage/.local/share/applications')
    steam: Path = Path('/storage/.local/share/Steam')
    state: Path = Path('/storage/.config/multi-pop-thor')
    proc: Path = Path('/proc')
    store_api: str = 'https://store.steampowered.com/api/appdetails'
    # Downloads follow addresses taken from the store's reply, so they are held to Steam's own hosts.
    hosts: tuple = ('store.steampowered.com', '.steamstatic.com')
    secure: bool = True
    # The background pass starts with the frontend, often before Wi-Fi has connected.
    network_wait: float = 300
    retry_delay: float = 15

    @property
    def media(self):
        return self.applications / 'media' / 'steam'

    @property
    def gamelist(self):
        return self.applications / 'gamelist.xml'


class Unreachable(Exception):
    """The store could not be reached, as opposed to answering that it has nothing."""


def log(config, message):
    config.state.mkdir(parents=True, exist_ok=True)
    path = config.state / 'steam-library.log'
    # A small rolling log keeps a record for diagnosis without growing on the device.
    if path.exists() and path.stat().st_size > 100_000:
        path.replace(path.with_suffix('.log.old'))
    with path.open('a') as output:
        output.write(time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n')


def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def write_bytes(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.with_name(path.name + '.part')
    staged.write_bytes(payload)
    staged.replace(path)


def shortcuts(config):
    found = []
    for path in sorted(config.applications.glob('*.desktop')):
        try:
            text = path.read_text(errors='replace')
        except OSError:
            continue
        app = SHORTCUT_APP.search(text)
        # ROCKNIX's own Steam.desktop is empty, and any other launcher in the folder is not a Steam game.
        if not app:
            continue
        name = SHORTCUT_NAME.search(text)
        found.append({'path': path, 'app': app.group(1), 'name': name.group(1).strip() if name else path.stem})
    return found


def frontend_running(config):
    for entry in config.proc.glob('[0-9]*/comm'):
        try:
            if entry.read_text().strip() == 'emulationstation':
                return True
        except OSError:
            continue
    return False


def cached_art(config, app, names):
    cache = config.steam / 'appcache' / 'librarycache'
    candidates = []
    for name in names:
        candidates.extend((cache / app).rglob(name))
        candidates.append(cache / (app + '_' + name))
    candidates = [path for path in candidates if path.is_file() and path.stat().st_size]
    # Steam keeps superseded artwork in sibling folders, so the newest file is the one its library shows.
    return max(candidates, key=lambda path: path.stat().st_mtime, default=None)


def copy_cached_art(config, app):
    # Copies outlive Steam pruning its cache, and keep the game list pointing inside the folder the frontend scans.
    for target, names in (('cover.jpg', COVER_NAMES), ('hero.jpg', HERO_NAMES)):
        source = cached_art(config, app, names)
        destination = config.media / app / target
        if source and (not destination.exists() or destination.stat().st_mtime < source.stat().st_mtime):
            destination.parent.mkdir(parents=True, exist_ok=True)
            staged = destination.with_name(destination.name + '.part')
            shutil.copyfile(source, staged)
            staged.replace(destination)


def trusted(config, url):
    parts = urllib.parse.urlsplit(url)
    host = parts.hostname or ''
    if config.secure and parts.scheme != 'https':
        return False
    return any(host == allowed or (allowed.startswith('.') and host.endswith(allowed)) for allowed in config.hosts)


def read_url(config, url, limit):
    if not trusted(config, url):
        raise ValueError('Refused an address outside Steam: ' + url)
    request = urllib.request.Request(url, headers={'User-Agent': 'MultiPopThor-steam-library'})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read(limit + 1)
    except urllib.error.HTTPError as error:
        # A missing file is the store's answer; an overloaded or rate-limiting store is worth another try.
        if error.code == 429 or error.code >= 500:
            raise Unreachable(str(error)) from error
        raise ValueError(str(error) + ' for ' + url) from error
    except OSError as error:
        raise Unreachable(str(error)) from error
    if len(payload) > limit:
        raise ValueError('Larger than expected: ' + url)
    return payload


def release_date(text):
    # The store writes the date for people, as "Oct 22, 2026" or "22 Oct, 2026"; the frontend wants a timestamp.
    match = re.fullmatch(r'\s*(?:([A-Za-z]{3})[a-z]*\.? (\d{1,2})|(\d{1,2}) ([A-Za-z]{3})[a-z]*\.?),? (\d{4})\s*', text or '')
    if not match:
        return ''
    month = MONTHS.get((match.group(1) or match.group(4)).lower())
    day = int(match.group(2) or match.group(3))
    if not month or not 1 <= day <= 31:
        return ''
    return '%04d%02d%02dT000000' % (int(match.group(5)), month, day)


def store_details(config, app):
    url = config.store_api + '?' + urllib.parse.urlencode({'appids': app, 'l': 'english'})
    try:
        reply = json.loads(read_url(config, url, TEXT_BYTES)).get(app) or {}
    except ValueError as error:
        raise Unreachable('The store reply was not usable: ' + str(error)) from error
    data = reply.get('data')
    # Non-Steam shortcuts and delisted games have no store page; recording that stops a request at every start.
    if not reply.get('success') or not isinstance(data, dict):
        return {'available': False}
    screenshots = [entry.get('path_full') for entry in data.get('screenshots') or [] if entry.get('path_full')]
    trailers = [entry.get('hls_h264') for entry in data.get('movies') or [] if entry.get('hls_h264')]
    return {
        'available': True,
        'description': html.unescape(data.get('short_description') or '').strip(),
        'genre': ', '.join(entry.get('description', '') for entry in (data.get('genres') or [])[:2]),
        'developer': ', '.join(data.get('developers') or []),
        'publisher': ', '.join(data.get('publishers') or []),
        'released': release_date((data.get('release_date') or {}).get('date')),
        'header': data.get('header_image') or '',
        'screenshot': screenshots[0] if screenshots else '',
        'trailer': trailers[0] if trailers else '',
    }


def trailer_bytes(config, master_url):
    """Return the opening of a store trailer as one MP4, or None when the stream is not in a form that can be joined.

    The store publishes trailers only as HLS. Its video renditions are fragmented MP4, so the initialization segment
    followed by the media segments is itself a playable file, with no remuxing tool needed on the device. The audio is
    a separate rendition and is left out, because the preview is muted.
    """
    master = read_url(config, master_url, TEXT_BYTES).decode('utf-8', 'replace').splitlines()
    variants = []
    for number, line in enumerate(master[:-1]):
        size = re.search(r'RESOLUTION=\d+x(\d+)', line)
        if line.startswith('#EXT-X-STREAM-INF') and size and not master[number + 1].startswith('#'):
            variants.append((int(size.group(1)), master[number + 1].strip()))
    if not variants:
        return None
    enough = [variant for variant in variants if variant[0] >= TRAILER_HEIGHT]
    height, variant = min(enough) if enough else max(variants)
    variant_url = urllib.parse.urljoin(master_url, variant)
    playlist = read_url(config, variant_url, TEXT_BYTES).decode('utf-8', 'replace').splitlines()
    start = next((re.search(r'URI="([^"]+)"', line) for line in playlist if line.startswith('#EXT-X-MAP')), None)
    # Without an initialization segment the stream is MPEG-TS, and an encrypted one cannot be joined at all.
    if not start or any(line.startswith('#EXT-X-KEY') and 'METHOD=NONE' not in line for line in playlist):
        return None
    segments, seconds, duration = [], 0.0, 0.0
    for line in playlist:
        if line.startswith('#EXTINF:'):
            duration = float(re.match(r'#EXTINF:([0-9.]+)', line).group(1))
        elif line.strip() and not line.startswith('#') and seconds < TRAILER_SECONDS:
            segments.append(line.strip())
            seconds += duration
    if not segments:
        return None
    output = bytearray(read_url(config, urllib.parse.urljoin(variant_url, start.group(1)), TEXT_BYTES))
    for segment in segments:
        output += read_url(config, urllib.parse.urljoin(variant_url, segment), TRAILER_BYTES)
        if len(output) > TRAILER_BYTES:
            raise ValueError('Trailer is larger than expected: ' + master_url)
    return bytes(output)


def fetch_game(config, shortcut):
    """Download whatever this game still lacks. Returns True when something new was stored."""
    app, folder = shortcut['app'], config.media / shortcut['app']
    changed = False
    details = read_json(folder / 'details.json')
    if not isinstance(details, dict):
        details = store_details(config, app)
        write_bytes(folder / 'details.json', (json.dumps(details, indent=2) + '\n').encode())
        changed = True
    if not details.get('available'):
        return changed
    try:
        # The merge usually copies the cached cover first; doing it here too keeps a manual fetch from downloading
        # a header for a game whose cover is already on the device.
        copy_cached_art(config, app)
    except OSError as error:
        log(config, shortcut['name'] + ': cached artwork could not be copied: ' + str(error))
    wanted = [('screenshot.jpg', details.get('screenshot'))]
    # The store's wide header stands in only for a game whose portrait cover Steam has not cached.
    if not (folder / 'cover.jpg').exists():
        wanted.append(('header.jpg', details.get('header')))
    for name, url in wanted:
        if url and not (folder / name).exists():
            try:
                write_bytes(folder / name, read_url(config, url, IMAGE_BYTES))
                changed = True
            except ValueError as error:
                log(config, shortcut['name'] + ': ' + str(error))
    if details.get('trailer') and not (folder / 'trailer.mp4').exists():
        try:
            trailer = trailer_bytes(config, details['trailer'])
            if trailer:
                write_bytes(folder / 'trailer.mp4', trailer)
                changed = True
            else:
                log(config, shortcut['name'] + ': the store trailer is not in a form that can be saved.')
        except ValueError as error:
            log(config, shortcut['name'] + ': ' + str(error))
    return changed


def incomplete(config, shortcut):
    folder = config.media / shortcut['app']
    details = read_json(folder / 'details.json')
    if not isinstance(details, dict):
        return True
    if not details.get('available'):
        return False
    return bool(details.get('screenshot') and not (folder / 'screenshot.jpg').exists() or
                details.get('trailer') and not (folder / 'trailer.mp4').exists())


def fetch(config, wait=None):
    deadline = time.monotonic() + (config.network_wait if wait is None else wait)
    stored = 0
    while True:
        # Deciding from the files alone means a complete library costs no request at all.
        pending = [shortcut for shortcut in shortcuts(config) if incomplete(config, shortcut)]
        failure = None
        for shortcut in pending:
            try:
                stored += fetch_game(config, shortcut)
            except Unreachable as error:
                failure = error
                break
            except Exception as error:
                log(config, shortcut['name'] + ': ' + str(error))
        if failure is None:
            break
        if time.monotonic() + config.retry_delay > deadline:
            log(config, 'The Steam store could not be reached: ' + str(failure))
            break
        time.sleep(config.retry_delay)
    if stored:
        log(config, 'Stored new Steam store media for %d game(s); the next start shows it.' % stored)
    return stored


def set_text(game, tag, value):
    """Fill a field only when it is empty, so anything the player or a scraper entered is kept."""
    element = game.find(tag)
    if not value or (element is not None and (element.text or '').strip()):
        return
    if element is None:
        element = ET.SubElement(game, tag)
    element.text = value


def set_media(config, game, tag, app, names):
    element = game.find(tag)
    current = (element.text or '').strip() if element is not None else ''
    # A reference this script did not write was chosen by the player or a scraper and is left alone.
    if current and not current.startswith(OWNED):
        return
    chosen = next((OWNED + app + '/' + name for name in names if (config.media / app / name).is_file()), '')
    if chosen:
        if element is None:
            element = ET.SubElement(game, tag)
        element.text = chosen
    elif element is not None:
        game.remove(element)


def merge(config):
    if frontend_running(config):
        # The frontend rewrites its game lists from memory, so an edit made under it would be lost or half-read.
        log(config, 'The game list was left alone because the frontend is running.')
        return False
    found = shortcuts(config)
    if not found:
        return False
    before = None
    if config.gamelist.exists():
        before = config.gamelist.read_bytes()
        try:
            root = ET.fromstring(before)
        except ET.ParseError as error:
            log(config, 'The Steam game list could not be read and was left alone: ' + str(error))
            return False
        if root.tag != 'gameList':
            log(config, 'The Steam game list has an unexpected root and was left alone.')
            return False
    else:
        root = ET.Element('gameList')
    games = {(game.findtext('path') or '').strip(): game for game in root.findall('game')}
    for shortcut in found:
        app, reference = shortcut['app'], './' + shortcut['path'].name
        try:
            copy_cached_art(config, app)
        except OSError as error:
            log(config, shortcut['name'] + ': cached artwork could not be copied: ' + str(error))
        game = games.get(reference)
        if game is None:
            game = ET.SubElement(root, 'game')
            ET.SubElement(game, 'path').text = reference
        set_text(game, 'name', shortcut['name'])
        details = read_json(config.media / app / 'details.json')
        if isinstance(details, dict) and details.get('available'):
            for tag, key in (('desc', 'description'), ('genre', 'genre'), ('developer', 'developer'),
                             ('publisher', 'publisher'), ('releasedate', 'released')):
                set_text(game, tag, details.get(key))
        # The carousel card shows the thumbnail, and the preview well shows the image until the video starts.
        set_media(config, game, 'thumbnail', app, ('cover.jpg', 'header.jpg'))
        set_media(config, game, 'image', app, ('screenshot.jpg', 'hero.jpg'))
        set_media(config, game, 'video', app, ('trailer.mp4',))
    ET.indent(root, '\t')
    after = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
    if after == before:
        return False
    backup = config.media / 'gamelist-before-multi-pop.xml'
    if before is not None and not backup.exists():
        # One copy of the list as it stood before this script first touched it is enough to undo everything.
        write_bytes(backup, before)
    write_bytes(config.gamelist, after)
    log(config, 'Updated the Steam game list for %d shortcut(s).' % len(found))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('merge', 'fetch', 'sync'))
    args = parser.parse_args()
    config = Config()
    try:
        # Listing the folder first means a Thor without Steam never gains a media folder, log or lock.
        if not shortcuts(config):
            return 0
        config.media.mkdir(parents=True, exist_ok=True)
        # A quick restart can begin a second background pass while the first is still downloading the same files.
        # The lock is released when the process exits.
        lock = (config.media / 'process.lock').open('w')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # The offline merge only reads finished files, so it need not wait for a download to end.
            if args.command != 'merge':
                return 0
        if args.command in ('fetch', 'sync'):
            # A manual run has someone waiting on it, so it does not sit out a missing connection.
            fetch(config, wait=0 if args.command == 'sync' else None)
        if args.command in ('merge', 'sync'):
            merge(config)
    except Exception as error:
        # Startup must continue whatever happens here, so a failure is only recorded.
        try:
            log(config, args.command + ' failed: ' + str(error))
        except OSError:
            pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
