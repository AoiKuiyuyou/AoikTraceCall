# coding: utf-8
from __future__ import absolute_import

# Standard imports
import inspect
import sys
import traceback
from types import FunctionType
from types import MethodType

# Internal imports
from aoiktracecall.logging import print_log
from aoiktracecall.state import count_add
from aoiktracecall.state import level_add
from aoiktracecall.util import to_uri


IS_PY2 = sys.version_info[0] == 2


_OLD_CALL_ATTR_NAME = '__old_call_0123456789__'

_NEW_CALL_ATTR_NAME = '__new_call_0123456789__'

_METHOD_DESCRIPTOR_TYPE = type(dict.__getitem__)

_WRAPPER_DESCRIPTOR_TYPE = type(dict.__setitem__)


class CallWrapper(object):

    def __init__(self, old_call, new_call):
        object.__setattr__(self, _OLD_CALL_ATTR_NAME, old_call)

        object.__setattr__(self, _NEW_CALL_ATTR_NAME, new_call)

    def __call__(self, *args, **kwargs):
        new_call = object.__getattribute__(
            self, _NEW_CALL_ATTR_NAME)
        res = new_call(*args, **kwargs)
        return res

    def __getitem__(self, key):
        old_call = object.__getattribute__(
            self, _OLD_CALL_ATTR_NAME)

        return old_call.__getitem__(key)

    def __setitem__(self, key, value):
        old_call = object.__getattribute__(
            self, _OLD_CALL_ATTR_NAME)

        return old_call.__setitem__(key, value)

    def __getattribute__(self, name):
        old_call = object.__getattribute__(
            self, _OLD_CALL_ATTR_NAME)

        return old_call.__getattribute__(name)

    def __setattr__(self, name, value):
        old_call = object.__getattribute__(
            self, _OLD_CALL_ATTR_NAME)

        return old_call.__setattr__(name, value)

    def __get__(self, obj, cls=None):
        old_call = object.__getattribute__(
            self, _OLD_CALL_ATTR_NAME)

        if isinstance(
                old_call, (
                    FunctionType,
                    MethodType,
                    _METHOD_DESCRIPTOR_TYPE,
                    _WRAPPER_DESCRIPTOR_TYPE)):
            is_func = True
        else:
            is_func = False

        #
        if is_func:
            if obj is None:
                if IS_PY2:
                    methodtype_args = (self, None, cls)

                    method = MethodType(*methodtype_args)

                    return method
                else:
                    return self
            else:
                if IS_PY2:
                    methodtype_args = (self, obj, cls)
                else:
                    methodtype_args = (self, obj)

                method = MethodType(*methodtype_args)

                return method
        else:
            return self


def get_wrapped_obj(wrapper):
    return object.__getattribute__(wrapper, _OLD_CALL_ATTR_NAME)


def wrap_callable(old_call, new_call=None):
    if new_call is not None:
        return CallWrapper(old_call, new_call)
    else:
        # Used as parameterized decorator.

        def next_deco(new_call):
            return CallWrapper(old_call, new_call)

        return next_deco


def is_wrappable(obj):
    return callable(obj)


class ExceptionInfo(object):

    def __init__(self, exc_info):
        self.exc_info = exc_info

    def __str__(self):
        # Get message
        message = '# Error\n---\n{}---\n'.format(
            ''.join(traceback.format_exception(*self.exc_info)))

        # Return message
        return message

    def __repr__(self):
        return self.__str__()


#
_default_filter = (lambda info: info)


_default_handler = (lambda info: info)


#
_WRAPPED_FUNC_DICT = {}


#
def wrapped_func_get(func, default=None):
    return _WRAPPED_FUNC_DICT.get(id(func), None)


#
def wrap_call(
    func,
    info=None,
    filter=None,
    handler=None,
    module=None,
    existwrap=None,
):
    #
    if not is_wrappable(func):
        return None

    #
    if isinstance(func, CallWrapper):
        #
        orig_func = get_wrapped_obj(func)

        #
        if isinstance(orig_func, CallWrapper):
            raise ValueError(func)

        #
        func = orig_func

    #
    if filter is None:
        filter = _default_filter

    #
    if handler is None:
        handler = _default_handler

    #
    if info is None:
        info = {}

    #
    if 'module' in info:
        if module is not info['module']:
            raise ValueError(module)
    else:
        if module is not None:
            info['module'] = module
        else:
            module_name = getattr(func, '__module__', None)

            if isinstance(module_name, str):
                #
                module = sys.modules.get(module_name, None)

                #
                if module is not None:
                    info['module'] = module

    #
    info.setdefault('class', None)

    #
    info.setdefault('mro_cls', None)

    #
    if 'name' not in info:
        info['name'] = func.__name__

    #
    attr_name = info['name']

    #
    if 'uri' not in info:
        #
        info['uri'] = to_uri(
            module=module,
            attr_obj=func,
            attr_name=attr_name,
        )

    #
    if filter is not None:
        info = filter(info)

        if not isinstance(info, dict):
            return None

    #
    @wrap_callable(func)
    def new_func(*args, **kwargs):
        #
        count = count_add(1)

        #
        level = level_add(1)

        #
        info_dict = info.copy()

        info_dict.update({
            'type': 'call',
            'level': level,
            'count': count,
            'func': func,
            'args': args,
            'kwargs': kwargs,
        })

        return_info_dict = info_dict.copy()

        #
        try:
            handler(info_dict)
        except Exception:
            #
            print_log('# Error (4RDGC)\n---\n{}---\n'.format(
                traceback.format_exc()))

        res_is_returned = False

        try:
            if func is object.__new__:
                res = func(args[0])
            elif func is object.__init__:
                res = func(args[0])
            else:
                res = func(*args, **kwargs)
            res_is_returned = True
        finally:
            #
            if not res_is_returned:
                #
                res = ExceptionInfo(sys.exc_info())

            #
            return_info_dict['type'] = 'return'
            return_info_dict['return'] = res

            #
            try:
                handler(return_info_dict)
            except Exception:
                #
                print_log('# Error (52JKO)\n---\n{}---\n'.format(
                    traceback.format_exc()))

            #
            level_add(-1)

        #
        return res

    #
    if inspect.isclass(func):
        old_cls = func

        class new_cls(old_cls):

            def __new__(cls, *args, **kwargs):
                return new_func(*args, **kwargs)

        res_func = new_cls
    else:
        res_func = new_func

    #
    _WRAPPED_FUNC_DICT[id(func)] = res_func

    _WRAPPED_FUNC_DICT[id(res_func)] = res_func

    #
    return res_func


_WRAPPED_MODULE_AND_CLASS_DICT = {}


def wrap_class(
    cls,
    filter=None,
    handler=None,
    module=None,
    class_uri=None,
    attr_names=None,
    class_existwrap=None,
    call_existwrap=None,
):
    #
    orig_cls = cls

    #
    if filter is None:
        filter = _default_filter

    #
    if handler is None:
        handler = _default_handler

    #
    if class_uri is None:
        class_uri = to_uri(
            module=module,
            cls=cls,
        )

    if class_uri is None:
        class_uri = ''

    #
    class_info = {
        'uri': class_uri,
        'class': cls,
    }

    #
    class_info = filter(class_info)

    if not isinstance(class_info, dict):
        return None

    #
    ex_class_info = _WRAPPED_MODULE_AND_CLASS_DICT.get(cls, None)

    if ex_class_info is not None:
        #
        if class_existwrap is not None:
            class_info['ex_info'] = ex_class_info

            class_existwrap(info=class_info)

        #
        return None
    else:
        _WRAPPED_MODULE_AND_CLASS_DICT[cls] = class_info

    #
    mro_class_s = getattr(cls, '__mro__', None)

    if mro_class_s is None:
        mro_class_s = [cls]
    else:
        mro_class_s = reversed(mro_class_s)

    func_infos_dict = {}

    for mro_cls in mro_class_s:
        for attr_name, attr_obj in vars(mro_cls).items():
            #
            if attr_names:
                if attr_name not in attr_names:
                    continue

            #
            if is_wrappable(attr_obj):
                #
                if isinstance(attr_obj, CallWrapper):
                    orig_func = get_wrapped_obj(attr_obj)
                else:
                    orig_func = attr_obj

                #
                existing_info = func_infos_dict.get(attr_name, None)

                if existing_info is None:
                    existing_orig_func = None
                else:
                    existing_attr_obj = existing_info['_attr_obj']

                    #
                    if isinstance(existing_attr_obj, CallWrapper):
                        existing_orig_func = get_wrapped_obj(existing_attr_obj)
                    else:
                        existing_orig_func = existing_attr_obj

                #
                if orig_func == existing_orig_func:
                    continue

                #
                attr_obj_uri = '{}.{}'.format(class_uri, attr_name)

                #
                info = {
                    'module': module,
                    'class': cls,
                    'mro_cls': mro_cls,
                    '_attr_obj': orig_func,
                    'uri': attr_obj_uri,
                    'name': attr_name,
                }

                info = filter(info)

                if isinstance(info, dict):
                    func_infos_dict[attr_name] = info

    #
    for func_info in func_infos_dict.values():
        cls = func_info['class']

        func = func_info.pop('_attr_obj')

        attr_name = func_info['name']

        try:
            new_func = wrap_call(
                func=func,
                info=func_info,
                handler=handler,
                filter=filter,
                module=module,
                existwrap=call_existwrap,
            )
        except Exception:
            print_log('# Error (6YAY2)\n---\n{}---\n'.format(
                traceback.format_exc()))
            continue

        if new_func is not None:
            try:
                setattr(cls, attr_name, new_func)
            except Exception:
                print_log('# Error (7ABY2)\n---\n{}---\n'.format(
                    traceback.format_exc()))
                continue

    #
    return orig_cls


def wrap_module(
    module,
    filter=None,
    handler=None,
    module_uri=None,
    module_existwrap=None,
    class_existwrap=None,
    call_existwrap=None,
):
    #
    if filter is None:
        filter = _default_filter

    #
    if handler is None:
        handler = _default_handler

    #
    if not module_uri:
        module_uri = module.__name__

    #
    module_info = {
        'uri': module_uri,
    }

    #
    module_info = filter(module_info)

    if not isinstance(module_info, dict):
        return None

    #
    ex_module_info = _WRAPPED_MODULE_AND_CLASS_DICT.get(module, None)

    if ex_module_info is not None:
        #
        if module_existwrap is not None:
            module_info['ex_info'] = ex_module_info

            module_existwrap(info=module_info)

        #
        return None
    else:
        _WRAPPED_MODULE_AND_CLASS_DICT[module] = module_info

    #
    for mod_attr_name, mod_attr_obj in vars(module).items():
        #
        attr_obj_uri = '{}.{}'.format(
            module_uri, mod_attr_name)

        #
        if inspect.isclass(mod_attr_obj):
            #
            class_uri = '{}.{}'.format(module_uri, mod_attr_name)

            #
            wrap_class(
                cls=mod_attr_obj,
                handler=handler,
                filter=filter,
                module=module,
                class_uri=class_uri,
                class_existwrap=class_existwrap,
                call_existwrap=call_existwrap,
            )
        #
        elif is_wrappable(mod_attr_obj):
            #
            info = {
                'module': module,
                'class': None,
                'mro_cls': None,
                'uri': attr_obj_uri,
                'name': mod_attr_name,
            }

            info = filter(info)

            if isinstance(info, dict):
                try:
                    new_func = wrap_call(
                        func=mod_attr_obj,
                        info=info,
                        handler=handler,
                        filter=filter,
                        module=module,
                        existwrap=call_existwrap,
                    )

                except Exception:
                    print_log('# Error (3JA9H)\n---\n{}---\n'.format(
                        traceback.format_exc()))
                    continue

                if new_func is not None:
                    try:
                        setattr(module, mod_attr_name, new_func)
                    except Exception:
                        print_log('# Error (4BNWG)\n---\n{}---\n'.format(
                            traceback.format_exc()))
                        continue
        else:
            continue

    #
    return module
