# coding: utf-8
from __future__ import absolute_import

# Standard imports
import threading

# Internal imports
from aoiktracecall.spec import find_matched_spec_info


# ----- Constants -----
# Notice code at 3WO2X relies on the `hide` values.

# Hide calls below the call but show the call itself
HIDE_BELOW = 'hide_below'

# Hide the call itself
HIDE_THIS = 'hide_this'

# Hide the call itself and calls below it
HIDE_TREE = 'hide_tree'

# Show calls below the call but hide the call itself
SHOW_BELOW = 'show_below'

# Show the call itself
SHOW_THIS = 'show_this'

# Show the call itself and calls below it
SHOW_TREE = 'show_tree'

# Set of all values
INFO_K_SHOWHIDE_VALUES = {
    HIDE_BELOW,
    HIDE_THIS,
    HIDE_TREE,
    SHOW_BELOW,
    SHOW_THIS,
    SHOW_TREE,
}


# ----- Info dict keys -----
INFO_K_SHOWHIDE = 'showhide'


def showhide_filter(info, parsed_specs):
    #
    spec_info = find_matched_spec_info(
        info=info,
        parsed_specs=parsed_specs,
        print_info=True,
    )

    #
    if spec_info is None:
        #
        return False
    else:
        # Default is show
        info['showhide'] = True

        #
        spec_arg = spec_info['spec_arg']

        #
        if isinstance(spec_arg, bool):
            info['showhide'] = spec_arg

        #
        elif isinstance(spec_arg, str):
            if spec_arg in INFO_K_SHOWHIDE_VALUES:
                info['showhide'] = spec_arg
            else:
                # Use default
                pass

        #
        elif isinstance(spec_arg, set):
            for value in INFO_K_SHOWHIDE_VALUES:
                if value in spec_arg:
                    info['showhide'] = value

                    break
            else:
                # Use default
                pass

        #
        elif isinstance(spec_arg, dict):
            #
            showhide = spec_arg.get(INFO_K_SHOWHIDE, None)

            #
            if showhide is None:
                # Use default
                pass

            elif isinstance(showhide, bool):
                info['showhide'] = showhide

            elif showhide in INFO_K_SHOWHIDE_VALUES:
                info['showhide'] = showhide

            else:
                raise ValueError(showhide)

        #
        else:
            info['showhide'] = True

        #
        if info['showhide'] is False:
            return False
        else:
            return info


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
        # 3WO2X
        if state_stack and state_stack[-1][0].startswith('hide'):
            return False
        else:
            return info

    elif showhide == SHOW_THIS:
        return info

    elif showhide == HIDE_THIS:
        return False

    elif showhide in [
            HIDE_TREE,
            HIDE_BELOW,
            SHOW_TREE,
            SHOW_BELOW]:
        if info_type == 'call':
            state_stack.append((showhide, func))
        elif info_type == 'return':
            if state_stack and state_stack[-1][1] is func:
                state_stack.pop()
        else:
            raise ValueError(info_type)

        if showhide == HIDE_TREE:
            return False

        elif showhide == SHOW_TREE:
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
