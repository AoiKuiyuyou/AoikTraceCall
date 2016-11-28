# coding: utf-8
from __future__ import absolute_import

# Standard imports
from collections import OrderedDict
import re

# Internal imports
from aoiktracecall.logging import print_debug
from aoiktracecall.util import format_info_dict_uris
from aoiktracecall.util import get_info_uris


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
                item_count = len(spec)

                assert item_count >= 2, item_count

                uri = spec[0]

                if item_count == 2:
                    spec_arg = spec[1]

                    if isinstance(spec_arg, dict):
                        spec_arg = spec_arg.copy()
                    elif isinstance(spec_arg, (list, tuple, set)):
                        spec_arg = list(spec_arg)
                    else:
                        spec_arg = [spec_arg]
                else:
                    spec_arg = list(spec[1:])

                assert isinstance(spec_arg, (list, dict)), spec_arg

                info = {
                    'spec_uri': uri,
                    'spec_arg': spec_arg,
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


def find_matched_spec_info(info, parsed_specs, need_log=False):
    # Get URI list
    uri_s = get_info_uris(info)

    #
    uris_text = format_info_dict_uris(info)

    #
    for pattern, spec_info in parsed_specs.items():
        #
        is_regex = spec_info.get('regex', False)

        #
        if is_regex:
            #
            if not pattern.endswith('$'):
                #
                pattern += '$'

        #
        uri = None

        #
        matched = None

        #
        for uri in uri_s:
            #
            if uri:
                #
                if is_regex:
                    #
                    matched = bool(re.match(pattern, uri))
                #
                else:
                    #
                    matched = (pattern == uri)

                #
                if matched:
                    #
                    if need_log:
                        #
                        msg = 'Matched URIs: {}\nMatched spec: {}'.format(
                            uris_text, spec_info
                        )

                        #
                        print_debug(msg)

                    #
                    return spec_info

    else:
        #
        if need_log:
            #
            msg = 'Matched URIs: {}\nMatched Spec: {}'.format(uris_text, None)

            #
            print_debug(msg)

        #
        return None
