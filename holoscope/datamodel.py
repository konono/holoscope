#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arrow
import re

from arrow.arrow import Arrow
from dataclasses import dataclass
from typing import List
from typing import Optional
from urllib.parse import urlparse


class LiveEvent():
    def __init__(self, data, actor, collaborate) -> None:
        self._data = data
        self._actor = actor
        self._collaborate = collaborate

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def title(self) -> str:
        return self._data['snippet']['title']

    @property
    def actual_start_time(self) -> Optional[Arrow]:
        try:
            actual_start_time = arrow.get(self._data['liveStreamingDetails']['actualStartTime'])
        except KeyError:
            actual_start_time = None
        return actual_start_time

    @property
    def scheduled_start_time(self) -> Optional[Arrow]:
        return arrow.get(self._data['liveStreamingDetails']['scheduledStartTime'])

    @property
    def channel_id(self) -> str:
        return self._data['snippet']['channelId']

    @property
    def channel_title(self) -> str:
        return self._data['snippet']['channelTitle']

    @property
    def actor(self) -> str:
        return self._actor

    @property
    def collaborate(self) -> Optional[str]:
        return self._collaborate


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
    def start_time(self) -> str:
        start_time = self._data['start']['dateTime']
        return arrow.get(start_time)

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
        url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"  # noqa: W605
        for url in re.findall(url_pattern, self.description):
            url = urlparse(url)
            if 'youtube.com' in url.netloc or 'youtu.be' in url.netloc:
                return url.query.split('=')[1]


@dataclass
class AwsConfiguration:
    kms_key_id: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    dynamodb_table: Optional[str] = 'holoscope'
    dynamodb_hash_key_name: Optional[str] = 'hashKey'


@dataclass
class GeneralConfiguration:
    loglevel: Optional[str] = None
    logdir: Optional[str] = None
    logfile: Optional[str] = None
    importer_plugin: Optional[str] = 'holodule'
    exporter_plugin: Optional[str] = 'google_calendar'


@dataclass
class GoogleCalendarConfiguration:
    calendar_id: str


@dataclass
class HoloduleConfiguration:
    holomenbers: List[str]
    holodule_url: Optional[str] = 'https://schedule.hololive.tv/simple'


@dataclass
class YoutubeConfiguration:
    api_key: str
    channel_ids: Optional[List[str]] = None


@dataclass
class Configuration:
    aws: Optional[AwsConfiguration] = None
    general: Optional[GeneralConfiguration] = None
    holodule: Optional[HoloduleConfiguration] = None
    google_calendar: Optional[GoogleCalendarConfiguration] = None
    youtube: Optional[YoutubeConfiguration] = None
