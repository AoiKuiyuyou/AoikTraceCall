# coding: utf-8
"""
This module contains function that inspects a function's calling arguments.
"""
from __future__ import absolute_import

# Standard imports
from collections import OrderedDict
import inspect
import sys

# Local imports
from .aoikenum import enum


# Version
__version__ = '0.1.1'


# Public attribute names
__all__ = (
    'ParameterType',
    'ArgumentType',
    'ArgumentInfo',
    'InspectInfo',
    'inspect_arguments',
    'format_inspect_info',
    'format_arguments',
)


# Whether is Python 2
IS_PY2 = sys.version_info[0] == 2


@enum
class ParameterType(int):
    """
    Parameter type enumeration class.
    """

    # Values are consistent with Python 3's `inspect.Parameter.kind` values
    POSITIONAL_ONLY = 0
    POSITIONAL_OR_KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4


# If is not Python 2
if not IS_PY2:
    # Ensure values are consistent with `inspect.Parameter.kind` values
    assert ParameterType.POSITIONAL_ONLY == inspect.Parameter.POSITIONAL_ONLY
    assert ParameterType.POSITIONAL_OR_KEYWORD == \
        inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert ParameterType.VAR_POSITIONAL == inspect.Parameter.VAR_POSITIONAL
    assert ParameterType.KEYWORD_ONLY == inspect.Parameter.KEYWORD_ONLY
    assert ParameterType.VAR_KEYWORD == inspect.Parameter.VAR_KEYWORD


@enum
class ArgumentType(int):
    """
    Argument type enumeration class.
    """

    POSITIONAL = 0
    KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4
    DEFAULT = 100
    MISSING = 101


class AttrDict(dict):
    """
    Attribute dict.
    """

    # Getting attribute means getting from dict
    __getattr__ = dict.__getitem__

    # Setting attribute means setting into dict
    __setattr__ = dict.__setitem__


class ArgumentInfo(AttrDict):
    """
    Argument info dict.
    """

    def __init__(
        self,
        name,
        value,
        type,
        param_type,
        pos_index=None,
        varpos_index=None,
    ):
        """
        Constructor.

        :param name: Argument name.

        :param value: Argument value.

        :param type: Argument type. ArgumentType instance.

        :param param_type: Parameter type. ParameterType instance.

        :param pos_index: Positional argument index.

        :param varpos_index: Variable-positional argument index.

        :return: None.
        """
        # Argument name
        self.name = name

        # Argument value
        self.value = value

        # Argument type
        self.type = type

        # Parameter type
        self.param_type = param_type

        # Positional argument index
        self.pos_index = pos_index

        # Variable-positional argument index
        self.varpos_index = varpos_index


class InspectInfo(AttrDict):
    """
    Inspect info dict.
    """

    # Dict keys
    K_POSKWD_PARAM_NAMES = 'poskwd_param_names'
    K_KWDONLY_PARAM_NAMES = 'kwdonly_param_names'
    K_VARPOS_PARAM_NAME = 'varpos_param_name'
    K_VARKWD_PARAM_NAME = 'varkwd_param_name'
    K_FIXED_ARG_INFOS = 'fixed_arg_infos'
    K_VARPOS_ARG_INFOS = 'varpos_arg_infos'
    K_VARKWD_ARG_INFOS = 'varkwd_arg_infos'
    K_DUPKWD_ARG_INFOS = 'dupkwd_arg_infos'
    K_MISSING_ARG_INFOS = 'missing_arg_infos'


def inspect_arguments_py2(func, args, kwargs):
    """
    Inspect function arguments in Python 2.

    :param func: Function.

    :param args: Function positional arguments.

    :param kwargs: Function keyword arguments.

    :return: InspectInfo instance.
    """
    # Map fixed argument name to argument info.
    # `fixed` means positional-or-keyword and keyword-only combined.
    # Notice Python 2 not supports keyword-only parameters.
    fixed_arg_infos = {}

    # Variable-positional argument info list
    varpos_arg_infos = []

    # Map variable-keyword argument name to argument info
    varkwd_arg_infos = {}

    # Map duplicate keyword argument name to argument info
    dupkwd_arg_infos = {}

    # Map missing argument name to argument info
    missing_arg_infos = OrderedDict()

    # Inspect info
    info = InspectInfo({
        InspectInfo.K_POSKWD_PARAM_NAMES: [],
        InspectInfo.K_KWDONLY_PARAM_NAMES: [],
        InspectInfo.K_VARPOS_PARAM_NAME: None,
        InspectInfo.K_VARKWD_PARAM_NAME: None,
        InspectInfo.K_FIXED_ARG_INFOS: fixed_arg_infos,
        InspectInfo.K_VARPOS_ARG_INFOS: varpos_arg_infos,
        InspectInfo.K_VARKWD_ARG_INFOS: varkwd_arg_infos,
        InspectInfo.K_DUPKWD_ARG_INFOS: dupkwd_arg_infos,
        InspectInfo.K_MISSING_ARG_INFOS: missing_arg_infos,
    })

    try:
        # Get parameters info tuple
        # - Positional-or-keyword parameter name list.
        # - Variable-positional parameter name, e.g. `args` for `*args`.
        # - Variable-keyword parameter name, e.g. `kwargs` for `**kwargs`.
        # - Default values for last n positional-or-keyword parameters.
        argspec = inspect.getargspec(func)  # pylint: disable=deprecated-method

        # Unpack parameters info tuple
        poskwd_param_names, varpos_param_name, varkwd_param_name, \
            poskwd_param_defaults = argspec

    # If have error
    except Exception:
        # Return inspect info
        return info

    # Set positional-or-keyword parameter names in inspect info
    info[InspectInfo.K_POSKWD_PARAM_NAMES] = poskwd_param_names

    # Set variable-positional parameter name in inspect info
    info[InspectInfo.K_VARPOS_PARAM_NAME] = varpos_param_name

    # Set variable-keyword parameter name in inspect info
    info[InspectInfo.K_VARKWD_PARAM_NAME] = varkwd_param_name

    # Get positional-or-keyword parameter name count
    poskwd_param_name_count = len(poskwd_param_names)

    # Positional argument index
    pos_index = -1

    # For each positional argument
    for pos_index, arg_value in enumerate(args):
        # If the argument is fixed-positional argument
        if pos_index < poskwd_param_name_count:
            # Get parameter name
            param_name = poskwd_param_names[pos_index]

            # Create argument info
            arg_info = ArgumentInfo(
                name=param_name,
                value=arg_value,
                type=ArgumentType.POSITIONAL,
                pos_index=pos_index,
                param_type=ParameterType.POSITIONAL_OR_KEYWORD,
            )

            # Add argument info to dict
            fixed_arg_infos[param_name] = arg_info

        # If the argument is not fixed-positional argument.
        # It means it is variable-positional argument.
        #
        # Notice if the function has not defined variable-positional parameter,
        # variable-positional arguments are invalid. But they are still
        # collected, and are left for caller to handle.
        #
        else:
            # Get variable-positional argument index, zero-based
            varpos_index = len(varpos_arg_infos)

            # Create argument info
            arg_info = ArgumentInfo(
                name=None,
                value=arg_value,
                type=ArgumentType.VAR_POSITIONAL,
                varpos_index=varpos_index,
                param_type=(
                    ParameterType.VAR_POSITIONAL if
                    varpos_param_name is not None else None
                ),
            )

            # Add argument info to list
            varpos_arg_infos.append(arg_info)

    # Get pending positional-or-keyword parameters that are not given argument.
    #
    # If have positional arguments
    if args:
        # Use remaining positional-or-keyword parameters as pending parameters.
        #
        # Notice if there are variable-positional arguments, `pos_index` value
        # will overrun the list, the slicing will return empty list.
        #
        pending_poskwd_param_name_s = poskwd_param_names[pos_index + 1:]

    # If not have positional arguments
    else:
        # Use all positional-or-keyword parameters as pending parameters
        pending_poskwd_param_name_s = poskwd_param_names

    # For each keyword argument
    for arg_name, arg_value in kwargs.items():
        # Find existing argument info
        existing_arg_info = fixed_arg_infos.get(arg_name, None)

        # If have existing argument info.
        # It means the parameter has been given positional argument, making the
        # keyword argument a duplicate.
        if existing_arg_info is not None:
            # Create argument info
            arg_info = ArgumentInfo(
                name=arg_name,
                value=arg_value,
                type=ArgumentType.KEYWORD,
                param_type=existing_arg_info.param_type,
            )

            # Add argument info to duplicate dict
            dupkwd_arg_infos[arg_name] = arg_info

        # If not have existing argument info.

        # If argument name is in pending positional-or-keyword parameter names.
        # It means the argument is fixed-keyword argument.
        elif arg_name in pending_poskwd_param_name_s:
            # Create argument info
            arg_info = ArgumentInfo(
                name=arg_name,
                value=arg_value,
                type=ArgumentType.KEYWORD,
                param_type=ParameterType.POSITIONAL_OR_KEYWORD,
            )

            # Add argument info to dict
            fixed_arg_infos[arg_name] = arg_info

        # If argument name is not in pending positional-or-keyword parameter
        # names.
        # It means the argument is variable-keyword argument.
        #
        # Notice if the function has not defined variable-keyword parameter,
        # variable-keyword arguments are invalid. But they are still collected,
        # and are left for caller to handle.
        #
        else:
            # Create argument info
            arg_info = ArgumentInfo(
                name=arg_name,
                value=arg_value,
                type=ArgumentType.VAR_KEYWORD,
                param_type=(
                    ParameterType.VAR_KEYWORD if
                    varkwd_param_name is not None else None
                ),
            )

            # Add argument info to dict
            varkwd_arg_infos[arg_name] = arg_info

    # Create dict that maps positional-or-keyword parameter name to default
    # value.
    #
    # If have default values
    if poskwd_param_defaults:
        # Create dict
        map_poskwd_param_name_to_default_value = dict(
            zip(reversed(poskwd_param_names), reversed(poskwd_param_defaults))
        )
    # If not have default values
    else:
        # Use empty dict
        map_poskwd_param_name_to_default_value = {}

    # For each fixed parameter name
    for poskwd_param_name in poskwd_param_names:
        # If the parameter name not has argument info.
        # It means the parameter is still pending.
        if poskwd_param_name not in fixed_arg_infos:
            # If the parameter has default value.
            # It means the argument is default.
            if poskwd_param_name in map_poskwd_param_name_to_default_value:
                # Get default value
                default = \
                    map_poskwd_param_name_to_default_value[poskwd_param_name]

                # Create argument info
                arg_info = ArgumentInfo(
                    name=poskwd_param_name,
                    value=default,
                    type=ArgumentType.DEFAULT,
                    param_type=ParameterType.POSITIONAL_OR_KEYWORD,
                )

                # Add argument info to dict
                fixed_arg_infos[poskwd_param_name] = arg_info

            # If the parameter not has default value.
            # It means the argument is missing.
            else:
                # Create argument info
                arg_info = ArgumentInfo(
                    name=poskwd_param_name,
                    value=None,
                    type=ArgumentType.MISSING,
                    param_type=ParameterType.POSITIONAL_OR_KEYWORD,
                )

                # Add argument info to missing dict
                missing_arg_infos[poskwd_param_name] = arg_info

    # Create ordered dict
    new_fixed_arg_infos = OrderedDict()

    # For each fixed parameter name
    for param_name in poskwd_param_names:
        # Find argument info.
        # Can be None if the argument is missing.
        arg_info = fixed_arg_infos.get(param_name, None)

        # If have argument info
        if arg_info is not None:
            # Add to the ordered dict
            new_fixed_arg_infos[param_name] = arg_info

    # Set fixed argument infos in inspect info
    info[InspectInfo.K_FIXED_ARG_INFOS] = new_fixed_arg_infos

    # Return inspect info
    return info


def signature_to_param_groups(sig):
    """
    Convert function signature object to parameter groups.

    :param sig: Function signature object.

    :return: 4-element tuple: \
        - Positional-or-keyword parameter list.
        - Keyword-only parameter list.
        - Variable-positional parameter.
        - Variable-keyword parameter.
    """
    # Positional-or-keyword parameter list
    poskwd_param_s = []

    # Keyword-only parameter list
    kwdonly_param_s = []

    # Variable-positional parameter
    varpos_param = None

    # Variable-keyword parameter
    varkwd_param = None

    # For each parameter
    for parameter in sig.parameters.values():
        # If the parameter type is variable-positional
        if parameter.kind == ParameterType.VAR_POSITIONAL:
            # Store variable-positional parameter
            varpos_param = parameter

        # If the parameter type is variable-keyword
        elif parameter.kind == ParameterType.VAR_KEYWORD:
            # Store variable-keyword parameter
            varkwd_param = parameter

        # If the parameter type is keyword-only
        elif parameter.kind == ParameterType.KEYWORD_ONLY:
            # Add to keyword-only parameter list
            kwdonly_param_s.append(parameter)

        # If the parameter type is none of above.
        # It means the parameter type is positional-or-keyword (including
        # positional-only)
        else:
            # Add to positional-or-keyword parameter list
            poskwd_param_s.append(parameter)

    # Get result tuple
    result_tuple = (
        poskwd_param_s,
        kwdonly_param_s,
        varpos_param,
        varkwd_param,
    )

    # Return result tuple
    return result_tuple


def inspect_arguments_py3(func, args, kwargs):
    """
    Inspect function arguments in Python 3.

    :param func: Function.

    :param args: Function positional arguments.

    :param kwargs: Function keyword arguments.

    :return: InspectInfo instance.
    """
    # Map fixed argument name to argument info.
    # `fixed` means positional-or-keyword and keyword-only combined.
    fixed_arg_infos = {}

    # Variable-positional argument info list
    varpos_arg_infos = []

    # Map variable-keyword argument name to argument info
    varkwd_arg_infos = {}

    # Map duplicate keyword argument name to argument info
    dupkwd_arg_infos = {}

    # Map missing argument name to argument info
    missing_arg_infos = OrderedDict()

    # Inspect info
    info = InspectInfo({
        InspectInfo.K_POSKWD_PARAM_NAMES: [],
        InspectInfo.K_KWDONLY_PARAM_NAMES: [],
        InspectInfo.K_VARPOS_PARAM_NAME: None,
        InspectInfo.K_VARKWD_PARAM_NAME: None,
        InspectInfo.K_FIXED_ARG_INFOS: fixed_arg_infos,
        InspectInfo.K_VARPOS_ARG_INFOS: varpos_arg_infos,
        InspectInfo.K_VARKWD_ARG_INFOS: varkwd_arg_infos,
        InspectInfo.K_DUPKWD_ARG_INFOS: dupkwd_arg_infos,
        InspectInfo.K_MISSING_ARG_INFOS: missing_arg_infos,
    })

    try:
        # Get signature object
        func_sig = inspect.signature(func)

    # If have error
    except Exception:
        # Return inspect info
        return info

    # Convert signature to parameter groups
    poskwd_param_s, kwdonly_param_s, varpos_param, \
        varkwd_param = signature_to_param_groups(func_sig)

    # Get positional-or-keyword parameter names.
    # Notice this not includes keyword-only parameters.
    poskwd_param_names = [x.name for x in poskwd_param_s]

    # Set positional-or-keyword parameter names in inspect info
    info[InspectInfo.K_POSKWD_PARAM_NAMES] = poskwd_param_names

    # If have keyword-only parameters
    if kwdonly_param_s:
        # Set keyword-only parameter names in inspect info
        info[InspectInfo.K_KWDONLY_PARAM_NAMES] = [
            p.name for p in kwdonly_param_s
        ]

    # Get keyword-only parameter names from inspect info
    kwdonly_param_name_s = info[InspectInfo.K_KWDONLY_PARAM_NAMES]

    # If have variable-positional parameter
    if varpos_param is not None:
        # Set variable-positional parameter name in inspect info
        info[InspectInfo.K_VARPOS_PARAM_NAME] = varpos_param.name

    # Get variable-positional parameter name from inspect info
    varpos_param_name = info[InspectInfo.K_VARPOS_PARAM_NAME]

    # If have variable-keyword parameter
    if varkwd_param is not None:
        # Set variable-keyword parameter name in inspect info
        info[InspectInfo.K_VARKWD_PARAM_NAME] = varkwd_param.name

    # Get variable-keyword parameter name from inspect info
    varkwd_param_name = info[InspectInfo.K_VARKWD_PARAM_NAME]

    # Get positional-or-keyword parameter name count
    poskwd_param_name_count = len(poskwd_param_s)

    # Positional argument index
    pos_index = -1

    # For each positional argument
    for pos_index, arg_value in enumerate(args):
        # If the argument is fixed-positional argument
        if pos_index < poskwd_param_name_count:
            # Get parameter object
            param = poskwd_param_s[pos_index]

            # Create argument info
            arg_info = ArgumentInfo(
                name=param.name,
                value=arg_value,
                type=ArgumentType.POSITIONAL,
                pos_index=pos_index,
                param_type=ParameterType(param.kind),
            )

            # Get parameter name
            param_name = param.name

            # Add argument info to dict
            fixed_arg_infos[param_name] = arg_info

        # If the argument is not fixed-positional argument.
        # It means it is variable-positional argument.
        #
        # Notice if the function has not defined variable-positional parameter,
        # variable-positional arguments are invalid. But they are still
        # collected, and are left for caller to handle.
        #
        else:
            # Get variable-positional argument index, zero-based
            varpos_index = len(varpos_arg_infos)

            # Create argument info
            arg_info = ArgumentInfo(
                name=None,
                value=arg_value,
                type=ArgumentType.VAR_POSITIONAL,
                varpos_index=varpos_index,
                param_type=(
                    ParameterType.VAR_POSITIONAL if
                    varpos_param_name is not None else None
                ),
            )

            # Add argument info to list
            varpos_arg_infos.append(arg_info)

    # Get pending positional-or-keyword parameters that are not given argument.
    #
    # If have positional arguments
    if args:
        # Use remaining positional-or-keyword parameters as pending parameters.
        #
        # Notice if there are variable-positional arguments, `pos_index` value
        # will overrun the list, the slicing will return empty list.
        #
        pending_poskwd_param_name_s = poskwd_param_names[pos_index + 1:]

    # If not have positional arguments
    else:
        # Use all positional-or-keyword parameters as pending parameters
        pending_poskwd_param_name_s = poskwd_param_names

    # For each keyword argument
    for arg_name, arg_value in kwargs.items():
        # Find existing argument info
        existing_arg_info = fixed_arg_infos.get(arg_name, None)

        # If have existing argument info.
        # It means the parameter has been given positional argument, making the
        # keyword argument a duplicate.
        if existing_arg_info is not None:
            # Create argument info
            arg_info = ArgumentInfo(
                name=arg_name,
                value=arg_value,
                type=ArgumentType.KEYWORD,
                param_type=existing_arg_info.param_type,
            )

            # Add argument info to duplicate dict
            dupkwd_arg_infos[arg_name] = arg_info

        # If not have existing argument info.

        # If argument name is in pending positional-or-keyword parameter names.
        # It means the argument is fixed-keyword argument.
        elif arg_name in pending_poskwd_param_name_s:
            # Create argument info
            arg_info = ArgumentInfo(
                name=arg_name,
                value=arg_value,
                type=ArgumentType.KEYWORD,
                param_type=ParameterType.POSITIONAL_OR_KEYWORD,
            )

            # Add argument info to dict
            fixed_arg_infos[arg_name] = arg_info

        # If argument name is in keyword-only parameter names.
        # It means the argument is keyword-only argument.
        elif arg_name in kwdonly_param_name_s:
            # Create argument info
            arg_info = ArgumentInfo(
                name=arg_name,
                value=arg_value,
                type=ArgumentType.KEYWORD_ONLY,
                param_type=ParameterType.KEYWORD_ONLY,
            )

            # Add argument info to dict
            fixed_arg_infos[arg_name] = arg_info

        # If argument name is not in pending positional-or-keyword parameter
        # names or keyword-only parameter names.
        # It means the argument is variable-keyword argument.
        #
        # Notice if the function has not defined variable-keyword parameter,
        # variable-keyword arguments are invalid. But they are still collected,
        # and are left for caller to handle.
        #
        else:
            # Create argument info
            arg_info = ArgumentInfo(
                name=arg_name,
                value=arg_value,
                type=ArgumentType.VAR_KEYWORD,
                param_type=(
                    ParameterType.VAR_KEYWORD if
                    varkwd_param_name is not None else None
                ),
            )

            # Add argument info to dict
            varkwd_arg_infos[arg_name] = arg_info

    # For each fixed parameter
    for fixed_param in poskwd_param_s + kwdonly_param_s:
        # Get parameter name
        fixed_param_name = fixed_param.name

        # If the parameter name not has argument info.
        # It means the parameter is still pending.
        if fixed_param_name not in fixed_arg_infos:
            # If the parameter has default value.
            # It means the argument is default.
            if fixed_param.default is not inspect.Parameter.empty:
                # Create argument info
                arg_info = ArgumentInfo(
                    name=fixed_param_name,
                    value=fixed_param.default,
                    type=ArgumentType.DEFAULT,
                    param_type=ParameterType(fixed_param.kind),
                )

                # Add argument info to dict
                fixed_arg_infos[fixed_param_name] = arg_info

            # If the parameter not has default value.
            # It means the argument is missing.
            else:
                # Create argument info
                arg_info = ArgumentInfo(
                    name=fixed_param_name,
                    value=None,
                    type=ArgumentType.MISSING,
                    param_type=ParameterType(fixed_param.kind),
                )

                # Add argument info to missing dict
                missing_arg_infos[fixed_param_name] = arg_info

    # Create ordered dict
    new_fixed_arg_infos = OrderedDict()

    # For each fixed parameter name
    for param_name in (poskwd_param_names + kwdonly_param_name_s):
        # Find argument info.
        # Can be None if the argument is missing.
        arg_info = fixed_arg_infos.get(param_name, None)

        # If have argument info
        if arg_info is not None:
            # Add to the ordered dict
            new_fixed_arg_infos[param_name] = arg_info

    # Set fixed argument infos in inspect info
    info[InspectInfo.K_FIXED_ARG_INFOS] = new_fixed_arg_infos

    # Return inspect info
    return info


def inspect_arguments(func, args, kwargs):
    """
    Inspect function arguments.

    :param func: Function.

    :param args: Function positional arguments.

    :param kwargs: Function keyword arguments.

    :return: InspectInfo instance.
    """
    # If is Python 2
    if IS_PY2:
        # Delegate call to `inspect_arguments_py2`
        return inspect_arguments_py2(func=func, args=args, kwargs=kwargs)

    # If is not Python 2
    else:
        # Delegate call to `inspect_arguments_py2`
        return inspect_arguments_py3(func=func, args=args, kwargs=kwargs)


def format_inspect_info(
    info,
    repr_func=None,
    filter_func=None,
):
    """
    Format inspect info to text.

    :param info: InspectInfo instance.

    :param repr_func: Representation function converting argument value to \
        string. Default is `repr`.

    :param filter_func: Inspect info filter function.

    :return: Result text.
    """
    # If representation function is not given
    if repr_func is None:
        # Use default
        repr_func = repr

    # If have inspect info filter function
    if filter_func is not None:
        # Store original inspect info
        orig_info = info

        # Call inspect info filter function
        info = filter_func(info)

        # If returned inspect info is None
        if info is None:
            # Use original inspect info
            info = orig_info

    # Result text's part list
    text_part_s = []

    # Fixed-positional argument text list
    fixed_arg_text_s = []

    # Get fixed argument infos dict
    fixed_arg_infos = info[InspectInfo.K_FIXED_ARG_INFOS]

    # For each fixed argument info
    for fixed_arg_info in fixed_arg_infos.values():
        try:
            # Get argument value's repr text
            value_text = repr_func(fixed_arg_info.value)

        # If have error
        except Exception:
            # Use default repr text
            value_text = '<?>'

        # Get argument's repr text
        fixed_arg_text = '{name}={value}'.format(
            name=fixed_arg_info.name,
            value=value_text
        )

        # Add argument's repr text to list
        fixed_arg_text_s.append(fixed_arg_text)

    # If text list is not empty
    if fixed_arg_text_s:
        # Add comma separator
        text_part = ', '.join(fixed_arg_text_s)

        # Add part to list
        text_part_s.append(text_part)

    # Get variable-positional parameter name
    varpos_param_name = info[InspectInfo.K_VARPOS_PARAM_NAME]

    # Get variable-positional argument infos list
    varpos_arg_infos = info[InspectInfo.K_VARPOS_ARG_INFOS]

    # Variable-positional argument text list
    varpos_arg_text_s = []

    # For each variable-positional argument info
    for varpos_arg_info in varpos_arg_infos:
        try:
            # Get argument value's repr text
            value_text = repr_func(varpos_arg_info.value)

        # If have error
        except Exception:
            # Use default repr text
            value_text = '<?>'

        # Get argument's repr text
        varpos_arg_text = str(value_text)

        # Add argument's repr text to list
        varpos_arg_text_s.append(varpos_arg_text)

    # Add comma separator
    text_part = ', '.join(varpos_arg_text_s)

    # If have variable-positional parameter
    if varpos_param_name:
        # Add variable-positional parameter name
        text_part = '*{name}=[{values}]'.format(
            name=varpos_param_name,
            values=text_part
        )

    # If not have variable-positional parameter.
    # These variable-positional arguments are invalid.
    # But they are still added to result.

    # If the text part is not empty
    if text_part:
        # Add the text part to list
        text_part_s.append(text_part)

    # Get variable-keyword parameter name
    varkwd_param_name = info[InspectInfo.K_VARKWD_PARAM_NAME]

    # Get variable-keyword argument infos dict
    varkwd_arg_infos = info[InspectInfo.K_VARKWD_ARG_INFOS]

    # Variable-keyword argument text list
    varkwd_arg_text_s = []

    # For each variable-keyword argument info
    for varkwd_arg_info in sorted(
        varkwd_arg_infos.values(), key=(lambda i: i.name)
    ):
        try:
            # Get argument value's repr text
            value_text = repr_func(varkwd_arg_info.value)

        # If have error
        except Exception:
            # Use default repr value
            value_text = '<?>'

        # Get argument's repr text
        varkwd_arg_text = '{name}={value}'.format(
            name=varkwd_arg_info.name,
            value=value_text
        )

        # Add argument's repr text to list
        varkwd_arg_text_s.append(varkwd_arg_text)

    # Add comma separator
    text_part = ', '.join(varkwd_arg_text_s)

    # If have variable-keyword parameter
    if varkwd_param_name:
        # Add variable-keyword parameter name
        text_part = '**%s={%s}' % (varkwd_param_name, text_part)

    # If not have variable-keyword parameter.
    # These variable-keyword arguments are invalid.
    # But they are still added to result.

    # If the text part is not empty
    if text_part:
        # Add the text part to list
        text_part_s.append(text_part)

    # Get result text
    text = ', '.join(text_part_s)

    # Return result text
    return text


def format_arguments(func, args, kwargs, repr_func=None, filter_func=None):
    """
    Format function arguments to text.

    :param func: Function.

    :param args: Function positional arguments.

    :param kwargs: Function keyword arguments.

    :param repr_func: Representation function converting argument value to \
        string. Default is `repr`.

    :param filter_func: Inspect info filter function.

    :return: Result text.
    """
    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
    )

    # Format inspect info
    text = format_inspect_info(
        info=info,
        repr_func=repr_func,
        filter_func=filter_func,
    )

    # Return result text
    return text
