#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arrow

from arrow.arrow import Arrow
from dataclasses import dataclass
from typing import List
from typing import Optional


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

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.id

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def title(self) -> str:
        return self._data['summary']

    @property
    def start_dateTime(self) -> str:
        start_dateTime = self._data['start']['dateTime']
        return arrow.get(start_dateTime)

    @property
    def actual_start_time(self) -> str:
        try:
            actual_start_time = arrow.get(self._data['extendedProperties']['private']['actual_start_time'])
        except KeyError:
            actual_start_time = None
        return actual_start_time

    @property
    def actual_end_time(self) -> str:
        try:
            actual_end_time = arrow.get(self._data['extendedProperties']['private']['actual_end_time'])
        except KeyError:
            actual_end_time = None
        return actual_end_time

        actual_end_time = self._data['extendedProperties']['private']['actual_end_time']
        return arrow.get(actual_end_time)

    @property
    def scheduled_start_time(self) -> str:
        scheduled_start_time = self._data['extendedProperties']['private']['scheduled_start_time']
        return arrow.get(scheduled_start_time)

    @property
    def end_dateTime(self) -> str:
        end_dateTime = self._data['end']['dateTime']
        return arrow.get(end_dateTime)

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
        return self._data['extendedProperties']['private']['video_id']

    @property
    def original_title(self) -> str:
        return self._data['extendedProperties']['private']['title']

    @property
    def channel_id(self) -> str:
        return self._data['extendedProperties']['private']['channel_id']

    @property
    def actor(self) -> str:
        return self._data['extendedProperties']['private']['actor']

    @property
    def collaborate(self) -> str:
        try:
            collaborate = self._data['extendedProperties']['private']['collaborate']
        except KeyError:
            collaborate = None
        return collaborate

    @property
    def extendedProperties(self) -> dict:
        return self._data["extendedProperties"]["private"]


@dataclass
class AwsConfiguration:
    kms_key_id: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    s3_bucket: Optional[str] = None
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
class LineConfiguration:
    line_channel_access_token: str


@dataclass
class Configuration:
    aws: Optional[AwsConfiguration] = None
    general: Optional[GeneralConfiguration] = None
    holodule: Optional[HoloduleConfiguration] = None
    google_calendar: Optional[GoogleCalendarConfiguration] = None
    youtube: Optional[YoutubeConfiguration] = None
    line: Optional[LineConfiguration] = None
