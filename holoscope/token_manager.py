#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import os
import pickle

import boto3
from boto3.dynamodb.conditions import Key
from boto3.session import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from holoscope.errors import RestError

SCOPES = ['https://www.googleapis.com/auth/calendar']


class TokenManager(object):
    def __init__(self, config, token_type):
        if config.aws.access_key_id and config.aws.secret_access_key:
            try:
                kms = boto3.client('kms',
                                   aws_access_key_id=config.aws.access_key_id,
                                   aws_secret_access_key=config.aws.secret_access_key)
                dynamodb = boto3.resource('dynamodb',
                                          aws_access_key_id=config.aws.access_key_id,
                                          aws_secret_access_key=config.aws.secret_access_key)
            except: # noqa E722
                dynamodb = Session.resource('dynamodb',
                                            aws_access_key_id=config.aws.access_key_id,
                                            aws_secret_access_key=config.aws.secret_access_key)
            self.table = dynamodb.Table(config.aws.dynamodb_table)
            self.hash_key_name = config.aws.dynamodb_hash_key_name
            self.token_type = token_type
            self.enable_dynamodb = True
        else:
            self.enable_dynamodb = False
        if config.aws.kms_key_id:
            try:
                kms = boto3.client('kms',
                                   aws_access_key_id=config.aws.access_key_id,
                                   aws_secret_access_key=config.aws.secret_access_key)
            except: # noqa E722
                kms = Session.client('kms',
                                     aws_access_key_id=config.aws.access_key_id,
                                     aws_secret_access_key=config.aws.secret_access_key)
            self.kms = kms
            self.key_id = config.aws.kms_key_id
            self.enable_kms = True
        else:
            self.enable_kms = False

    def is_exist_hash_key(self) -> bool:
        options = {
            'Select': 'COUNT',
            'KeyConditionExpression': Key(self.hash_key_name).eq(self.token_type),
            'Limit': 1,
        }
        response = self.table.query(**options)
        if response.get('Count', 0) != 0:
            return True
        return False

    def _get_token(self) -> Credentials:
        if self.enable_dynamodb:
            return self._get_token_from_dynamodb()
        else:
            return self._get_token_from_file()

    def _get_token_from_dynamodb(self) -> Credentials:
        response = self.table.get_item(Key={self.hash_key_name: self.token_type})
        # The value method is used to cast from boto3 Binary type to byte type.
        encoded_creds = response['Item']['credential'].value
        byte_creds = base64.b64decode(encoded_creds)
        if self.enable_kms:
            byte_creds = self.kms.decrypt(CiphertextBlob=byte_creds)['Plaintext']
        creds = pickle.loads(byte_creds)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._update_token(pickle.dumps(creds))
        return creds

    def _get_token_from_file(self) -> Credentials:
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def set_token_to_dynamodb(self):
        with open('token.pickle', 'rb') as token:
            creds = token.read()
        if self.enable_kms:
            encrypted = self.kms.encrypt(KeyId=self.key_id, Plaintext=creds)
            encoded = base64.b64encode(encrypted['CiphertextBlob'])
        else:
            encoded = base64.b64encode(creds)
        response = self.table.put_item(Item={self.hash_key_name: self.token_type,
                                       'credential': encoded})
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RestError(response)
        return response

    def _update_token(self, creds):
        if self.enable_kms:
            encrypted = self.kms.encrypt(KeyId=self.key_id, Plaintext=creds)
            encoded = base64.b64encode(encrypted['CiphertextBlob'])
        else:
            encoded = base64.b64encode(creds)
        response = self.table.update_item(
            Key={self.hash_key_name: self.token_type},
            UpdateExpression="set creds=:e",
            ExpressionAttributeValues={
                ':e': encoded
            },
            ReturnValues="UPDATED_NEW"
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RestError(response)
        return response
