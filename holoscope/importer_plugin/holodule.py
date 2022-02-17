#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import imagehash
# import io
import json
import logging
import requests
import socket
# import urllib.request

from bs4 import BeautifulSoup
# from PIL import Image
from urllib.parse import urlparse

from ..datamodel import LiveEvent
from ..thumbnail_cache_manager import ThumbnailCacheManager
from ..utils import YoutubeUtils

log = logging.getLogger(__name__)
timeout_in_sec = 5
socket.setdefaulttimeout(timeout_in_sec)


class Importer(object):
    def __init__(self, config, youtube_instance):
        self.cnf = config
        self.youtube = youtube_instance
        self.live_events = self._get_live_events()

    def _deduplicate_live_events(self, events) -> list:
        primary_events = [{event.actor: event} for event in events if not event.collaborate]
        collaborate_events = [{event.collaborate: event} for event in events if event.collaborate]
        for i in self.cnf.holodule.holomenbers:
            for y, ce in enumerate([x[i] for x in collaborate_events if x.get(i)]):
                for pe in [x[i] for x in primary_events if x.get(i)]:
                    if ce.begin == pe.begin:
                        collaborate_events.pop(y)
                        log.info(f'{ce.title} was deleted because duplicate event.')
                        break
        return [i.values() for i in primary_events] + [j.values() for j in primary_events]

    def _get_live_events(self) -> list:
        events = []
        programs = []
        thumbnail_hash = {}
        youtube_utils = YoutubeUtils(self.youtube)
        all_programs = self._get_programs(youtube_utils)
        for program in all_programs:
            thumbnail_hash[program.get('actor')] = {'holodule_url': program.get('img')}
        thumbnail_cache_manager = ThumbnailCacheManager(self.cnf, self.youtube, thumbnail_hash)
        thumbnail_cache = thumbnail_cache_manager.get_thumbnail_cache()

        for program in all_programs:
            for i in self.cnf.holodule.holomenbers:
                if i == program.get('actor'):
                    program['collaborate'] = None
                    programs.append(program)
                elif thumbnail_cache[i].get('holodule_url') in program['collaborators']:
                    program['collaborate'] = i
                    programs.append(program)
                # else:
                #     for collaborator in program['collaborators']:
                #         img_read = urllib.request.urlopen(collaborator).read()
                #         img_bin = io.BytesIO(img_read)
                #         img_hash = imagehash.average_hash(Image.open(img_bin))
                #         if (imagehash.hex_to_hash(thumbnail_cache[i]['youtube_img_hash']) - img_hash) < 4:
                #             program['collaborate'] = i
                #             programs.append(program)

        video_ids = [program.get('video_id') for program in programs]
        if len(video_ids) > 50:
            i = 0
            video_ids_list = [video_ids[:50], video_ids[50:]]
            for video_ids in video_ids_list:
                responses = youtube_utils.get_live_event(video_ids)
                log.debug('LIVE EVENT JSON DUMP')
                log.debug(json.dumps(responses))
                for resp in responses:
                    try:
                        resp['liveStreamingDetails']['scheduledStartTime']
                    except KeyError:
                        continue
                    events.append(LiveEvent(resp, programs[i].get('actor'),
                                            programs[i].get('collaborate')))
                    log.info(f'Live event found [{events[-1].id}] {events[-1].channel_title}:' +
                             f'{events[-1].title}.')
                    i = i + 1
        else:
            responses = youtube_utils.get_live_event(video_ids)
            log.debug('LIVE EVENT JSON DUMP')
            log.debug(json.dumps(responses))
            for j, resp in enumerate(responses):
                try:
                    resp['liveStreamingDetails']['scheduledStartTime']
                except KeyError:
                    continue
                events.append(LiveEvent(resp, programs[j].get('actor'),
                                        programs[j].get('collaborate')))
                log.info(f'Live event found [{events[-1].id}] {events[-1].channel_title}:' +
                         f'{events[-1].title}.')
        return self._deduplicate_live_events(events)

    def _get_programs(self, youtube_utils) -> list:
        programs = []
        r = requests.get(self.cnf.holodule.holodule_url, timeout=(3.0, 7.5))
        soup = BeautifulSoup(r.text, 'html.parser')
        divs = soup.find_all('div', class_="col-6 col-sm-4 col-md-3")
        for div in divs:
            a = div.find('a')
            url = urlparse(a.get("href"))
            if 'youtube.com' not in url.netloc and 'youtu.be' not in url.netloc:
                continue
            s = a.find('div', class_="col text-right name").get_text()
            actor = '\n'.join(filter(lambda x: x.strip(),
                                     s.replace(" ", "").split('\r\n')))
            if actor == 'ラプラス':
                actor = 'ラプラス・ダークネス'
            if actor == 'アキロゼ':
                actor = 'アキ・ローゼンタール'
            s_img = a.find('div', class_="col col-sm col-md col-lg col-xl").find('img').attrs['src']
            imgs = a.find_all('div', class_="col col-sm col-md col-lg col-xl")
            collaborators = [
                        i.find('img').attrs['src']
                        for i in imgs
                        if i.find('img').attrs['src'] != s_img
                        ]
            video_id = url.query.split('=')[1]
            result = {'actor': actor,
                      'collaborators': collaborators,
                      'video_id': video_id,
                      'img': s_img}
            programs.append(result)
        return programs
