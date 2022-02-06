#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import pickle

import boto3
from boto3.dynamodb.conditions import Key
from boto3.session import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from holoscope.errors import RestError


class TokenManager(object):
    def __init__(self, config, token_type):
        try:
            kms = boto3.client('kms',
                               aws_access_key_id=config.aws.access_key_id,
                               aws_secret_access_key=config.aws.secret_access_key)
            dynamodb = boto3.resource('dynamodb',
                                      aws_access_key_id=config.aws.access_key_id,
                                      aws_secret_access_key=config.aws.secret_access_key)
        except: # noqa E722
            kms = Session.client('kms',
                                 aws_access_key_id=config.aws.access_key_id,
                                 aws_secret_access_key=config.aws.secret_access_key)
            dynamodb = Session.resource('dynamodb',
                                        aws_access_key_id=config.aws.access_key_id,
                                        aws_secret_access_key=config.aws.secret_access_key)
        self.kms = kms
        self.table = dynamodb.Table(config.aws.dynamodb_table)
        self.key_id = config.aws.kms_key_id
        self.hash_key_name = config.aws.dynamodb_hash_key_name
        self.token_type = token_type

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
        response = self.table.get_item(Key={self.hash_key_name: self.token_type})
        # The value method is used to cast from boto3 Binary type to byte type.
        encrypted_creds = response['Item']['credential'].value
        base64_decoded = base64.b64decode(encrypted_creds)
        decrypted = self.kms.decrypt(CiphertextBlob=base64_decoded)['Plaintext']
        creds = pickle.loads(decrypted)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._update_token(pickle.dumps(creds))
        return creds

    def set_token(self):
        with open('token.pickle', 'rb') as token:
            creds = token.read()
        encrypted = self.kms.encrypt(KeyId=self.key_id, Plaintext=creds)
        encoded = base64.b64encode(encrypted['CiphertextBlob'])
        response = self.table.put_item(Item={self.hash_key_name: self.token_type,
                                       'credential': encoded})
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RestError(response)
        return response

    def _update_token(self, creds):
        encrypted = self.kms.encrypt(KeyId=self.key_id, Plaintext=creds)
        encoded = base64.b64encode(encrypted['CiphertextBlob'])
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
