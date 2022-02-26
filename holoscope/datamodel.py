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
    def actual_end_time(self) -> Optional[Arrow]:
        try:
            actual_end_time = arrow.get(self._data['liveStreamingDetails']['actualEndTime'])
        except KeyError:
            actual_end_time = None
        return actual_end_time

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
    def collaborate(self) -> list:
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

    # TODO(if self._data.get('extendedProperties'): section will planned delete.)
    @property
    def scheduled_start_time(self) -> str:
        if self._data.get('extendedProperties'):
            scheduled_start_time = self._data['extendedProperties']['private']['scheduled_start_time']
        else:
            return None
        return arrow.get(scheduled_start_time)

    @property
    def end_time(self) -> str:
        end_time = self._data['end']['dateTime']
        return arrow.get(end_time)

    @property
    def link(self) -> str:
        return self._data['htmlLink']

    @property
    def calid(self) -> str:
        return self._data['organizer']['email']

    @property
    def description(self) -> str:
        return self._data['description']

    # TODO(if self._data.get('extendedProperties'): section will planned delete.)
    @property
    def video_id(self) -> str:
        if self._data.get('extendedProperties'):
            return self._data['extendedProperties']['private']['video_id']
        url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"  # noqa: W605
        for url in re.findall(url_pattern, self.description):
            url = urlparse(url)
            if 'youtube.com' in url.netloc or 'youtu.be' in url.netloc:
                return url.query.split('=')[1]

    # TODO(if self._data.get('extendedProperties'): section will planned delete.)
    @property
    def original_title(self) -> str:
        if self._data.get('extendedProperties'):
            return self._data['extendedProperties']['private']['title']
        return None

    # TODO(if self._data.get('extendedProperties'): section will planned delete.)
    @property
    def channel_id(self) -> str:
        if self._data.get('extendedProperties'):
            return self._data['extendedProperties']['private']['channel_id']
        return None

    # TODO(if self._data.get('extendedProperties'): section will planned delete.)
    @property
    def actor(self) -> str:
        if self._data.get('extendedProperties'):
            return self._data['extendedProperties']['private']['actor']
        return None

    # TODO(if self._data.get('extendedProperties'): section will planned delete.)
    @property
    def collaborate(self) -> str:
        if self._data.get('extendedProperties'):
            return self._data['extendedProperties']['private']['collaborate']
        return None


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
    enable_actual_end_time: Optional[bool] = False


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
