# coding: utf-8
from __future__ import absolute_import

# Standard imports
import re


def reject_uri_by_regex(info, patterns, allow=False):
    # Get attribute URI
    attr_uri = info['uri']

    # If pattern list is not empty
    if patterns:
        # For each pattern
        for pattern in patterns:
            # If the pattern not ends with `$`
            if not pattern.endswith('$'):
                # Append `$` to the pattern
                pattern += '$'

            # Match pattern against the attribute URI
            matched = re.match(pattern, attr_uri)

            # If is matched
            if matched:
                # Return False to reject
                return False

    # Return given info
    return info
