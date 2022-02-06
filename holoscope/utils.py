#!/usr/bin/env python
# -*- coding: utf-8 -*-


class YoutubeUtils():
    def __init__(self, youtube_instance):
        self.youtube = youtube_instance

    def get_upcomming_videos_from_ch(self, channel_id: str, max_results: int = 5) -> list:
        response = self.youtube.search().list(channelId=channel_id, part='id',
                                              order='date', type='video',
                                              eventType='upcoming',
                                              maxResults=max_results).execute()
        video_ids = [item['id']['videoId'] for item in response.get('items', [])]
        return video_ids

    def get_live_event(self, video_ids: list) -> list:
        part = 'snippet,liveStreamingDetails'
        video_response = self.youtube.videos().list(id=','.join(video_ids),
                                                    part=part).execute()
        return video_response.get('items', [])


class GooglecClendarUtils(object):
    def __init__(self, google_calendar_instance) -> None:
        self.youtube = google_calendar_instance

    def get_calendars(self) -> list:
        # カレンダーのリストを取得
        pt = None
        calendars = []

        while True:
            calendar_list = self.calendar.calendarList().list(pageToken=pt).execute()
            for calendar_list_entry in calendar_list['items']:
                calendars.append(calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        return calendars
