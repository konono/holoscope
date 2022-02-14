#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import toml

from holoscope.config import ConfigLoader
from holoscope.thumbnail_cache_manager import ThumbnailCacheManager
from logging import basicConfig
from logging import getLogger

SCOPES = ['https://www.googleapis.com/auth/calendar']

log = getLogger(__name__)

if __name__ == '__main__':
    cl = ConfigLoader()
    config = cl.config
    basicConfig(
        level=(config.general.loglevel).upper(),
        format="[{levelname}][{module}][{funcName}] {message}",
        style='{'
    )
    cache_path = pathlib.Path('thumbnail_cache.toml')
    raw_config = toml.load(cache_path)
    thumbnail_cache = ThumbnailCacheManager(config, raw_config)
    if config.aws.access_key_id and config.aws.secret_access_key:
        if not thumbnail_cache.is_exist_hash_key():
            log.info('Thumbnail cache was not found in dynamodb')
            log.info('Create thumbnail cache')
            thumbnail_cache.set_thumbnail_cache_to_dynamodb()
            log.info('Insert thumbnail cache to dynamodb')
            cache = thumbnail_cache._get_token()
            print(cache)
            log.info('Success get thumbnail cache from dynamodb')
        else:
            log.info('Thumbnail cache was found in dynamodb')
            cache = thumbnail_cache._get_token()
            print(cache)
            log.info('Success get thumbnail cache from dynamodb')
