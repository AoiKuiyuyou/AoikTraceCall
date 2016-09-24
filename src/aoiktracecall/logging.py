# coding: utf-8
from __future__ import absolute_import


_LOG_ON = False


def log_set_on(value=True):
    global _LOG_ON
    _LOG_ON = value


def print_log(text):
    if _LOG_ON:
        print(text)
