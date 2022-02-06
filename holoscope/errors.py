#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Error(Exception):
    """An ambigious error occurred."""
    pass


class RestError(Error):
    """A REST error occurred."""
    pass


class UserError(Error):
    """A user caused error occurred."""
    pass


class ConfigrationError(Error):
    """A file caused error occurred."""
    pass
