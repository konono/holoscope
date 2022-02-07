#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

from bs4 import BeautifulSoup


class Importer(object):
    def __init__(self, config):
        self.cnf = config
        self.video_ids = self._get_video_ids()

    def _get_video_ids(self):
        r = requests.get(self.cnf.holodule.holodule_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        divs = soup.find_all('div', class_="col-12 col-sm-12 col-md-12")
        schedules = []
        for div in divs:
            a = div.find('a')
            if a:
                s = '\n'.join(filter(lambda x: x.strip(),
                                     a.get_text().replace(" ", "").split('\r\n')))
                schedules.append({s.split('\n')[1]:
                                  a.get('href')[a.get('href').find('=')+1:]})
        schedules = list(map(json.loads, set(map(json.dumps, schedules))))
        video_ids = []
        for schedule in schedules:
            for k, v in schedule.items():
                if [h for h in self.cnf.holodule.holomenbers if k == h]:
                    video_ids.append(v)
        return video_ids
