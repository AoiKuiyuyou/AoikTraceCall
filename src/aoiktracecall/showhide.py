# coding: utf-8
from __future__ import absolute_import

# Standard imports
import re
import threading

# Internal imports
from aoiktracecall.const import HIDE
from aoiktracecall.const import HIDE_BELOW
from aoiktracecall.const import HIDE_ME
from aoiktracecall.const import HIDE_WHOLE
from aoiktracecall.const import SHOW_BELOW
from aoiktracecall.const import SHOW_ME
from aoiktracecall.const import SHOW_WHOLE


INFO_K_SHOWHIDE = 'showhide'

INFO_K_FIGLET = 'figlet'


def showhide_filter(info, parsed_specs=None, print_uri=False):
    #
    if parsed_specs is None:
        raise ValueError(parsed_specs)

    #
    attr_obj_uri = info['uri']

    #
    if print_uri:
        print('URI: {}'.format(attr_obj_uri))

    #
    for pattern, spec_info in parsed_specs.items():
        #
        is_regex = spec_info.get('regex', False)

        #
        if is_regex:
            #
            if not pattern.endswith('$'):
                pattern += '$'

            matched = bool(re.match(pattern, attr_obj_uri))
        else:
            matched = (attr_obj_uri == pattern)

        if matched:
            #
            spec_value = spec_info['spec_value']

            #
            if spec_value is False:
                return False

            #
            elif isinstance(spec_value, (bool, str)):
                info['showhide'] = spec_value

            #
            elif isinstance(spec_value, dict):
                #
                showhide = spec_value.get(INFO_K_SHOWHIDE, None)

                #
                if showhide is False:
                    #
                    info['showhide'] = False

                    #
                    return False

                elif showhide in [None, True]:
                    info['showhide'] = True

                elif isinstance(showhide, str):
                    info['showhide'] = showhide

                else:
                    raise ValueError(showhide)

                #
                figlet_info = spec_value.get(INFO_K_FIGLET, None)

                #
                if figlet_info:
                    if isinstance(figlet_info, dict):
                        figlet_info = figlet_info

                        figlet_info.setdefault('enable', True)
                    else:
                        figlet_info = {
                            'enable': figlet_info,
                        }

                    info[INFO_K_FIGLET] = figlet_info

            #
            else:
                raise ValueError(spec_value)

            #
            return info

    #
    return False


_TLocal = threading.local()


def showhide_handler(info):
    #
    state_stack = getattr(_TLocal, 'state_stack', None)

    if state_stack is None:
        state_stack = _TLocal.state_stack = []

    #
    info_type = info['type']

    #
    func = info['func']

    #
    showhide = info.get(INFO_K_SHOWHIDE, None)

    #
    if showhide is None:
        return info

    #
    elif showhide is False:
        return False

    elif showhide is True:
        if state_stack and state_stack[-1][0].startswith(HIDE):
            return False
        else:
            return info

    elif showhide == SHOW_ME:
        return info

    elif showhide == HIDE_ME:
        return False

    elif showhide in [
            HIDE_WHOLE,
            HIDE_BELOW,
            SHOW_WHOLE,
            SHOW_BELOW]:
        if info_type == 'call':
            state_stack.append((showhide, func))
        elif info_type == 'return':
            if state_stack and state_stack[-1][1] is func:
                state_stack.pop()
        else:
            raise ValueError(info_type)

        if showhide == HIDE_WHOLE:
            return False

        elif showhide == SHOW_WHOLE:
            return info

        elif showhide == SHOW_BELOW:
            return False

        elif showhide == HIDE_BELOW:
            return info

        else:
            raise ValueError(showhide)
    else:
        raise ValueError(showhide)

    raise ValueError(showhide)
