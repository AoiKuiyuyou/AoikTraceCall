# coding: utf-8
from __future__ import absolute_import


def print_dict(*args):
    #
    for arg in args:
        if isinstance(arg, dict):
            #
            dict_obj = arg

            sorted_item_s = sorted(dict_obj.items(), key=(lambda x: x[0]))

            #
            for key, value in sorted_item_s:
                print('{}: {}'.format(key, repr(value)))
        else:
            print(repr(arg))


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
