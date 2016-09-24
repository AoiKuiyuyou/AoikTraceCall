# coding: utf-8
from __future__ import absolute_import

# Internal imports
import aoiktracecall.filter.builtin as filters
import aoiktracecall.showhide
from aoiktracecall.spec import parse_specs_by_object


def filter_factory(
    regex_attr_filter=None,
    exception_filter=None,
    showhide_filter=None,
    custom_filter=None,
):
    #
    if showhide_filter:
        if not isinstance(showhide_filter, dict):
            raise ValueError(showhide_filter)

        specs = showhide_filter.pop('specs')

        showhide_filter['parsed_specs'] = parse_specs_by_object(specs)

    #
    def new_filter(info):
        #
        if exception_filter:
            #
            if exception_filter is True:
                kwargs = {}
            elif isinstance(exception_filter, dict):
                kwargs = exception_filter
            else:
                raise ValueError(exception_filter)

            #
            info = filters.exception_filter(info, **kwargs)

            #
            if not isinstance(info, dict):
                return False

        #
        if regex_attr_filter:
            #
            if regex_attr_filter is True:
                kwargs = {}
            elif isinstance(regex_attr_filter, dict):
                kwargs = regex_attr_filter
            else:
                raise ValueError(regex_attr_filter)

            #
            info = filters.regex_attr_filter(info, **kwargs)

            #
            if not isinstance(info, dict):
                return False

        #
        if showhide_filter:
            #
            if isinstance(showhide_filter, dict):
                kwargs = showhide_filter
            else:
                raise ValueError(showhide_filter)

            #
            info = aoiktracecall.showhide.showhide_filter(info, **kwargs)

            #
            if not isinstance(info, dict):
                return False

        #
        if custom_filter is not None:
            #
            info = custom_filter(info)

            #
            if not isinstance(info, dict):
                return False

        #
        return info

    #
    return new_filter
