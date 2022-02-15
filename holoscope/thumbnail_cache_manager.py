#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
# import imagehash
# import io
import logging
import os
import toml
# import urllib.request

from boto3.dynamodb.conditions import Key
from boto3.session import Session
from holoscope.errors import RestError
from holoscope.utils import YoutubeUtils
# from PIL import Image


log = logging.getLogger(__name__)


class ThumbnailCacheManager(object):
    def __init__(self, config, youtube_instance, data=None):
        if config.aws.access_key_id and config.aws.secret_access_key:
            try:
                dynamodb = boto3.resource('dynamodb',
                                          aws_access_key_id=config.aws.access_key_id,
                                          aws_secret_access_key=config.aws.secret_access_key)
            except: # noqa E722
                dynamodb = Session.resource('dynamodb',
                                            aws_access_key_id=config.aws.access_key_id,
                                            aws_secret_access_key=config.aws.secret_access_key)
            self.table = dynamodb.Table(config.aws.dynamodb_table)
            self.hash_key_name = config.aws.dynamodb_hash_key_name
            self.enable_dynamodb = True
        else:
            self.enable_dynamodb = False
        self.youtube = youtube_instance
        self.hash_key = 'thumbnail_cache'
        self.data = data

    def is_exist_hash_key(self) -> bool:
        options = {
            'Select': 'COUNT',
            'KeyConditionExpression': Key(self.hash_key_name).eq(self.hash_key),
            'Limit': 1,
        }
        response = self.table.query(**options)
        if response.get('Count', 0) != 0:
            return True
        return False

    def get_thumbnail_cache(self) -> str:
        if self.enable_dynamodb:
            thumbnail_cache = self._get_thumbnail_cache_from_dynamodb()
        else:
            thumbnail_cache = self._get_thumbnail_cache_from_file()
        if thumbnail_cache:
            thumbnail_cache = self._update_thumbnail_cache(thumbnail_cache)
        else:
            thumbnail_cache = self._set_thumbnail_cache()
        return thumbnail_cache

    def _get_thumbnail_cache_from_dynamodb(self) -> dict:
        if self.is_exist_hash_key():
            response = self.table.get_item(Key={self.hash_key_name: self.hash_key})
            thumbnail_cache = response['Item'][self.hash_key]
            log.info('Get thumbnail cache from dynamodb')
        else:
            log.info('Thumbnail cache was not found in dynamodb')
            return None
        return thumbnail_cache

    def _get_thumbnail_cache_from_file(self) -> dict:
        if os.path.exists(f'{self.hash_key}.toml'):
            thumbnail_cache = toml.load(f'{self.hash_key}.toml')
            log.info('Get thumbnail cache from file')
        else:
            log.info('Thumbnail cache was not found')
            return None
        return thumbnail_cache

    def _update_thumbnail_cache(self, thumbnail_cache) -> str:
        if self.enable_dynamodb:
            if thumbnail_cache:
                return self._update_thumbnail_cache_to_dynamodb(thumbnail_cache)
            else:
                return self.set_thumbnail_cache_to_dynamodb()
        else:
            return self._update_thumbnail_cache_to_file(thumbnail_cache)

    def _update_thumbnail_cache_to_dynamodb(self, thumbnail_cache) -> dict:
        thumbnail_cache = self._update_youtube_thumbnail(thumbnail_cache)
        for i in thumbnail_cache:
            # if not thumbnail_cache[i].get('holodule_img_hash'):
            #     if thumbnail_cache[i].get('holodule_url'):
            #         img_read = urllib.request.urlopen(thumbnail_cache[i]['holodule_url']).read()
            #         img_bin = io.BytesIO(img_read)
            #         img_hash = imagehash.average_hash(Image.open(img_bin))
            #         thumbnail_cache[i]['holodule_img_hash'] = str(img_hash)
            if self.data.get(i):
                if self.data[i].get('holodule_url') != thumbnail_cache[i].get('holodule_url'):
                    thumbnail_cache[i].update(self.data[i])
                    # img_read = urllib.request.urlopen(thumbnail_cache[i]['holodule_url']).read()
                    # img_bin = io.BytesIO(img_read)
                    # img_hash = imagehash.average_hash(Image.open(img_bin))
                    # thumbnail_cache[i]['holodule_img_hash'] = str(img_hash)
                    log.info(f'Update holodule thumbnail url: {i}')

        response = self.table.update_item(
            Key={self.hash_key_name: self.hash_key},
            UpdateExpression=f"set {self.hash_key}=:e",
            ExpressionAttributeValues={
                ':e': thumbnail_cache
            },
            ReturnValues="UPDATED_NEW"
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RestError(response)
        log.info('Update thumbnail cache to dynamodb')
        return thumbnail_cache

    def _update_thumbnail_cache_to_file(self, thumbnail_cache) -> dict:
        if thumbnail_cache:
            thumbnail_cache = self._update_youtube_thumbnail(thumbnail_cache)
            for i in thumbnail_cache:
                # if not thumbnail_cache[i].get('holodule_img_hash'):
                #     if thumbnail_cache[i].get('holodule_url'):
                #         img_read = urllib.request.urlopen(thumbnail_cache[i]['holodule_url']).read()
                #         img_bin = io.BytesIO(img_read)
                #         img_hash = imagehash.average_hash(Image.open(img_bin))
                #         thumbnail_cache[i]['holodule_img_hash'] = str(img_hash)
                if self.data.get(i):
                    if self.data[i].get('holodule_url') != thumbnail_cache[i].get('holodule_url'):
                        thumbnail_cache[i].update(self.data[i])
                        # img_read = urllib.request.urlopen(thumbnail_cache[i]['holodule_url']).read()
                        # img_bin = io.BytesIO(img_read)
                        # img_hash = imagehash.average_hash(Image.open(img_bin))
                        # thumbnail_cache[i]['holodule_img_hash'] = str(img_hash)
                        log.info(f'Update holodule thumbnail url: {i}')

            with open(f'{self.hash_key}.toml', 'wt') as f:
                toml.dump(thumbnail_cache, f)
            return thumbnail_cache
        else:
            with open(f'{self.hash_key}.toml', 'wt') as f:
                toml.dump(self.data, f)
            return self.data

    def _update_youtube_thumbnail(self, thumbnail_cache):
        youtube_utils = YoutubeUtils(self.youtube)
        responses = youtube_utils.get_channels([thumbnail_cache[i]['channel'] for i in thumbnail_cache])
        for resp in responses:
            for i in thumbnail_cache:
                # if not thumbnail_cache[i].get('youtube_img_hash'):
                #     if thumbnail_cache[i].get('youtube_url'):
                #         img_read = urllib.request.urlopen(thumbnail_cache[i]['youtube_url']).read()
                #         img_bin = io.BytesIO(img_read)
                #         img_hash = imagehash.average_hash(Image.open(img_bin))
                #         thumbnail_cache[i]['youtube_img_hash'] = str(img_hash)
                if thumbnail_cache[i]['channel'] == resp['id']:
                    if (thumbnail_cache[i].get('youtube_url') !=
                            resp['snippet']['thumbnails']['default']['url']):
                        thumbnail_cache[i]['youtube_url'] = resp['snippet']['thumbnails']['default']['url']
                        # img_read = urllib.request.urlopen(thumbnail_cache[i]['youtube_url']).read()
                        # img_bin = io.BytesIO(img_read)
                        # img_hash = imagehash.average_hash(Image.open(img_bin))
                        # thumbnail_cache[i]['holodule_img_hash'] = str(img_hash)
                        log.info(f'Update youtube thumbnail url: {i}')
        return thumbnail_cache

    def set_thumbnail_cache_to_dynamodb(self):
        response = self.table.put_item(Item={self.hash_key_name: self.hash_key,
                                       self.hash_key: self.data})
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RestError(response)
        log.info('Insert thumbnail cache to dynamodb')
        return self.data
