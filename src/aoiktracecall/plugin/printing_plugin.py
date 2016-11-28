# coding: utf-8
from __future__ import absolute_import

# Standard imports
from inspect import isclass
from pprint import pformat
from traceback import format_exc

# Internal imports
from aoiktracecall.config import get_config
from aoiktracecall.logging import print_error
from aoiktracecall.logging import print_info
from aoiktracecall.spec import find_matched_spec_info
from aoiktracecall.state import get_simple_thread_id
from aoiktracecall.util import format_func_args
from aoiktracecall.util import format_func_name
from aoiktracecall.util import to_uri
from aoiktracecall.wrap import get_wrapped_obj
from aoiktracecall.wrap import STATICMETHOD_TYPE

# Local imports
from ..aoikinspectargs import format_inspect_info
from ..aoikinspectargs import inspect_arguments


def _repr_safe(obj, default='<?>'):
    try:
        #
        if hasattr(obj, '__repr__'):
            text = repr(obj)
        else:
            text = str(obj)

        #
        return text

    except Exception as e:
        #
        error_msg = "# Warning: Failed getting argument's text:\n---\n{}---\n"\
            .format(
                format_exc()
            )

        #
        print_error(error_msg)

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
        if isinstance(spec_arg, list):
            if INFO_K_HIGHLIGHT in spec_arg:
                highlight_info = {
                    'enabled': True,
                }
        #
        elif isinstance(spec_arg, dict):
            highlight_info = spec_arg.copy()
        #
        else:
            raise ValueError(spec_arg)

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

    #
    try:
        # Inspect function arguments
        inspect_info = inspect_arguments(
            func=func,
            args=args,
            kwargs=kwargs,
        )
    #
    except Exception:
        inspect_info = None

    #
    args_inspect_info_debug_msg = None

    # If need debug arguments inspect info
    if get_config('PRINTING_HANDLER_DEBUG_ARGS_INSPECT_INFO'):
        # If hook type is `pre_call`
        if trace_hook_type == 'pre_call':
            # Get message
            args_inspect_info_debug_msg = \
                '# PRINTING_HANDLER_DEBUG_ARGS_INSPECT_INFO:\n{}\n'.format(
                    pformat(inspect_info, indent=4, width=1)
                )

    #
    if inspect_info is None:
        #
        args_text = format_func_args(
            args=args, kwargs=kwargs, repr_func=_repr_safe
        )
    #
    else:
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
    origin_attr_uri = info.get('origin_attr_uri', None)

    #
    if origin_attr_uri and origin_attr_uri != self_attr_uri:
        self_cls_uri, _, _ = self_attr_uri.rpartition('.')

        func_name_text = '{} -> {}'.format(self_cls_uri, origin_attr_uri)
    else:
        func_name_text = self_attr_uri

    #
    indent_unit = get_config('INDENT_UNIT_TEXT') or ''

    #
    indent_text = indent_unit * level

    #
    if simple_thread_id == 0:
        thread_text = ''
    else:
        thread_text = ' T{}:'.format(simple_thread_id)

    #
    count_text = ' {}: '.format(count)

    #
    if trace_hook_type == 'pre_call':
        call_msg = '{indent}+{thread}{count}{func_name} => {args_text}\n'\
            .format(
                indent=indent_text,
                thread=thread_text,
                count=count_text,
                func_name=func_name_text,
                args_text='( {} )'.format(args_text) if args_text else ''
            )
    elif trace_hook_type == 'post_call':
        result = info['call_result']

        result_repr = _repr_safe(result)

        call_msg = '{indent}-{thread}{count}{func_name} <= {result}\n'\
            .format(
                indent=indent_text,
                thread=thread_text,
                count=count_text,
                func_name=func_name_text,
                result=result_repr,
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

    #
    onself_func = None

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
                        # Get function on `self` class
                        onself_func = vars(self_arg_cls).get(
                            attr_name, None
                        )

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
                            if onself_func is not func:
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
        msg = format_func_name(
            '+ {}'.format(pre_figlet_title), count=count, figlet=True
        )

        print_info(msg, indent=False)

    #
    try:
        # Notice the message is indented already.
        print_info(call_msg, indent=False)
    except Exception:
        exc_msg = '{}\n# Error\n---\n{}---\n'.format(
            onwrap_uri,
            format_exc(),
        )

        print_info(exc_msg)

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
        file_path_lineno = ''

        #
        func_to_show_lineno = func

        # Loop at most 5 times to avoid circle
        for _ in range(5):
            #
            if isinstance(func_to_show_lineno, STATICMETHOD_TYPE):
                if hasattr(func_to_show_lineno, '__func__'):
                    func_to_show_lineno = func_to_show_lineno.__func__

            #
            if hasattr(func_to_show_lineno, '__code__'):
                #
                func_code_obj = func_to_show_lineno.__code__

                #
                if func_code_obj:
                    #
                    file_path_lineno += '# File: {} Line: {}\n'.format(
                        func_code_obj.co_filename,
                        func_code_obj.co_firstlineno,
                    )

            #
            if hasattr(func_to_show_lineno, '__wrapped__'):
                #
                func_to_show_lineno = func_to_show_lineno.__wrapped__

                #
                continue

            #
            break

        #
        if file_path_lineno:
            #
            print_info(file_path_lineno)

    # If hook type is `pre_call`
    if trace_hook_type == 'pre_call':
        #
        need_debug = get_config('PRINTING_HANDLER_DEBUG_INFO_DICT')

        #
        need_debug_safe = get_config('PRINTING_HANDLER_DEBUG_INFO_DICT_SAFE')

        # If need print debug info
        if need_debug or need_debug_safe:
            # Get info dict copy
            debug_info = info.copy()

            #
            if need_debug_safe:
                #
                debug_info.pop('args', None)

                #
                debug_info.pop('kwargs', None)

            # Set internal variables
            debug_info['_INTERNAL_VARIABLES_'] = {
                'self_arg_cls': self_arg_cls,
                'self_attr_uri': self_attr_uri,
                'highlighted_cls': highlighted_cls,
                'highlighted_title': highlighted_title,
            }

            #
            if onself_func is not None:
                #
                debug_info['_INTERNAL_VARIABLES_']['onself_func'] = onself_func

            #
            if not need_debug_safe:
                debug_info['_INTERNAL_VARIABLES_']['self_arg_value'] = \
                    self_arg_value

            # Get message
            msg = '# {}:\n{}\n'.format(
                'PRINTING_HANDLER_DEBUG_INFO_DICT_SAFE' if
                need_debug_safe else 'PRINTING_HANDLER_DEBUG_INFO_DICT',
                pformat(debug_info, indent=4),
            )

            # Print message
            print_info(msg)

    #
    if args_inspect_info_debug_msg:
        # Print message
        print_info(args_inspect_info_debug_msg)

    #
    if post_figlet_title is not None:
        msg = format_func_name(
            '- {}'.format(post_figlet_title), count=count, figlet=True
        )

        print_info(msg, indent=False)

        post_figlet_title = None

    #
    return info
