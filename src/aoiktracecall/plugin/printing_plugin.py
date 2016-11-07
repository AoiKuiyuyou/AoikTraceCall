# coding: utf-8
from __future__ import absolute_import

# Standard imports
import inspect
import traceback

# Internal imports
from aoiktracecall.plugin.figlet_plugin import print_text
from aoiktracecall.spec import find_matched_spec_info
from aoiktracecall.state import get_simple_thread_id
from aoiktracecall.util import to_uri


try:
    # Python 3
    import builtins
except Exception:
    # Python 2
    import __builtin__ as builtins


try:
    # Python 3
    from inspect import signature
except Exception:
    # Python 2
    signature = None


#
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


def format_args(
        func,
        cls,
        module,
        func_name,
        args,
        kwargs,
        show_self=False):
    #
    if func_name is None:
        func_name = func.__name__

    #
    if signature:
        try:
            func_sig = signature(func)
        except Exception:
            func_sig = None
    else:
        func_sig = None

    #
    self_value = None

    #
    var_pos_arg_value_s = []

    #
    var_kwd_arg_name_to_value_dict = {}

    #
    fix_pos_arg_text_s = []

    #
    fix_kwd_arg_text_s = []

    # Use None to mean the function has no parameter "*args"
    var_pos_arg_text_s = None

    # Use None to mean the function has no parameter "**kwargs"
    var_kwd_arg_text_s = None

    #
    if func_sig is None:
        #
        for value in args:
            fix_pos_arg_text = _repr_safe(value)

            fix_pos_arg_text_s.append(fix_pos_arg_text)

        #
        for key, value in kwargs.items():
            fix_kwd_arg_text = '{}={}'.format(key, _repr_safe(value))

            fix_kwd_arg_text_s.append(fix_kwd_arg_text)
    else:
        params_dict = func_sig.parameters

        params_list = list(params_dict.values())

        arg_name_to_value_dict = {}

        is_var_pos_arg = False

        for index, value in enumerate(args):
            if not is_var_pos_arg:
                param = params_list[index]

                param_name = param.name

                if param.kind == inspect.Parameter.VAR_POSITIONAL:
                    is_var_pos_arg = True

            if is_var_pos_arg:
                var_pos_arg_value_s.append(value)
            else:
                arg_name_to_value_dict[param_name] = value

        for arg_name, value in kwargs.items():
            # Get param info object
            param = params_dict.get(arg_name, arg_name)

            # If the param info object is not found,
            # it means the argument is an variable keyword argument.
            if param is arg_name:
                var_kwd_arg_name_to_value_dict[arg_name] = value
            # If the param info object is found,
            # it means the argument is a fixed keyword argument.
            else:
                arg_name_to_value_dict[arg_name] = value

        for param_name, param_info in params_dict.items():
            #
            if param_name == 'self':
                self_value = arg_name_to_value_dict[param_name]

                if not show_self:
                    continue

            #
            if param_info.kind == inspect.Parameter.VAR_POSITIONAL:
                #
                var_pos_arg_text_s = []

                for value in var_pos_arg_value_s:
                    #
                    var_pos_arg_text = _repr_safe(value, default=param_name)

                    var_pos_arg_text_s.append(var_pos_arg_text)
            #
            elif param_info.kind == inspect.Parameter.VAR_KEYWORD:
                #
                var_kwd_arg_text_s = []

                for key, value in sorted(
                        var_kwd_arg_name_to_value_dict.items(),
                        key=lambda x: x[0]):
                    #
                    var_kwd_arg_text = '{}: {}'.format(
                        key, _repr_safe(value, default=param_name))

                    var_kwd_arg_text_s.append(var_kwd_arg_text)
            #
            elif param_info.kind == inspect.Parameter.KEYWORD_ONLY:
                #
                value = arg_name_to_value_dict.get(
                    param_name, param_info.default)

                kwd_only_arg_text = '{}={}'.format(
                    param_name, _repr_safe(value, default=param_name))

                fix_kwd_arg_text_s.append(kwd_only_arg_text)
            else:
                #
                value = arg_name_to_value_dict.get(
                    param_name, param_info.default)

                fix_pos_arg_text = '{}={}'.format(
                    param_name, _repr_safe(value, default=param_name))

                if param_name == 'environ':
                    fix_pos_arg_text = 'environ={...}'

                fix_pos_arg_text_s.append(fix_pos_arg_text)

    #
    args_text_part_s = []

    #
    if fix_pos_arg_text_s:
        pos_args_text = ', '.join(fix_pos_arg_text_s)

        args_text_part_s.append(pos_args_text)

    #
    if var_pos_arg_text_s is not None:
        if var_pos_arg_text_s:
            var_pos_args_text = ', '.join(var_pos_arg_text_s)
            var_pos_args_text = '*args=[ {} ]'.format(
                var_pos_args_text)
        else:
            var_pos_args_text = '*args=[]'

        args_text_part_s.append(var_pos_args_text)

    #
    if fix_kwd_arg_text_s:
        fix_kwd_args_text = ', '.join(fix_kwd_arg_text_s)

        args_text_part_s.append(fix_kwd_args_text)

    #
    if var_kwd_arg_text_s is not None:
        if var_kwd_arg_text_s:
            var_kwd_args_text = ', '.join(var_kwd_arg_text_s)
            var_kwd_args_text = '**kwargs={ %s }' % var_kwd_args_text
        else:
            var_kwd_args_text = '**kwargs={}'

        args_text_part_s.append(var_kwd_args_text)

    #
    args_text = ', '.join(args_text_part_s)

    #
    res_dict = {
        'arg_self': self_value,
        'args_text': args_text,
    }

    #
    return res_dict


#
_BUILTIN_OBJECTS = tuple(vars(builtins).values())


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
def printing_handler(info, pre_handler=None):
    #
    if pre_handler is not None:
        info = pre_handler(info)

    #
    if not isinstance(info, dict):
        return info

    #
    info_type = info['type']

    #
    level = info['level']

    count = info['count']

    #
    func = info['func']

    #
    uri = info['uri']

    #
    func_name = info['name']

    #
    cls = info['class']

    #
    mro_cls = info.get('mro_cls', None)

    #
    base_cls = mro_cls if mro_cls is not None else cls

    #
    module = info['module']

    args = info['args']

    kwargs = info['kwargs']

    attr_name = info['name']

    #
    format_args_dict = format_args(
        func=func,
        cls=cls,
        module=module,
        func_name=func_name,
        args=args,
        kwargs=kwargs,
        show_self=False)

    #
    arg_self = format_args_dict['arg_self']

    args_text = format_args_dict['args_text']

    #
    simple_thread_id = get_simple_thread_id()

    #
    self_cls = None

    if arg_self is not None:
        if arg_self.__class__ is not cls:
            self_cls = arg_self.__class__

    else:
        if attr_name == '__new__':
            if args:
                self_cls = args[0]

    #
    if self_cls is None:
        self_cls = info['class']

    #
    self_attr_uri = to_uri(module=module, cls=self_cls, attr_name=attr_name)

    #
    base_attr_uri = to_uri(module=module, cls=base_cls, attr_name=attr_name)

    #
    if base_attr_uri == self_attr_uri:
        base_attr_uri = ''

    #
    if self_attr_uri and base_attr_uri:
        self_base_sep = ' -> '
    else:
        self_base_sep = ''

    #
    if attr_name == '__init__':
        figlet_title = to_uri(
            module_name='', cls=base_cls, attr_name=attr_name)
    else:
        figlet_title = to_uri(
            module_name='', cls=self_cls, attr_name=attr_name)

    #
    msg = None

    indent_unit = '        '

    if info_type == 'call':
        msg = '{}+ {}: {}: {}{}{} => {}'.format(
            indent_unit * level,
            'T{}'.format(simple_thread_id),
            count,
            self_attr_uri,
            self_base_sep,
            base_attr_uri,
            '( {} )'.format(args_text) if args_text else '')
    elif info_type == 'return':
        result = info['return']

        result_repr = _repr_safe(result)

        msg = '{}- {}: {}: {}{}{} <= {}'.format(
            indent_unit * level,
            'T{}'.format(simple_thread_id),
            count,
            self_attr_uri,
            self_base_sep,
            base_attr_uri,
            result_repr,
        )
    else:
        raise ValueError(info_type)

    if msg:
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
                title = figlet_title

            #
            if info_type == 'call':
                pre_figlet_title = title
            else:
                post_figlet_title = title

        #
        if pre_figlet_title is not None:
            print_text(
                '+ {}'.format(pre_figlet_title), count=count, figlet=True)

        #
        try:
            print(msg)
        except Exception:
            exc_msg = '{}\n# Error\n---\n{}---\n'.format(
                uri,
                traceback.format_exc(),
            )

            print(exc_msg)

        #
        if post_figlet_title is not None:
            print_text(
                '- {}'.format(post_figlet_title), count=count, figlet=True)

            post_figlet_title = None

    #
    return info
