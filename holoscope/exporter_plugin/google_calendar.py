#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arrow
import json
import logging
import os.path
import pickle
import textwrap

from ..datamodel import GCalEvent
from ..datamodel import LiveEvent
from ..token_manager import TokenManager

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

log = logging.getLogger(__name__)
CALENDAR_API_SERVICE_NAME = 'calendar'
CALENDAR_API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

ISO861FORMAT = 'YYYY-MM-DDTHH:mm:ss.SSSSSS'

PAST = 7
FUTURE = 120


class Exporter(object):
    def __init__(self, config) -> None:
        token_manager = TokenManager(config, token_type='google_calendar')
        self.calendar = build(
            CALENDAR_API_SERVICE_NAME,
            CALENDAR_API_VERSION,
            credentials=token_manager._get_token()
        )
        self.calendar_id = config.google_calendar.calendar_id
        self.events = self._get_events()

    @staticmethod
    def _refresh_credential() -> Credentials:
        # Google にcalendarへのアクセストークンを要求してcredsに格納します。
        creds = None

        # 有効なトークンをすでに持っているかチェック（２回目以降の実行時に認証を省略するため）
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            # アクセストークンを要求
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # アクセストークン保存（２回目以降の実行時に認証を省略するため）
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def _get_events(self, past: int = PAST, future: int = FUTURE) -> list:
        # 指定されたカレンダーからeventを取得
        events = []
        now = arrow.utcnow()
        past = now.shift(days=-past).format(ISO861FORMAT) + 'Z'
        future = now.shift(days=future).format(ISO861FORMAT) + 'Z'
        try:
            # Call the Calendar API
            responses = self.calendar.events().list(calendarId=self.calendar_id,
                                                    timeMin=(past),
                                                    timeMax=(future),
                                                    maxResults=250, singleEvents=True,
                                                    orderBy='startTime').execute()
            responses = responses.get('items', [])
            if not responses:
                log.error('Upcomming events was not found.')
                return events
            log.debug('CALENDAR EVENT JSON DUMP')
            log.debug(json.dumps(responses))
            for resp in responses:
                events.append(GCalEvent(resp))
                log.info(f'Schedule found {events[-1].title}.')
            return events
        except HttpError as error:
            log.error(f'An error occurred: {error}.')

    def create_event(self, live_events: list) -> None:
        for live_event in live_events:
            title_str = f'{live_event.channel_title}: {live_event.title}'
            body = {
                # 予定のタイトル
                'summary': f'{title_str}',
                'description':
                textwrap.dedent(f'''
                 チャンネル: {live_event.channel_title}
                 タイトル: {live_event.title}

                  配信URL: https://www.youtube.com/watch?v={live_event.id}
                '''),
                # 予定の開始時刻
                'start': {
                    'dateTime': live_event.begin.format(ISO861FORMAT) + 'Z',
                    'timeZone': 'Japan'
                },
                # 予定の終了時刻
                'end': {
                    'dateTime': live_event.begin.shift(hours=+1).format(ISO861FORMAT) + 'Z',
                    'timeZone': 'Japan'
                },
            }
            if (event := [event for event in self.events if live_event.id == event.video_id]):
                event = event[0]
                if title_str == event.title:
                    if live_event.begin.to('Asia/Tokyo') == event.begin:
                        log.info(f'{live_event.title} is already scheduled.')
                        continue
                self._update_event(event.id, live_event)
                log.info(f'Update the scheduled {live_event.title}.')
            else:
                if live_event.begin > arrow.utcnow().shift(days=FUTURE):
                    log.info(f'{title_str} was not scheduled, ' +
                             f'because it is {FUTURE} days away.')
                    continue
                event = self.calendar.events().insert(calendarId=self.calendar_id,
                                                      body=body).execute()
                log.info(f'Create {title_str} has been scheduled.')

    def _update_event(self, event_id: str, live_event: LiveEvent):
        title_str = f'{live_event.channel_title}: {live_event.title}'
        body = {
            # 予定のタイトル
            'summary': f'{title_str}',
            'description':
            textwrap.dedent(f'''
             チャンネル: {live_event.channel_title}
             タイトル: {live_event.title}

              配信URL: https://www.youtube.com/watch?v={live_event.id}
            '''),
            # 予定の開始時刻
            'start': {
                'dateTime': live_event.begin.format(ISO861FORMAT) + 'Z',
                'timeZone': 'Japan'
            },
            # 予定の終了時刻
            'end': {
                'dateTime': live_event.begin.shift(hours=+1).format(ISO861FORMAT) + 'Z',
                'timeZone': 'Japan'
            },
        }
        self.calendar.events().update(calendarId=self.calendar_id,
                                      eventId=event_id,
                                      body=body).execute()
