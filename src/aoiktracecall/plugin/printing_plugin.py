# coding: utf-8
from __future__ import absolute_import

# Standard imports
import traceback

# Internal imports
from aoiktracecall.plugin.figlet_plugin import print_text
from aoiktracecall.spec import find_matched_spec_info
from aoiktracecall.state import get_simple_thread_id
from aoiktracecall.util import to_uri

# Local imports
from ..aoikinspectargs import format_inspect_info
from ..aoikinspectargs import inspect_arguments


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
    cls = info['class']

    #
    mro_cls = info.get('mro_cls', None)

    #
    module = info['module']

    args = info['args']

    kwargs = info['kwargs']

    attr_name = info['name']

    # `self` argument value
    arg_self = None

    # Inspect function arguments
    inspect_info = inspect_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
    )

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
            arg_self = arg_info.value

            # Remove `self` argument info
            del fixed_arg_infos['self']

    # Format function arguments
    args_text = format_inspect_info(
        inspect_info,
        repr_func=repr,
    )

    #
    simple_thread_id = get_simple_thread_id()

    #
    self_cls = None

    #
    attr_uri = None

    #
    if cls is None:
        attr_uri = to_uri(module=module, cls=None, attr_name=attr_name)
    else:
        if arg_self is not None:
            if arg_self.__class__ is not cls:
                self_cls = arg_self.__class__

        else:
            if attr_name == '__new__':
                if args:
                    self_cls = args[0]

        if self_cls is not None:
            if isinstance(self_cls, type):
                if issubclass(self_cls, cls):
                    attr_uri = to_uri(
                        module=module, cls=self_cls, attr_name=attr_name
                    )

        #
        if attr_uri is None:
            #
            attr_uri = to_uri(module=module, cls=cls, attr_name=attr_name)

    #
    if mro_cls is None:
        #
        mro_cls_attr_uri = ''
    else:
        #
        mro_cls_attr_uri = to_uri(
            module=module, cls=mro_cls, attr_name=attr_name
        )

        #
        if mro_cls_attr_uri == attr_uri:
            mro_cls_attr_uri = ''

    #
    if attr_uri and mro_cls_attr_uri:
        uri_sep = ' -> '
    else:
        uri_sep = ''

    #
    msg = None

    indent_unit = '        '

    if info_type == 'call':
        msg = '{}+ {}: {}: {}{}{} => {}'.format(
            indent_unit * level,
            'T{}'.format(simple_thread_id),
            count,
            attr_uri,
            uri_sep,
            mro_cls_attr_uri,
            '( {} )'.format(args_text) if args_text else '')
    elif info_type == 'return':
        result = info['return']

        result_repr = _repr_safe(result)

        msg = '{}- {}: {}: {}{}{} <= {}'.format(
            indent_unit * level,
            'T{}'.format(simple_thread_id),
            count,
            attr_uri,
            uri_sep,
            mro_cls_attr_uri,
            result_repr,
        )
    else:
        raise ValueError(info_type)

    #
    title_cls = None

    if attr_name == '__init__':
        if mro_cls is not None:
            title_cls = mro_cls

    if title_cls is None:
        if self_cls is not None:
            title_cls = self_cls
        else:
            title_cls = cls

    figlet_title = to_uri(module_name='', cls=title_cls, attr_name=attr_name)

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
