# coding: utf-8
from __future__ import absolute_import

# Internal imports
import aoiktracecall.handler.printing
import aoiktracecall.showhide


def handler_factory(
    pre_handler=None,
    post_handler=None,
    showhide_handler=None,
    printing_handler=None,
):
    #
    if showhide_handler is None:
        showhide_handler_func = None
    else:
        showhide_handler_func = aoiktracecall.showhide.showhide_handler

        #
        if showhide_handler is True:
            showhide_handler_kwargs = {}
        elif isinstance(showhide_handler, dict):
            showhide_handler_kwargs = showhide_handler
        else:
            raise ValueError(showhide_handler)

    #
    if printing_handler is None:
        printing_handler_func = None
    else:
        printing_handler_func = aoiktracecall.handler.printing.printing_handler

        #
        if printing_handler is True:
            printing_handler_kwargs = {}
        elif isinstance(printing_handler, dict):
            printing_handler_kwargs = printing_handler
        else:
            raise ValueError(printing_handler)

    #
    def new_handler(info):
        #
        if info is None:
            return None

        #
        if pre_handler is not None:
            info = pre_handler(info)

            if info is None:
                return None

        #
        if showhide_handler_func is not None:
            info = showhide_handler_func(info, **showhide_handler_kwargs)

            if info is None:
                return None

        #
        if printing_handler_func is not None:
            info = printing_handler_func(info, **printing_handler_kwargs)

            if info is None:
                return None

        #
        if post_handler is not None:
            info = post_handler(info)

            if info is None:
                return None

        #
        return info

    #
    return new_handler
