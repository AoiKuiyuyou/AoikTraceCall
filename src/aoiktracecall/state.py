# coding: utf-8
from __future__ import absolute_import

# Standard imports
import threading


try:
    # Python 3
    from threading import get_ident
except ImportError:
    # Python 2
    from thread import get_ident


# ----- ThreadLocal -----
class ThreadLocal(threading.local):

    def get(self, attr_name, default=None):
        if not hasattr(self, attr_name):
            self.set(attr_name, default)
        return getattr(self, attr_name)

    def set(self, attr_name, value):
        setattr(self, attr_name, value)
        return value

    def add(self, attr_name, diff, default=None):
        new_value = self.get(attr_name, default=default) + diff
        self.set(attr_name, new_value)
        return new_value


_ThreadLocal = ThreadLocal()
# ===== ThreadLocal =====


# ----- Count APIs -----
def count_get():
    return _ThreadLocal.get('_COUNT', default=0)


def count_set(value):
    return _ThreadLocal.set('_COUNT', value)


def count_add(value, default=0):
    return _ThreadLocal.add('_COUNT', value, default=default)
# ===== Count APIs =====


# ----- Level APIs -----
def level_get():
    return _ThreadLocal.get('_LEVEL', default=-1)


def level_set(value):
    return _ThreadLocal.set('_LEVEL', value)


def level_add(value, default=-1):
    return _ThreadLocal.add('_LEVEL', value, default=default)
# ===== Level APIs =====


# ----- Thread APIs -----
MAIN_THREAD_ID = get_ident()

_SIMPLE_ID_MAX = 0

_SIMPLE_ID_DICT = {
    MAIN_THREAD_ID: 0,
}

_SIMPLE_ID_DICT_LOCK = threading.Lock()


def get_simple_thread_id(thread_id=None):
    #
    if thread_id is None:
        thread_id = get_ident()

    with _SIMPLE_ID_DICT_LOCK:
        simple_thread_id = _SIMPLE_ID_DICT.get(thread_id, None)

        if simple_thread_id is None:
            global _SIMPLE_ID_MAX
            _SIMPLE_ID_MAX += 1
            simple_thread_id = _SIMPLE_ID_DICT[thread_id] = _SIMPLE_ID_MAX

    return simple_thread_id
# ===== Thread APIs =====


# ----- Filter APIs -----
_FILTER = None


def filter_get():
    return _FILTER


def filter_set(filter):
    global _FILTER

    _FILTER = filter
# ===== Handler APIs =====


# ----- Handler APIs -----
_HANDLER = None


def handler_get():
    return _HANDLER


def handler_set(handler):
    global _HANDLER

    _HANDLER = handler
# ===== Handler APIs =====


_MODULE_PRELOAD_CALLBACK = None


def module_preload_get():
    return _MODULE_PRELOAD_CALLBACK


def module_preload_set(callback):
    global _MODULE_PRELOAD_CALLBACK

    _MODULE_PRELOAD_CALLBACK = callback


_MODULE_POSTLOAD_CALLBACK = None


def module_postload_get():
    return _MODULE_POSTLOAD_CALLBACK


def module_postload_set(callback):
    global _MODULE_POSTLOAD_CALLBACK

    _MODULE_POSTLOAD_CALLBACK = callback


_MODULE_FAILLOAD_CALLBACK = None


def module_failload_get():
    return _MODULE_FAILLOAD_CALLBACK


def module_failload_set(callback):
    global _MODULE_FAILLOAD_CALLBACK

    _MODULE_FAILLOAD_CALLBACK = callback


_MODULE_EXISTWRAP_CALLBACK = None


def module_existwrap_get():
    return _MODULE_EXISTWRAP_CALLBACK


def module_existwrap_set(callback):
    global _MODULE_EXISTWRAP_CALLBACK

    _MODULE_EXISTWRAP_CALLBACK = callback


_CLASS_EXISTWRAP_CALLBACK = None


def class_existwrap_get():
    return _CLASS_EXISTWRAP_CALLBACK


def class_existwrap_set(callback):
    global _CLASS_EXISTWRAP_CALLBACK

    _CLASS_EXISTWRAP_CALLBACK = callback


_CALL_EXISTWRAP_CALLBACK = None


def call_existwrap_get():
    return _CALL_EXISTWRAP_CALLBACK


def call_existwrap_set(callback):
    global _CALL_EXISTWRAP_CALLBACK

    _CALL_EXISTWRAP_CALLBACK = callback
