# coding: utf-8
from __future__ import absolute_import

# Standard imports
from collections import OrderedDict
import re


def parse_specs(specs):
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

                info = {
                    'spec_uri': uri,
                    'spec_arg': spec[1],
                }
            else:
                raise ValueError(spec)

            #
            is_regex = bool(re.search('[^_.0-9a-zA-Z]', uri))

            #
            info['regex'] = is_regex

            #
            if is_regex:
                re_spec_s.append((uri, info))
            else:
                exact_spec_s.append((uri, info))

        # Add exact specs first
        obj_uris_dict.update(exact_spec_s)

        # Add re specs after exact specs
        obj_uris_dict.update(re_spec_s)

    #
    return obj_uris_dict


def find_matched_spec_info(info, parsed_specs, print_info=False):
    #
    uri = info['uri']

    #
    for pattern, spec_info in parsed_specs.items():
        #
        is_regex = spec_info.get('regex', False)

        #
        if is_regex:
            #
            if not pattern.endswith('$'):
                pattern += '$'

            matched = bool(re.match(pattern, uri))
        else:
            matched = (uri == pattern)

        #
        if matched:
            if print_info:
                print('# Match: {}: {}'.format(uri, spec_info))

            return spec_info

    else:
        if print_info:
            print('# Match: {}: {}'.format(uri, None))

        return None
