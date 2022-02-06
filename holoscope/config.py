#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dacite
import pathlib
import toml

from holoscope.datamodel import Configuration
from holoscope.errors import ConfigrationError


class ConfigLoader(object):
    def __init__(self, config_path='./config.toml'):
        config_path = pathlib.Path(config_path)
        if not config_path.exists():
            raise ConfigrationError(str(config_path) + ' was not found')
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        raw_config = toml.load(self.config_path)
        config = dacite.from_dict(data_class=Configuration, data=raw_config)
        return config


if __name__ == '__main__':
    cl = ConfigLoader()
    print(cl.config)
