#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Importer(object):
    def __init__(self, config, youtube_utils):
        self.cnf = config
        self.youtube_utils = youtube_utils
        self.video_ids = self._get_video_ids()

    def _get_video_ids(self) -> list:
        upcoming_videos = []
        for channel_id in self.cnf.youtube.channel_ids:
            upcoming_videos += self.youtube_utils.get_upcoming_videos_from_ch(channel_id)
        return upcoming_videos
