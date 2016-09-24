# coding: utf-8
from __future__ import absolute_import

# Standard imports
import re


_EMPTY = ()


def regex_attr_filter(info, specs, allow=False):
    #
    attr_obj_uri = info['uri']

    #
    if specs:
        #
        for spec in specs:
            #
            if not spec.endswith('$'):
                spec += '$'

            #
            res = re.match(spec, attr_obj_uri)

            #
            if res:
                if allow:
                    return info
                else:
                    return False
        else:
            if allow:
                return False
            else:
                return info

    #
    return info


def exception_filter(info):
    #
    class_obj = info.get('class', None)

    #
    if class_obj is None:
        return info

    elif isinstance(class_obj, type) and issubclass(class_obj, BaseException):
        return False

    else:
        return info
