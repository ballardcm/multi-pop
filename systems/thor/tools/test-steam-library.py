#!/usr/bin/env python3
"""Exercise the Steam library artwork script against a local stand-in for the Steam store."""

import http.server
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('steam_library', ROOT / 'multi-pop-thor/scripts/steam_library.py')
steam_library = importlib.util.module_from_spec(spec)
spec.loader.exec_module(steam_library)

APP = '3259780'
SEGMENTS = 25


class Store(http.server.BaseHTTPRequestHandler):
    """Serve one game's store page, pictures and an HLS trailer, and count what is asked for."""

    requests = []
    available = True
    broken = False

    def log_message(self, *args):
        pass

    def do_GET(self):
        Store.requests.append(self.path)
        base = 'http://127.0.0.1:%d' % self.server.server_port
        path = self.path.split('?')[0]
        if Store.broken:
            self.send_error(503)
            return
        if path == '/api/appdetails':
            app = self.path.split('appids=')[1].split('&')[0]
            data = {
                'short_description': 'Pixel&#8209;art &amp; fate.',
                'genres': [{'description': 'RPG'}, {'description': 'Adventure'}, {'description': 'Indie'}],
                'developers': ['Studio One', 'Studio Two'],
                'publishers': ['Publisher'],
                'release_date': {'date': 'Oct 22, 2026'},
                'header_image': base + '/header.jpg?t=1',
                'screenshots': [{'path_full': base + '/shot-1.jpg?t=1'}, {'path_full': base + '/shot-2.jpg'}],
                'movies': [{'hls_h264': base + '/trailer/master.m3u8?t=1'}],
            }
            body = json.dumps({app: {'success': Store.available and app == APP, 'data': data}}).encode()
        elif path == '/trailer/master.m3u8':
            body = ('#EXTM3U\n'
                    '#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",URI="audio.m3u8"\n'
                    '#EXT-X-STREAM-INF:BANDWIDTH=5800000,RESOLUTION=1920x1080,AUDIO="audio"\n1080.m3u8\n'
                    '#EXT-X-STREAM-INF:BANDWIDTH=2600000,RESOLUTION=1280x720,AUDIO="audio"\n720.m3u8\n'
                    '#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=854x480,AUDIO="audio"\n480.m3u8\n').encode()
        elif path.startswith('/trailer/') and path.endswith('.m3u8'):
            size = path.rsplit('/', 1)[1][:-5]
            lines = ['#EXTM3U', '#EXT-X-TARGETDURATION:3', '#EXT-X-MAP:URI="parts/%s-init.m4s"' % size]
            for number in range(SEGMENTS):
                lines += ['#EXTINF:3', 'parts/%s-%02d.m4s' % (size, number)]
            body = ('\n'.join(lines) + '\n#EXT-X-ENDLIST\n').encode()
        elif path.startswith('/trailer/parts/') or path.endswith('.jpg'):
            body = ('<' + path.rsplit('/', 1)[1] + '>').encode()
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class SteamLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Store)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        Store.requests, Store.available, Store.broken = [], True, False
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.config = steam_library.Config(
            applications=root / 'applications', steam=root / 'Steam', state=root / 'state', proc=root / 'proc',
            store_api='http://127.0.0.1:%d/api/appdetails' % self.server.server_port,
            hosts=('127.0.0.1',), secure=False, network_wait=0, retry_delay=0)
        self.config.applications.mkdir()
        self.shortcut('Final Game', APP)
        # ROCKNIX's own launcher is an empty file, and other launchers share the folder; neither is a Steam game.
        (self.config.applications / 'Steam.desktop').write_text('')
        (self.config.applications / 'Other.desktop').write_text('[Desktop Entry]\nName=Other\nExec=other --run\n')
        self.media = self.config.media / APP

    def shortcut(self, name, app):
        (self.config.applications / (name + '.desktop')).write_text(
            '[Desktop Entry]\nName=' + name + '\nComment=Play this game on Steam\n'
            'Exec=steam steam://rungameid/' + app + '\nIcon=steam_icon_' + app + '\nType=Application\n')

    def cache(self, relative, text):
        path = self.config.steam / 'appcache/librarycache' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def games(self):
        root = ET.parse(self.config.gamelist).getroot()
        return {game.findtext('path'): {child.tag: child.text for child in game} for game in root.findall('game')}

    def test_merge_uses_only_what_steam_cached(self):
        self.cache(APP + '/aaaa/library_capsule.jpg', 'cover')
        self.cache(APP + '/bbbb/library_hero.jpg', 'hero')
        self.assertTrue(steam_library.merge(self.config))
        self.assertEqual(Store.requests, [])
        self.assertEqual(self.games(), {'./Final Game.desktop': {
            'path': './Final Game.desktop', 'name': 'Final Game',
            'thumbnail': './media/steam/' + APP + '/cover.jpg', 'image': './media/steam/' + APP + '/hero.jpg'}})
        self.assertEqual((self.media / 'cover.jpg').read_text(), 'cover')
        # A second start with nothing new leaves the file untouched.
        written = self.config.gamelist.stat().st_mtime_ns
        self.assertFalse(steam_library.merge(self.config))
        self.assertEqual(self.config.gamelist.stat().st_mtime_ns, written)

    def test_older_flat_cache_layout(self):
        self.cache(APP + '_library_600x900.jpg', 'flat cover')
        steam_library.merge(self.config)
        self.assertEqual((self.media / 'cover.jpg').read_text(), 'flat cover')

    def test_fetch_then_merge_adds_store_details_screenshot_and_trailer(self):
        self.cache(APP + '/aaaa/library_capsule.jpg', 'cover')
        self.cache(APP + '/bbbb/library_hero.jpg', 'hero')
        steam_library.merge(self.config)
        self.assertEqual(steam_library.fetch(self.config), 1)
        steam_library.merge(self.config)
        game = self.games()['./Final Game.desktop']
        self.assertEqual(game['desc'], 'Pixel‑art & fate.')
        self.assertEqual(game['genre'], 'RPG, Adventure')
        self.assertEqual(game['developer'], 'Studio One, Studio Two')
        self.assertEqual(game['publisher'], 'Publisher')
        self.assertEqual(game['releasedate'], '20261022T000000')
        self.assertEqual(game['thumbnail'], './media/steam/' + APP + '/cover.jpg')
        # The gameplay screenshot replaces the hero this script chose before the store was reachable.
        self.assertEqual(game['image'], './media/steam/' + APP + '/screenshot.jpg')
        self.assertEqual(game['video'], './media/steam/' + APP + '/trailer.mp4')
        self.assertEqual((self.media / 'screenshot.jpg').read_text(), '<shot-1.jpg>')
        # The 720-line rendition is the smallest that fills the preview, and one minute is twenty 3-second segments.
        expected = '<720-init.m4s>' + ''.join('<720-%02d.m4s>' % number for number in range(20))
        self.assertEqual((self.media / 'trailer.mp4').read_text(), expected)
        # The cached cover made the store's header unnecessary.
        self.assertFalse((self.media / 'header.jpg').exists())
        # A complete game costs no further request.
        Store.requests.clear()
        self.assertEqual(steam_library.fetch(self.config), 0)
        self.assertEqual(Store.requests, [])

    def test_store_header_stands_in_for_a_missing_cover(self):
        steam_library.fetch(self.config)
        steam_library.merge(self.config)
        self.assertEqual(self.games()['./Final Game.desktop']['thumbnail'], './media/steam/' + APP + '/header.jpg')

    def test_existing_entries_and_player_choices_are_kept(self):
        original = ('<?xml version="1.0"?>\n<gameList>\n'
                    '\t<game><path>./Other.desktop</path><name>Other</name><favorite>true</favorite></game>\n'
                    '\t<game id="7"><path>./Final Game.desktop</path><name>My Name</name><desc>My words</desc>'
                    '<image>./images/mine.png</image><playcount>3</playcount></game>\n</gameList>\n')
        self.config.gamelist.write_text(original)
        self.cache(APP + '/aaaa/library_capsule.jpg', 'cover')
        steam_library.fetch(self.config)
        steam_library.merge(self.config)
        games = self.games()
        self.assertEqual(games['./Other.desktop'], {'path': './Other.desktop', 'name': 'Other', 'favorite': 'true'})
        game = games['./Final Game.desktop']
        self.assertEqual((game['name'], game['desc'], game['image'], game['playcount']),
                         ('My Name', 'My words', './images/mine.png', '3'))
        self.assertEqual(game['genre'], 'RPG, Adventure')
        self.assertEqual(game['video'], './media/steam/' + APP + '/trailer.mp4')
        self.assertEqual(ET.parse(self.config.gamelist).getroot().findall('game')[1].get('id'), '7')
        self.assertEqual((self.config.media / 'gamelist-before-multi-pop.xml').read_text(), original)

    def test_media_that_disappears_is_no_longer_referenced(self):
        self.cache(APP + '/aaaa/library_capsule.jpg', 'cover')
        steam_library.merge(self.config)
        (self.media / 'cover.jpg').unlink()
        (self.config.steam / 'appcache/librarycache' / APP / 'aaaa/library_capsule.jpg').unlink()
        steam_library.merge(self.config)
        self.assertNotIn('thumbnail', self.games()['./Final Game.desktop'])

    def test_running_frontend_and_unreadable_list_are_left_alone(self):
        process = self.config.proc / '321'
        process.mkdir(parents=True)
        (process / 'comm').write_text('emulationstation\n')
        self.assertFalse(steam_library.merge(self.config))
        self.assertFalse(self.config.gamelist.exists())
        (process / 'comm').write_text('bash\n')
        self.config.gamelist.write_text('<gameList><game>')
        self.assertFalse(steam_library.merge(self.config))
        self.assertEqual(self.config.gamelist.read_text(), '<gameList><game>')

    def test_game_without_store_page_is_asked_about_once(self):
        Store.available = False
        self.assertEqual(steam_library.fetch(self.config), 1)
        self.assertEqual(json.loads((self.media / 'details.json').read_text()), {'available': False})
        Store.requests.clear()
        steam_library.fetch(self.config)
        self.assertEqual(Store.requests, [])
        steam_library.merge(self.config)
        self.assertEqual(self.games()['./Final Game.desktop'], {'path': './Final Game.desktop', 'name': 'Final Game'})

    def test_unreachable_store_is_tried_again_later(self):
        Store.broken = True
        self.assertEqual(steam_library.fetch(self.config), 0)
        self.assertFalse((self.media / 'details.json').exists())
        self.assertIn('could not be reached', (self.config.state / 'steam-library.log').read_text())
        Store.broken = False
        self.assertEqual(steam_library.fetch(self.config), 1)
        self.assertTrue((self.media / 'trailer.mp4').exists())

    def test_addresses_outside_steam_are_refused(self):
        real = steam_library.Config()
        self.assertTrue(steam_library.trusted(real, 'https://shared.akamai.steamstatic.com/a.jpg'))
        self.assertTrue(steam_library.trusted(real, 'https://store.steampowered.com/api/appdetails?appids=1'))
        for url in ('http://shared.akamai.steamstatic.com/a.jpg', 'https://steamstatic.com.example.org/a.jpg',
                    'https://example.org/steamstatic.com/a.jpg', 'file:///etc/passwd'):
            self.assertFalse(steam_library.trusted(real, url), url)
        self.assertRaises(ValueError, steam_library.read_url, real, 'https://example.org/a.jpg', 10)

    def test_release_dates(self):
        for text, expected in (('Oct 22, 2026', '20261022T000000'), ('22 Oct, 2026', '20261022T000000'),
                               ('3 March, 2025', '20250303T000000'), ('Coming soon', ''), ('Q4 2026', ''), (None, '')):
            self.assertEqual(steam_library.release_date(text), expected, text)

    def test_folder_without_steam_shortcuts_is_untouched(self):
        (self.config.applications / 'Final Game.desktop').unlink()
        self.assertFalse(steam_library.merge(self.config))
        self.assertEqual(steam_library.fetch(self.config), 0)
        self.assertFalse(self.config.gamelist.exists())
        self.assertFalse(self.config.media.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
