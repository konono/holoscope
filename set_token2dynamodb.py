#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from holoscope.config import ConfigLoader
from holoscope.token_manager import TokenManager
from logging import basicConfig
from logging import getLogger

SCOPES = ['https://www.googleapis.com/auth/calendar']

log = getLogger(__name__)


def create_token():
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


def valid_token(creds):
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    cl = ConfigLoader()
    config = cl.config
    basicConfig(
        level=(config.general.loglevel).upper(),
        format="[{levelname}][{module}][{funcName}] {message}",
        style='{'
    )
    token_manager = TokenManager(config, token_type='google_calendar')
    if config.aws.access_key_id and config.aws.secret_access_key:
        if not token_manager.is_exist_hash_key():
            log.info('Token was not found in dynamodb')
            log.info('Create token')
            creds = create_token()
            valid_token(creds)
            token_manager.set_token_to_dynamodb()
            log.info('Insert token to dynamodb')
            creds = token_manager._get_token()
            log.info('Success get token from dynamodb')
        else:
            log.info('Token was found in dynamodb')
            creds = token_manager._get_token()
            log.info('Success get token from dynamodb')
    else:
        log.info('Create token')
        creds = create_token()
        valid_token(creds)
        log.info('Success validation token')
