# coding: utf-8
from __future__ import unicode_literals

from ..utils import (
    int_or_none,
)
import re
from .common import InfoExtractor
from .openload import PhantomJSwrapper


def extract_season_episode (self, title):
    season = self._search_regex(
        r'Season[ -_]*(?P<season>\d+)',
        title, 'season', group='season', fatal=False
    )

    episode = self._search_regex(
        r'Episode[ -_]*(?P<episode>\d+)',
        title, 'episode', group='episode', fatal=False
    )

    return (int_or_none(season), int_or_none(episode))

class TWCIE(InfoExtractor):
    IE_NAME = 'The Watch Cartoon Online'
    BASE_URL = 'https://www.thewatchcartoononline.tv'
    _VALID_URL = r'^https?://(www\.)?thewatchcartoononline\.tv/(?P<id>[a-z0-9-]+)$'
    _TEST = {
        'url': 'https://www.thewatchcartoononline.tv/the-legend-of-korra-season-3-episode-12-enter-the-void-2',
        'info_dict': {
            'id': 'the-legend-of-korra-season-3-episode-12-enter-the-void-2',
            'title': 'md5:05712247fe2699cfb6c77a77cacf7916',
            'ext': 'mp4',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage('https://thewatchcartoononline.tv/%s' % video_id, video_id)

        obfu = self._search_regex(
            r'<script>(?P<obfu>.+decodeURIComponent.+)</script>',
            webpage, 'obfu')

        phantom = PhantomJSwrapper(self, required_version='2.0')
        iframe_url = phantom.eval('''
          %s;
          return document.getElementsByTagName('iframe')[0].src
        ''' % obfu, video_id, note='Deobfuscating')

        iframe = self._download_webpage(self.BASE_URL + iframe_url, video_id, headers={
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'referrer': 'https://www.thewatchcartoononline.tv/anime/',
        })

        api = self._search_regex(
            r'getJSON\(\"(?P<url>[/a-z0-9-.?=A-Z%&]+)\"',
            iframe, 'url')

        json = self._download_json(self.BASE_URL + api, video_id, headers={
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'referrer': self.BASE_URL + api,
        })

        formats = []

        headers = {
            'accept': '*/*',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'range': 'bytes=0-',
            'sec-fetch-dest': 'video',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'referrer': self.BASE_URL + api,
        }

        if 'hd' in json and json.get('hd') != '':
            formats.append({
                'format_id': 'hd',
                'url': json.get('server') + '/getvid?evid=' + json.get('hd'),
                'width': 1080,
                'ext': 'mp4',
                'http_headers': headers,
            })

        formats.append({
            'format_id': 'sd',
            'url': json.get('server') + '/getvid?evid=' + json.get('enc'),
            'ext': 'mp4',
            'http_headers': headers,
        })

        self._sort_formats(formats)

        title = self._search_regex(
            r'<title>Watch (?P<title>.+)<\/title>',
            webpage, 'title', group='title')

        (series, seriesname) = self._search_regex(
            r'href="(?P<series>.+)" rel="category tag">(?P<seriesname>.+)</a>',
            webpage, 'series', group=('series', 'seriesname'), fatal=False
        )

        (season, episode) = extract_season_episode(self, title)

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'headers': headers,
            'series': series,
            'series_title': seriesname,
            'season_number': season,
            'episode_number': episode
        }

class TWCSeriesIE(InfoExtractor):
    IE_NAME = 'The Watch Cartoon Online Series'
    BASE_URL = 'https://www.thewatchcartoononline.tv/anime'
    _VALID_URL = r'^https?://(www\.)?thewatchcartoononline\.tv/anime/(?P<id>[a-z0-9-]+)$'
    _TEST = {
        'url': 'https://www.thewatchcartoononline.tv/anime/the-legend-of-korra',
        'playlist_mincount': 10,
        'info_dict': {
            'id': 'the-legend-of-korra',
            'title': 'md5:2350b947e7442d8c89a5cf8956bbf7ed',
            'description': 'md5:6f42d929c2ba6504984ac04c468d92a5',
        },
    }

    def _real_extract(self, url):
        anime_id = self._match_id(url)
        webpage = self._download_webpage('https://thewatchcartoononline.tv/anime/%s' % anime_id, anime_id)

        title = self._search_regex(
            r'h1-tag"><a href=".+">(?P<title>.+)</a></div>',
            webpage, 'title', group='title', fatal=False
        )

        description = self._search_regex(
            r'</h3>\n\n<p>(?P<description>.+)</p>',
            webpage, 'description', group='description', fatal=False
        )

        return self.playlist_result(tuple(self.url_result(
                match.group('url'), ie=TWCIE.ie_key(),
                video_id=TWCIE._match_id(match.group('url')),
                video_title=match.group('title')
            )
            for match in re.finditer(r'<a href="(?P<url>.+)" rel="bookmark" title=".+" class="sonra">(?P<title>.+)</a>', webpage)
        ), playlist_id=anime_id, playlist_title=title, playlist_description=description)
