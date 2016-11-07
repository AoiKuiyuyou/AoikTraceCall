# coding: utf-8
from __future__ import absolute_import

# Standard imports
from functools import partial
import inspect
import sys
import traceback
from types import FunctionType
from types import MethodType

# Internal imports
from aoiktracecall.config import get_config
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


def get_wrapped_obj(wrapper, default=None):
    try:
        return object.__getattribute__(wrapper, _OLD_CALL_ATTR_NAME)
    except AttributeError:
        return default


def wrap_callable(old_call, new_call=None):
    # If argument `new_call` is not given.
    # It means this function is used as parameterized decorator.
    if new_call is None:
        return partial(wrap_callable, old_call)

    # If argument `new_call` is given
    else:
        object.__setattr__(new_call, _OLD_CALL_ATTR_NAME, old_call)

        if get_config('WRAP_USING_CALL_WRAPPER_CLASS'):
            return CallWrapper(old_call, new_call)
        else:
            return new_call


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
_MAP_ORIG_OBJ_TO_WRAP_INFO = {}


#
_default_filter = (lambda info: info)


_default_handler = (lambda info: info)


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
    func = get_wrapped_obj(func, default=func)

    #
    if get_wrapped_obj(func, default=None) is not None:
        raise ValueError(func)

    #
    if filter is None:
        filter = _default_filter

    #
    if handler is None:
        handler = _default_handler

    #
    if info is None:
        info = {
            'uri_type': 'object',
        }

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
    info['obj'] = func

    #
    if filter is not None:
        info = filter(info)

        if not isinstance(info, dict):
            return None

    #
    wrap_info_s = _MAP_ORIG_OBJ_TO_WRAP_INFO.setdefault(func, [])

    wrap_info_s.append(info)

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
    return res_func


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

    #
    print('\n# ----- Process class `{}` -----'.format(class_uri))

    #
    class_info = {
        'uri_type': 'class',
        'uri': class_uri,
        'obj': cls,
        'class': cls,
        'module': module,
    }

    #
    class_info = filter(class_info)

    if not isinstance(class_info, dict):
        return None

    #
    ex_class_info_s = _MAP_ORIG_OBJ_TO_WRAP_INFO.setdefault(cls, [])

    if ex_class_info_s:
        #
        if class_existwrap is not None:
            class_existwrap(class_info, ex_class_info_s)

        #
        return None
    else:
        ex_class_info_s.append(class_info)

    #
    if IS_PY2:
        mro_class_s = list(cls.__bases__)

        mro_class_s.insert(0, cls)
    else:
        mro_class_s = cls.__mro__

    func_infos_dict = {}

    # For each MRO class, from base class to subclass
    for mro_cls in reversed(mro_class_s):
        if mro_cls is cls:
            print('\n# ---- Search class `{}` ----'.format(
                class_uri
            ))
        else:
            print('\n# ---- Search base class `{}` ----'.format(
                to_uri(cls=mro_cls))
            )

        # For the MRO class' each attribute
        for attr_name, attr_obj in sorted(
            vars(mro_cls).items(), key=(lambda x: x[0])
        ):
            #
            if attr_names:
                if attr_name not in attr_names:
                    continue

            #
            if cls.__name__ == 'ExtendCacheResolver' and attr_name == 'query':
                print('7KXYW: MRO_CLS:', mro_cls)

            # If the attribute is wrappable
            if is_wrappable(attr_obj):
                #
                orig_func = get_wrapped_obj(attr_obj, default=attr_obj)

                assert orig_func is not None

                existing_info_s = _MAP_ORIG_OBJ_TO_WRAP_INFO.setdefault(
                    orig_func, []
                )

                if existing_info_s:
                    existing_info = existing_info_s[0]
                else:
                    existing_info = None

                # If existing info is not found
                if existing_info is None:
                    containing_class = mro_cls

                    origin_uri = to_uri(
                        module=module,
                        cls=containing_class,
                        attr_obj=attr_obj,
                        attr_name=attr_name,
                    )

                # If existing info is found
                else:
                    #
                    origin_uri = existing_info.get('origin_uri', None)

                    if origin_uri is None:
                        origin_uri = existing_info['uri']

                        assert origin_uri

                    #
                    containing_class = existing_info.get('mro_cls', None)

                    if containing_class is None:
                        containing_class = mro_cls

                #
                attr_obj_uri = '{}.{}'.format(class_uri, attr_name)

                #
                info = {
                    'uri_type': 'class_attr',
                    'module': module,
                    # The subclass
                    'class': cls,
                    # The class containing the attribute
                    'mro_cls': containing_class,
                    'obj': orig_func,
                    'uri': attr_obj_uri,
                    'origin_uri': origin_uri,
                    'name': attr_name,
                }

                # 3YWC7
                info = filter(info)

                if isinstance(info, dict):
                    func_infos_dict[attr_name] = info

                    if existing_info is None:
                        existing_info_s.append(info)

    #
    print('\n# ---- Wrap class `{}`\'s attributes ----'.format(class_uri))

    for _, func_info in sorted(
        func_infos_dict.items(), key=(lambda x: x[0])
    ):
        cls = func_info['class']

        func = func_info['obj']

        attr_name = func_info['name']

        access_uri = func_info['uri']

        origin_uri = func_info['origin_uri']

        if access_uri == origin_uri:
            print('@: {}'.format(access_uri))
        else:
            print('@: {} == {}'.format(
                access_uri, origin_uri)
            )

        try:
            # Filter is called at 3YWC7 so do not pass in filter here
            new_func = wrap_call(
                func=func,
                info=func_info,
                handler=handler,
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
    print('# ===== Process class `{}` =====\n'.format(class_uri))

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
        'uri_type': 'module',
        'uri': module_uri,
        'module': module,
    }

    #
    print('\n# ----- Process module `{}` -----'.format(module_uri))

    #
    module_info = filter(module_info)

    if not isinstance(module_info, dict):
        return None

    #
    ex_module_info_s = _MAP_ORIG_OBJ_TO_WRAP_INFO.setdefault(module, [])

    if ex_module_info_s:
        #
        if module_existwrap is not None:
            module_existwrap(module_info, ex_module_info_s)

        #
        return None
    else:
        ex_module_info_s.append(module_info)

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
            print(
                '\n# ----- Process callable `{}` -----'.format(attr_obj_uri)
            )

            #
            info = {
                'uri_type': 'object',
                'module': module,
                'class': None,
                'mro_cls': None,
                'uri': attr_obj_uri,
                'name': mod_attr_name,
                'obj': mod_attr_obj,
            }

            info = filter(info)

            if isinstance(info, dict):
                try:
                    new_func = wrap_call(
                        func=mod_attr_obj,
                        info=info,
                        handler=handler,
                        filter=None,
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
    print('# ===== Process module `{}` =====\n'.format(module_uri))

    #
    return module
