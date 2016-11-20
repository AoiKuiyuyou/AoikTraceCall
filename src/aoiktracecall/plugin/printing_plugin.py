# coding: utf-8
from __future__ import absolute_import

# Standard imports
from inspect import isclass
from pprint import pformat
import traceback

# Internal imports
from aoiktracecall.config import get_config
from aoiktracecall.spec import find_matched_spec_info
from aoiktracecall.state import get_simple_thread_id
from aoiktracecall.util import print_func_name
from aoiktracecall.util import print_text
from aoiktracecall.util import to_uri
from aoiktracecall.wrap import get_wrapped_obj

# Local imports
from ..aoikinspectargs import format_inspect_info
from ..aoikinspectargs import inspect_arguments


def _repr_safe(obj, default='?'):
    try:
        #
        if hasattr(obj, '__repr__'):
            text = repr(obj)
        else:
            text = str(obj)

        #
        return text

    except Exception as e:
        print('Error (5HZNN): {}'.format(e))

    return default


#
INFO_K_HIGHLIGHT = 'highlight'


def printing_filter(info, parsed_specs):
    #
    spec_info = find_matched_spec_info(info=info, parsed_specs=parsed_specs)

    #
    if spec_info is None:
        #
        return info
    else:
        #
        highlight_info = None

        #
        spec_arg = spec_info['spec_arg']

        #
        if spec_arg == INFO_K_HIGHLIGHT:
            highlight_info = {
                'enabled': True,
            }

        #
        elif isinstance(spec_arg, set):
            if INFO_K_HIGHLIGHT in spec_arg:
                highlight_info = {
                    'enabled': True,
                }

        #
        elif isinstance(spec_arg, dict):
            highlight_info = spec_arg

        #
        info[INFO_K_HIGHLIGHT] = highlight_info

        #
        return info


#
def printing_handler(info, filter_func=None):
    #
    trace_hook_type = info['trace_hook_type']

    #
    info_type = info['info_type']

    #
    level = info['level']

    #
    count = info['count']

    #
    module = info['module']

    #
    cls = info['class']

    #
    func = info['func']

    #
    args = info['args']

    #
    kwargs = info['kwargs']

    #
    onwrap_uri = info['onwrap_uri']

    #
    attr_name = info['attr_name']

    # `self` argument value
    self_arg_value = None

    # Inspect function arguments
    inspect_info = inspect_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
    )

    # First argument name
    first_arg_name = None

    # Get fixed argument infos dict
    fixed_arg_infos = inspect_info['fixed_arg_infos']

    # If fixed argument infos dict is not empty
    if fixed_arg_infos:
        # Get the first fixed argument name
        first_arg_name = next(iter(fixed_arg_infos))

        # If the first fixed argument name is `self`
        if first_arg_name == 'self':
            # Get `self` argument info
            arg_info = fixed_arg_infos['self']

            # Get `self` argument value
            self_arg_value = arg_info.value

    # If have filter function
    if filter_func is not None:
        # Add arguments inspect info to info dict
        info['arguments_inspect_info'] = inspect_info

        # Call filter function
        info = filter_func(info)

        # Remove arguments inspect info from info dict
        info.pop('arguments_inspect_info', None)

        # If returned info is None
        if info is None:
            # Ignore
            return

    # If the first fixed argument name is `self`
    if first_arg_name == 'self':
        # Remove `self` argument info
        fixed_arg_infos.pop('self', None)

    # Format function arguments
    args_text = format_inspect_info(
        inspect_info,
        repr_func=repr,
    )

    #
    simple_thread_id = get_simple_thread_id()

    #
    self_arg_cls = None

    #
    self_attr_uri = None

    #
    if cls is None:
        self_attr_uri = onwrap_uri
    else:
        if self_arg_value is not None:
            self_arg_cls = self_arg_value.__class__

        else:
            if attr_name == '__new__':
                if args:
                    self_arg_cls = args[0]

        #
        if self_arg_cls is not cls:

            #
            if isclass(self_arg_cls) and issubclass(self_arg_cls, cls):
                #
                self_attr_uri = to_uri(
                    module=module, cls=self_arg_cls, attr_name=attr_name
                )

        #
        if self_attr_uri is None:
            #
            self_attr_uri = onwrap_uri

    #
    origin_attr_uri_shown = \
        info.get('origin_attr_uri', None) or ''

    #
    if origin_attr_uri_shown == self_attr_uri:
        origin_attr_uri_shown = ''

    #
    if self_attr_uri and origin_attr_uri_shown:
        uri_sep = ' -> '
    else:
        uri_sep = ''

    #
    indent_unit = '        '

    if trace_hook_type == 'pre_call':
        msg = '{}+ {}: {}: {}{}{} => {}'.format(
            indent_unit * level,
            'T{}'.format(simple_thread_id),
            count,
            self_attr_uri,
            uri_sep,
            origin_attr_uri_shown,
            '( {} )'.format(args_text) if args_text else '')
    elif trace_hook_type == 'post_call':
        result = info['call_result']

        result_repr = _repr_safe(result)

        msg = '{}- {}: {}: {}{}{} <= {}'.format(
            indent_unit * level,
            'T{}'.format(simple_thread_id),
            count,
            self_attr_uri,
            uri_sep,
            origin_attr_uri_shown,
            result_repr,
        )
    else:
        raise ValueError(trace_hook_type)

    #
    if self_arg_cls is not None:
        highlighted_cls = self_arg_cls
    else:
        highlighted_cls = cls

    # Get origin attribute class
    origin_attr_class = info.get('origin_attr_class', None)

    # If have origin attribute class
    if origin_attr_class is not None:
        # If origin attribute class is not highlighted class
        if origin_attr_class is not highlighted_cls:
            # If the function is constructor
            if attr_name == '__init__':
                # Use origin attribute class as highlighted class
                highlighted_cls = origin_attr_class

            # If the config says not use `self` class
            elif not get_config('HIGHLIGHT_TITLE_SHOW_SELF_CLASS'):
                # Use origin attribute class as highlighted class
                highlighted_cls = origin_attr_class

            # If info type is `class_attr`
            elif info_type == 'class_attr':
                # If have `self` class
                if self_arg_cls is not None:
                    # If `self` class is not origin attribute class
                    if self_arg_cls is not origin_attr_class:
                        # Get origin function
                        origin_func = getattr(origin_attr_class, attr_name)

                        # Get wrapped object if it is a wrapper
                        origin_func = get_wrapped_obj(origin_func, origin_func)

                        # Get function on `self` class
                        onself_func = getattr(self_arg_cls, attr_name, None)

                        # If have function on `self` class
                        if onself_func is not None:
                            # Get wrapped object if it is a wrapper
                            onself_func = get_wrapped_obj(
                                onself_func, onself_func
                            )

                            # If the function on `self` class is not the origin
                            # function.
                            # It means the `self` class has defined same-name
                            # attribute. But the origin class' attribute is
                            # called. This is the case of calling super method.
                            if onself_func is not origin_func:
                                # Use origin attribute class as highlighted
                                # class
                                highlighted_cls = origin_attr_class

    #
    highlighted_title = to_uri(
        module_name='',
        cls=highlighted_cls,
        attr_name=attr_name,
    )

    #
    pre_figlet_title = None

    post_figlet_title = None

    #
    highlight_info = info.get(INFO_K_HIGHLIGHT, None)

    #
    if highlight_info is not None and highlight_info.get('enabled', True):
        #
        title = highlight_info.get('title', None)

        if not title:
            title = highlighted_title

        #
        if trace_hook_type == 'pre_call':
            pre_figlet_title = title
        else:
            post_figlet_title = title

    #
    if pre_figlet_title is not None:
        print_func_name(
            '+ {}'.format(pre_figlet_title), count=count, figlet=True)

    #
    try:
        print(msg)
    except Exception:
        exc_msg = '{}\n# Error\n---\n{}---\n'.format(
            onwrap_uri,
            traceback.format_exc(),
        )

        print(exc_msg)

    #
    if hasattr(func, '__code__'):
        #
        need_print_lineno = False

        #
        if trace_hook_type == 'pre_call':
            #
            if get_config('SHOW_FUNC_FILE_PATH_LINENO_PRE_CALL'):
                #
                need_print_lineno = True

        #
        if trace_hook_type == 'post_call':
            #
            if get_config('SHOW_FUNC_FILE_PATH_LINENO_POST_CALL'):
                #
                need_print_lineno = True

        #
        if need_print_lineno:
            #
            func_code_obj = func.__code__

            #
            file_path_lineno = '# {} Line: {}'.format(
                func_code_obj.co_filename,
                func_code_obj.co_firstlineno,
            )

            #
            print_text(file_path_lineno)

    # If need print debug info
    if get_config('PRINTING_HANDLER_SHOW_DEBUG_INFO'):
        # If is before call the wrapped function
        if trace_hook_type == 'pre_call':
            # Get info dict copy
            debug_info = info.copy()

            # Set internal variables
            debug_info['_INTERNAL_VARIABLES_'] = {
                'self_arg_cls': self_arg_cls,
                'self_arg_value': self_arg_value,
                'self_attr_uri': self_attr_uri,
                'highlighted_cls': highlighted_cls,
                'highlighted_title': highlighted_title,
                'origin_attr_uri_shown': origin_attr_uri_shown,
            }

            # Print title
            print_text('# `printing_handler` debug:')

            # Print debug info dict
            print_text(pformat(debug_info, indent=4))

            print('')

    #
    if post_figlet_title is not None:
        print_func_name(
            '- {}'.format(post_figlet_title), count=count, figlet=True)

        post_figlet_title = None

    #
    return info
