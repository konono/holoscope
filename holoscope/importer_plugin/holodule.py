#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import imagehash
# import io
import itertools
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
        primary_events = [{e.actor: e} for e in events if not e.collaborate]
        collaborate_events = [{collabo: e} for e in events if e.collaborate for collabo in e.collaborate]
        delete_items = []
        ''' ホロメンのリストと、コラボ予定のeventsでループを回し、
            推しの配信予定とコラボ予定の時間が重複していた場合はdelete_itemsに追加
        '''
        for i in self.cnf.holodule.holomenbers:
            for y, ce in enumerate(collaborate_events):
                if ce.get(i):
                    for pe in [x[i] for x in primary_events if x.get(i)]:
                        if ce[i].scheduled_start_time == pe.scheduled_start_time:
                            delete_items.append(ce.get(i))
                            log.info(f'{ce[i].title} was deleted because duplicate event.')
                            break
        # primary_eventsとcollaborate_eventsを二次元配列にした後、flattenする
        events = list(itertools.chain.from_iterable(([list(i.values()) for i in primary_events]
                                                    + [list(j.values()) for j in collaborate_events])))
        # delete_itemsにあるオブジェクトがeventsの中にあれば削除する
        for d in delete_items:
            events = [event for event in events if event != d]

        # コラボレーターが複数人いる場合にeventが重複するので、重複しているイベントがあれば削除
        return list(set(events))

    def _get_live_events(self) -> list:
        events = []
        programs = []
        thumbnail_hash = {}
        youtube_utils = YoutubeUtils(self.youtube)
        all_programs = self._get_programs()
        for program in all_programs:
            thumbnail_hash[program.get('actor')] = {'holodule_url': program.get('img')}
        thumbnail_cache_manager = ThumbnailCacheManager(self.cnf, self.youtube, thumbnail_hash)
        thumbnail_cache = thumbnail_cache_manager.get_thumbnail_cache()
        # 配信予定でループして、actorが一致したらbreak、コラボ予定であればcollaboratorsを追加
        for program in all_programs:
            # for i in self.cnf.holodule.holomenbers:
            for holomen in thumbnail_cache:
                if program.get('actor') in self.cnf.holodule.holomenbers:
                    program['collaborate'] = []
                    programs.append(program)
                    break
                # キャッシュに入ってる推しのサムネイルのURLとコラボレーターの中に入っていたサムネイルのURLが一致したらコラボ配信と判定
                if thumbnail_cache[holomen].get('holodule_url') in program['collaborators']:
                    program['collaborate'].append(holomen)
                if holomen in self.cnf.holodule.holomenbers:
                    if holomen in program['collaborate']:
                        programs.append(program)
        # 同一のprogramがlist内にあった場合削除
        programs = list(map(json.loads, set(map(json.dumps, programs))))
        log.debug(f'Contents filtered by favorite: {programs}')
        video_ids = [program.get('video_id') for program in programs]
        log.debug(f'Contents filtered by favorite video_ids: {video_ids}')
        if len(video_ids) > 50:
            i = 0
            video_ids_list = [video_ids[:50], video_ids[50:]]
            for video_ids in video_ids_list:
                responses = youtube_utils.get_live_events(video_ids)
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
            responses = youtube_utils.get_live_events(video_ids)
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

    def _get_programs(self) -> list:
        programs = []
        r = requests.get(self.cnf.holodule.holodule_url, timeout=(3.0, 7.5))
        soup = BeautifulSoup(r.text, 'html.parser')
        divs = soup.find_all('div', class_="col-6 col-sm-4 col-md-3")
        for div in divs:
            a = div.find('a')
            url = urlparse(a.get("href"))
            if ('youtube.com' not in url.netloc and 'youtu.be' not in url.netloc) or '/watch' != url.path:
                continue
            s = a.find('div', class_="col text-right name").get_text()
            actor = '\n'.join(filter(lambda x: x.strip(),
                                     s.replace(" ", "").split('\n')))
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
                      'img': s_img,
                      'collaborate': []}
            programs.append(result)
            log.debug(f'Get contents from holodule: {result}')
        return programs
