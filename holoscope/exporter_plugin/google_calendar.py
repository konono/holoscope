#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arrow
import logging
import re
import socket

from .. import utils
from ..utils import GoogleCalendarUtils

log = logging.getLogger(__name__)
timeout_in_sec = 5
socket.setdefaulttimeout(timeout_in_sec)

CALENDAR_API_SERVICE_NAME = 'calendar'
CALENDAR_API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']
TZ = "Asia/Tokyo"
ISO861FORMAT = 'YYYY-MM-DDTHH:mm:ss.SSSSSS'
LINEFORMAT = 'YYYY/MM/DD HH:mm:ss'
COLLAB_PATTERN = re.compile(r'^\[(.*?)\]')
FUTURE = 120


class Exporter(object):
    def __init__(self, config) -> None:
        self.holomenbers = config.holodule.holomenbers
        self.google_calendar = GoogleCalendarUtils(config)
        self.events = self.google_calendar.get_events()

    def create_event(self, live_events: list) -> None:
        for live_event in live_events:
            self.process_live_event(live_event)

    def process_live_event(self, live_event):
        event = self.find_event(live_event)
        title = utils.create_title(live_event)

        log.info(f'[{live_event.id}] ### Processing {live_event.title}.')
        if event:
            self.update_event_if_needed(event, live_event, title)
        else:
            self.create_event_if_possible(live_event, title)

    def find_event(self, live_event):
        return next((event for event in self.events if live_event.id == event.video_id), None)

    def update_event_if_needed(self, event, live_event, title):
        should_notify = False

        if title != event.title:
            self.google_calendar.update_event(event.id, live_event)
            log.info(f'[{live_event.id}] [UPDATE]: [{event.id}] ' +
                     f'Update title {live_event.title}.')
            should_notify = True

        if (live_event.actual_start_time and
                live_event.actual_start_time.to(TZ) != event.start_dateTime):
            self.google_calendar.update_event(event.id, live_event)
            log.info(f'[{live_event.id}] [UPDATE]: [{event.id}] ' +
                     f'Update to actual start_dateTime {live_event.title}.')
            if not event.actual_start_time:
                should_notify = True

        if (not live_event.actual_start_time and
                live_event.scheduled_start_time.to(TZ) != event.start_dateTime):
            self.google_calendar.update_event(event.id, live_event)
            log.info(f'[{live_event.id}] [UPDATE]: [{event.id}] ' +
                     f'Update to scheduled start_dateTime {live_event.title}.')
            should_notify = True

        if live_event.scheduled_start_time.to(TZ) > arrow.utcnow().to(TZ):
            if (live_event.scheduled_start_time.to(TZ) - arrow.utcnow().to(TZ)).seconds <= 900:
                should_notify = True

        if (live_event.actual_end_time and
                live_event.actual_end_time.to(TZ) != event.end_dateTime):
            self.google_calendar.update_event(event.id, live_event)
            log.info(f'[{live_event.id}] [UPDATE]: [{event.id}] ' +
                     f'Update to actual end_dateTime {live_event.title}.')
            if not event.actual_end_time:
                should_notify = True

        if not should_notify:
            log.info(f'[{live_event.id}] [ALREADY_EXIST]: [{event.id}] ' +
                     f'{live_event.title} is already scheduled.')

    def create_event_if_possible(self, live_event, title):
        if live_event.scheduled_start_time > arrow.utcnow().shift(days=FUTURE):
            log.info(f'[{live_event.id}]: {title} was not scheduled, ' +
                     f'because it is {FUTURE} days away.')
            return

        created_event = self.google_calendar.create_event(live_event)
        log.info(f'[{live_event.id}] [CREATE]: [{created_event.get("id")}] ' +
                 f'Create {title} has been scheduled.')

    def delete_duplicate_event(self, live_events: list):
        for member in self.holomenbers:
            for live_event in live_events:
                if live_event.collaborate or live_event.actor != member:
                    continue
                for event in self.events:
                    collaborater = self._get_collabo_title(event.title)
                    if not collaborater or member not in collaborater:
                        continue
                    if event.scheduled_start_time == live_event.scheduled_start_time:
                        self.google_calendar.delete_event(event.id, live_event)
                        log.info(f'[{live_event.id}] [DELETE] [{event.id}] ' +
                                 f'was deleted because of duplicate {event.title}.')

    def _get_collabo_title(self, title: str) -> str:
        match = COLLAB_PATTERN.search(title)
        if match:
            collabo_title = match.group(1)
            collaborater = collabo_title.split()
            collaborater.remove('コラボ')
            return collaborater
        return ''
