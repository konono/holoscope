#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import json
import logging

from apiclient.discovery import build

from holoscope.config import ConfigLoader
from holoscope.datamodel import LiveEvent
from holoscope.utils import YoutubeUtils

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
IMPOTER_PLUGIN_DIR = "holoscope.importer_plugin"
EXPOTER_PLUGIN_DIR = "holoscope.exporter_plugin"

log = logging.getLogger(__name__)


class Holoscope(object):
    def __init__(self, config):
        self.cnf = config

    def run(self):
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=self.cnf.youtube.api_key
        )

        importer_plugin_path = f'{IMPOTER_PLUGIN_DIR}.{self.cnf.general.importer_plugin}'
        exporter_plugin_path = f'{EXPOTER_PLUGIN_DIR}.{self.cnf.general.exporter_plugin}'

        importer_module = importlib.import_module(importer_plugin_path,
                                                  package='Importer')
        exporter_module = importlib.import_module(exporter_plugin_path,
                                                  package='Exporter')

        youtube_utils = YoutubeUtils(youtube)
        importer = importer_module.Importer(self.cnf, youtube_utils)

        responses = youtube_utils.get_live_event(importer.video_ids)
        log.debug('LIVE EVENT JSON DUMP')
        log.debug(json.dumps(responses))

        events = []
        for resp in responses:
            events.append(LiveEvent(resp))
            log.info(f'Live event found {events[-1].channel_title}: {events[-1].title}.')

        exporter = exporter_module.Exporter(self.cnf)
        exporter.create_event(events)


if __name__ == '__main__':
    config = ConfigLoader()
    holoscope = Holoscope(config)
    holoscope.run()
