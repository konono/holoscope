#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging import FileHandler
from logging import Formatter
from logging import NOTSET
from logging import StreamHandler

import os
import sys

from holoscope.config import ConfigLoader
from holoscope.core import Holoscope

FORMAT = "[%(asctime)s] [%(levelname)s][%(module)s][%(funcName)s]: %(message)s"

log = logging.getLogger(__name__)


def lambda_handler(event, context):
    cl = ConfigLoader()
    config = cl.config
    logging.basicConfig(
        level=(config.general.loglevel).upper(),
        format="[{asctime}] [{levelname}][{module}][{funcName}]: {message}",
        style='{',
        stream=sys.stdout,
        force=True
    )
    holoscope = Holoscope(config)
    holoscope.run()


def set_stream_handler(loglevel):
    stream_handler = StreamHandler()
    stream_handler.setLevel(loglevel)
    stream_handler.setFormatter(
        Formatter(FORMAT)
    )
    return stream_handler


def set_file_handler(logdir, logfile, loglevel):
    if not os.path.isdir(logdir):
        os.makedirs(logdir, exist_ok=True)
    file_handler = FileHandler(f"{logdir}/{logfile}")
    file_handler.setLevel(loglevel)
    file_handler.setFormatter(
        Formatter(FORMAT)
    )
    return file_handler


if __name__ == '__main__':
    cl = ConfigLoader()
    cnf = cl.config
    stream_handler = set_stream_handler(cnf.general.loglevel)
    file_handler = set_file_handler(cnf.general.logdir,
                                    cnf.general.logfile,
                                    cnf.general.loglevel)
    logging.basicConfig(level=NOTSET, handlers=[stream_handler, file_handler])

    logging.basicConfig(
        handlers=[stream_handler, file_handler]
    )
    holoscope = Holoscope(cnf)
    holoscope.run()
