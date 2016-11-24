# coding: utf-8
from __future__ import absolute_import

# Standard imports
import sys

# Internal imports
from aoiktracecall.config import get_config
from aoiktracecall.state import count_get
from aoiktracecall.state import get_simple_thread_id
from aoiktracecall.state import level_add
from aoiktracecall.state import level_get


try:
    from pyfiglet import figlet_format
except ImportError:
    figlet_format = None


def to_uri(
    module=None,
    module_name=None,
    cls=None,
    cls_name=None,
    attr_obj=None,
    attr_name=None,
):
    # Find module name using method 1
    if module_name is None:
        if cls is not None:
            module_name = getattr(cls, '__module__', None)

            if not isinstance(module_name, str):
                module_name = None

    # Find module name using method 2
    if module_name is None:
        if attr_obj is not None:
            module_name = getattr(attr_obj, '__module__', None)

            if not isinstance(module_name, str):
                module_name = None

    # Find module name using method 3
    if module_name is None:
        if module is not None:
            module_name = getattr(module, '__name__', None)

            if not isinstance(module_name, str):
                module_name = None

    # Use default
    if module_name is None:
        module_name = ''

    #
    if cls_name is None:
        if cls is not None:
            cls_name = getattr(cls, '__name__', None)

            if not isinstance(cls_name, str):
                cls_name = None

    # Use default
    if cls_name is None:
        cls_name = ''

    #
    if attr_name is None:
        if attr_obj is not None:
            attr_name = getattr(attr_obj, '__name__', None)

            if not isinstance(attr_name, str):
                attr_name = None

    # Use default
    if attr_name is None:
        attr_name = ''

    #
    if module_name:
        after_module_sep = '.'
    else:
        after_module_sep = ''

    #
    if cls_name and attr_name:
        cls_attr_sep = '.'
    else:
        cls_attr_sep = ''

    #
    obj_uri = \
        '{module_name}{after_module_sep}{cls_name}{cls_attr_sep}{attr_name}'\
        .format(
            module_name=module_name,
            after_module_sep=after_module_sep,
            cls_name=cls_name,
            cls_attr_sep=cls_attr_sep,
            attr_name=attr_name,
        )

    #
    return obj_uri


def to_origin_uri(
    module=None,
    cls=None,
    attr_obj=None,
    attr_name=None,
):
    #
    orig_module = None

    #
    if cls is not None:
        #
        orig_module_name = getattr(cls, '__module__', None)

        #
        if not isinstance(orig_module_name, str):
            #
            orig_module_name = None

        #
        if orig_module_name:
            #
            orig_module = sys.modules.get(orig_module_name, None)

    #
    if orig_module is None:
        #
        if attr_obj is not None:
            #
            orig_module_name = getattr(attr_obj, '__module__', None)

            #
            if not isinstance(orig_module_name, str):
                orig_module_name = None

            #
            if orig_module_name:
                #
                orig_module = sys.modules.get(orig_module_name, None)

    #
    if orig_module is None:
        #
        orig_module = module

    #
    if orig_module is None:
        #
        orig_module_name = '<?>'
    else:
        #
        orig_module_name = orig_module.__name__

    #
    if cls is None:
        #
        orig_cls_name = ''
    else:
        #
        orig_cls_name = cls.__name__

    #
    if attr_obj is None:
        #
        orig_attr_name = ''
    else:
        #
        orig_attr_name = getattr(attr_obj, '__name__', None) or attr_name

    #
    if orig_module_name:
        #
        after_module_sep = '.'
    else:
        #
        after_module_sep = ''

    #
    if orig_cls_name and orig_attr_name:
        #
        cls_attr_sep = '.'
    else:
        #
        cls_attr_sep = ''

    #
    obj_uri = \
        '{module_name}{after_module_sep}{cls_name}{cls_attr_sep}{attr_name}'\
        .format(
            module_name=orig_module_name,
            after_module_sep=after_module_sep,
            cls_name=orig_cls_name,
            cls_attr_sep=cls_attr_sep,
            attr_name=orig_attr_name,
        )

    #
    return obj_uri


def chain_filters(filters):
    # Create combo filter
    def combo_filter(info):
        # For each filter
        for filter in filters:
            # Call the filter
            info = filter(info)

            # If the result info is not dict
            if not isinstance(info, dict):
                # Return false
                return False

        # Return result info
        return info

    # Return combo filter
    return combo_filter


def indent_text(text, indent):
    new_part_s = []
    for line in text.split('\n'):
        new_part_s.append(indent)
        new_part_s.append(line)
        new_part_s.append('\n')
    new_part_s.pop()
    res = ''.join(new_part_s)
    return res


def indent_by_level(
    text,
    level=None,
    indent_unit='        ',
    level_step_before=0,
    level_step_after=0,
    level_diff=0,
    auto_step=False,
):
    #
    if auto_step:
        level_step_before = 1

        level_step_after = -1

    #
    if level_step_before:
        level_add(level_step_before)

    #
    if level is None:
        #
        level = level_get()

    #
    indent = indent_unit * (level + level_diff)

    #
    text = indent_text(text, indent)

    #
    if level_step_after:
        level_add(level_step_after)

    #
    return text


def format_func_name(
    text,
    indent_unit='        ',
    indent_by_level=True,
    level_step_before=0,
    level_step_after=0,
    level_diff=0,
    count=True,
    figlet=False,
    auto_step=False,
):
    #
    if auto_step:
        level_step_before = 1

        level_step_after = -1

    #
    if level_step_before:
        level_add(level_step_before)

    #
    head_mark = ''
    if text.startswith('+'):
        head_mark = '+'
    elif text.startswith('-'):
        head_mark = '-'
    else:
        head_mark = '!'

    #
    simple_thread_id = get_simple_thread_id()

    #
    if simple_thread_id == 0:
        thread_text = ''
    else:
        thread_text = '{} T{}'.format(head_mark, simple_thread_id)

    #
    if count is None or count is False:
        count_text = ' '
    elif count is True:
        count_text = ' {} {} '.format(head_mark, count_get())
    else:
        count_text = ' {} {} '.format(head_mark, count)

    #
    indent = ''

    #
    if indent_unit is not None:
        if indent_by_level:
            indent = indent_unit * (level_get() + level_diff)
        else:
            indent = indent_unit

    #
    text = '{thread_text}{count_text}{text} {head_mark}'.format(
        thread_text=thread_text,
        count_text=count_text,
        text=text,
        head_mark=head_mark,
    )

    #
    if figlet:
        if figlet_format is not None:
            figlet_width = \
                get_config('HIGHLIGHT_TITLE_LINE_CHAR_COUNT_MAX') - len(indent)

            text = figlet_format(text, width=figlet_width)

    #
    if indent:
        text = indent_text(text, indent)

    #
    if level_step_after:
        level_add(level_step_after)

    #
    return text


def format_func_args(args, kwargs, repr_func):
    #
    pos_args_text = ', '.join(repr_func(x) for x in args)

    #
    kwd_args_text = ', '.join(
        '{}={}'.format(
            item[0], repr_func(item[1])
        ) for item in sorted(
            kwargs.items(), key=lambda i: i[0]
        )
    )

    #
    if pos_args_text and kwd_args_text:
        #
        result_text = '{}, {}'.format(pos_args_text, kwd_args_text)
    #
    elif pos_args_text:
        #
        result_text = pos_args_text
    #
    elif kwd_args_text:
        #
        result_text = kwd_args_text
    #
    else:
        #
        result_text = ''

    #
    return result_text


def get_info_uris(info):
    # URI list
    uri_s = []

    # Get onwrap URI
    onwrap_uri = info['onwrap_uri']

    # Add to list
    uri_s.append(onwrap_uri)

    # Get origin URI
    origin_uri = info.get('origin_uri', None)

    # If origin URI is not empty,
    # and is not EQ onwrap URI.
    if origin_uri and (origin_uri != onwrap_uri):
        # Add to list
        uri_s.append(origin_uri)

    # Get origin attribute URI
    origin_attr_uri = info.get('origin_attr_uri', None)

    # If origin attribute URI is not empty,
    # and is not EQ onwrap URI.
    if origin_attr_uri and (origin_attr_uri != onwrap_uri):
        # Add to list
        uri_s.append(origin_attr_uri)

    # URI list
    return uri_s


def format_info_dict_uris(info):
    # Get onwrap URI
    onwrap_uri = info.get('onwrap_uri')

    # Get origin URI
    origin_uri = info.get('origin_uri', None)

    # If origin URI EQ onwrap URI
    if origin_uri == onwrap_uri:
        # Set None to not show it
        origin_uri = None

    # Get origin attribute URI
    origin_attr_uri = info.get('origin_attr_uri', None)

    # If origin attribute URI EQ onwrap URI
    if origin_attr_uri == onwrap_uri:
        # Set None to not show it
        origin_attr_uri = None

    # Get text
    uris_text = '{%s%s%s}' % (
        "'onwrap_uri': {}".format(
            repr(onwrap_uri)
        ) if onwrap_uri else '',
        ", 'origin_uri': {}".format(
            repr(origin_uri)
        ) if origin_uri else '',
        ", 'origin_attr_uri': {}".format(
            repr(origin_attr_uri)
        ) if origin_attr_uri else '',
    )

    # Return text
    return uris_text
