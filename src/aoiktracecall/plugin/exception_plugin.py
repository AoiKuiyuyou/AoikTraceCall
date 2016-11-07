# coding: utf-8
from __future__ import absolute_import


def reject_exception(info):
    #
    class_obj = info.get('class', None)

    #
    if class_obj is None:
        return info

    elif isinstance(class_obj, type) and issubclass(class_obj, BaseException):
        return False

    else:
        return info
