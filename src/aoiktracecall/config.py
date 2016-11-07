# coding: utf-8
from __future__ import absolute_import


_CONFIG_DICT = {
    # Whether use `CallWrapper` class.
    #
    # `CallWrapper` would break if the code that was using the wrapped function
    # requires a real function, instead of a callable. Known cases include PyQt
    # slot functions.
    'WRAP_USING_CALL_WRAPPER_CLASS': True,

    # Whether wrap base class attributes into subclass attributes
    'WRAP_BASE_CLASS_ATTRIBUTES': True,

    # Figlet width
    'FIGLET_WIDTH': 200,
}


def get_config(key):
    return _CONFIG_DICT.get(key, None)


def set_config(key, value):
    _CONFIG_DICT[key] = value
