# coding: utf-8
from __future__ import absolute_import

# Standard imports
from collections import OrderedDict
import re


def parse_specs_by_object(specs):
    #
    obj_uris_dict = OrderedDict()

    #
    if specs:
        #
        re_spec_s = []

        exact_spec_s = []

        #
        for spec in specs:
            if isinstance(spec, (list, tuple)):
                uri = spec[0]

                spec_value = spec[1]

                if isinstance(spec_value, (bool, str)):
                    info = {
                        'spec_value': spec_value,
                    }

                elif isinstance(spec_value, dict):
                    info = spec_value.copy()

                    info['spec_value'] = spec_value
                else:
                    raise ValueError(spec)
            else:
                raise ValueError(spec)

            #
            regex = info.get('regex', None)

            if regex is None:
                if re.search('[^_.0-9a-zA-Z]', uri):
                    #
                    regex = info['regex'] = True

            #
            regex = info['regex'] = bool(regex)

            #
            if regex:
                #
                re_spec_s.append((uri, info))
            else:
                exact_spec_s.append((uri, info))

        # Add exact specs first
        obj_uris_dict.update(exact_spec_s)

        # Add re specs after exact specs
        obj_uris_dict.update(re_spec_s)

    #
    return obj_uris_dict
