#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arrow

from dataclasses import dataclass
from typing import List
from typing import Optional
from urlextract import URLExtract
from urllib.parse import urlparse


class LiveEvent():
    def __init__(self, data) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def title(self) -> str:
        return self._data['snippet']['title']

    @property
    def begin(self) -> str:
        begin = self._data['liveStreamingDetails']['scheduledStartTime']
        return arrow.get(begin)

    @property
    def channel_id(self) -> str:
        return self._data['snippet']['channelId']

    @property
    def channel_title(self) -> str:
        return self._data['snippet']['channelTitle']


class GCalEvent():
    def __init__(self, data) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def title(self) -> str:
        return self._data['summary']

    @property
    def begin(self) -> str:
        begin = self._data['start']['dateTime']
        return arrow.get(begin)

    @property
    def link(self) -> str:
        return self._data['htmlLink']

    @property
    def calid(self) -> str:
        return self._data['organizer']['email']

    @property
    def description(self) -> str:
        return self._data['description']

    @property
    def video_id(self) -> str:
        for url in URLExtract().find_urls(self.description):
            url = urlparse(url)
            if 'youtube.com' in url.netloc or 'youtu.be' in url.netloc:
                return url.query.split('=')[1]


@dataclass
class GeneralConfiguration:
    loglevel: Optional[str] = None
    logdir: Optional[str] = None
    logfile: Optional[str] = None
    importer_plugin: Optional[str] = 'config'
    exporter_plugin: Optional[str] = 'google_calendar'


@dataclass
class GoogleCalendarConfiguration:
    calendar_id: str


@dataclass
class YoutubeConfiguration:
    api_key: str
    channel_ids: Optional[List[str]] = None


@dataclass
class AwsConfiguration:
    kms_key_id: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    dynamodb_table: Optional[str] = 'holoscope'
    dynamodb_hash_key_name: Optional[str] = 'hashKey'


@dataclass
class Configuration:
    general: Optional[GeneralConfiguration] = None
    google_calendar: Optional[GoogleCalendarConfiguration] = None
    youtube: Optional[YoutubeConfiguration] = None
    aws: Optional[AwsConfiguration] = None
