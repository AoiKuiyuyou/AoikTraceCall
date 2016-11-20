# coding: utf-8
from __future__ import absolute_import

# Standard imports
import re

# Internal imports
from aoiktracecall.util import get_info_uris


def reject_uri_by_regex(info, patterns, allow=False):
    # Get URI list
    uri_s = get_info_uris(info)

    # If pattern list is not empty
    if patterns:
        # For each pattern
        for pattern in patterns:
            # If the pattern not ends with `$`
            if not pattern.endswith('$'):
                # Append `$` to the pattern
                pattern += '$'

            # For each URI
            for uri in uri_s:
                # If the URI is not empty
                if uri:
                    # Match pattern against the URI
                    matched = re.match(pattern, uri)

                    # If is matched
                    if matched:
                        # Return False to reject
                        return False

    # Return given info
    return info
