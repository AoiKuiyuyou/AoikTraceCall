# coding: utf-8
from __future__ import absolute_import

# Standard imports
from functools import partial
import inspect
from pprint import pformat
import sys
import traceback
from types import FunctionType
from types import MethodType

# Internal imports
from aoiktracecall.config import get_config
from aoiktracecall.logging import print_debug
from aoiktracecall.logging import print_error
from aoiktracecall.logging import print_info
from aoiktracecall.state import count_add
from aoiktracecall.state import level_add
from aoiktracecall.state import level_set
from aoiktracecall.util import format_info_dict_uris
from aoiktracecall.util import to_origin_uri
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
        new_call = object.__getattribute__(self, _NEW_CALL_ATTR_NAME)

        res = new_call(*args, **kwargs)

        return res

    def __getitem__(self, key):
        old_call = object.__getattribute__(self, _OLD_CALL_ATTR_NAME)

        return old_call.__getitem__(key)

    def __setitem__(self, key, value):
        old_call = object.__getattribute__(self, _OLD_CALL_ATTR_NAME)

        return old_call.__setitem__(key, value)

    def __getattribute__(self, name):
        old_call = object.__getattribute__(self, _OLD_CALL_ATTR_NAME)

        return old_call.__getattribute__(name)

    def __setattr__(self, name, value):
        old_call = object.__getattribute__(self, _OLD_CALL_ATTR_NAME)

        return old_call.__setattr__(name, value)

    def __repr__(self):
        old_call = object.__getattribute__(self, _OLD_CALL_ATTR_NAME)

        return repr(old_call)

    def __str__(self):
        old_call = object.__getattribute__(self, _OLD_CALL_ATTR_NAME)

        return str(old_call)

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

        if get_config('WRAP_USING_WRAPPER_CLASS'):
            return CallWrapper(old_call, new_call)
        else:
            return new_call


class _NewStyleClass(object):

    def __new__(self):
        pass


STATICMETHOD_TYPE = type(vars(_NewStyleClass)['__new__'])

del _NewStyleClass


def is_wrappable(obj):
    return callable(obj) or isinstance(obj, STATICMETHOD_TYPE)


class ExceptionInfo(object):

    def __init__(self, exc_info):
        self.exc_info = exc_info

    def __str__(self):
        # Get message
        message = 'Exception:\n---\n{}---\n'.format(
            ''.join(traceback.format_exception(*self.exc_info)))

        # Return message
        return message

    def __repr__(self):
        return self.__str__()


#
_MAP_MODULE_OR_CLASS_TO_WRAP_INFOS = {}


#
_MAP_CALLABLE_TO_WRAP_INFOS = {}


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
            'info_type': 'callable',
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
    info.setdefault('origin_attr_class', None)

    #
    if 'attr_name' not in info:
        info['attr_name'] = func.__name__

    #
    attr_name = info['attr_name']

    #
    if 'onwrap_uri' not in info:
        #
        info['onwrap_uri'] = to_uri(
            module=module,
            attr_obj=func,
            attr_name=attr_name,
        )

    #
    info['obj'] = func

    #
    if filter is not None:
        # 7AETC
        info = filter(info)

        if not isinstance(info, dict):
            return None

    #
    wrap_info_s = _MAP_CALLABLE_TO_WRAP_INFOS.setdefault(func, [])

    #
    if wrap_info_s:
        #
        if existwrap is not None:
            # 3QWOT
            existwrap(info, wrap_info_s)

    #
    wrap_info_s.append(info)

    #
    @wrap_callable(func)
    def new_func(*args, **kwargs):
        #
        count = count_add(1)

        #
        level = level_add(1)

        # If need debug info dict's URIs
        if get_config('WRAPPER_FUNC_DEBUG_INFO_DICT_URIS'):
            # Get message
            msg = '# WRAPPER_FUNC_DEBUG_INFO_DICT_URIS: {}'.format(
                format_info_dict_uris(info)
            )

            # Print message
            print_info(msg)

        #
        info_dict = info.copy()

        info_dict.update({
            'trace_hook_type': 'pre_call',
            'level': level,
            'count': count,
            'func': func,
            'args': args,
            'kwargs': kwargs,
        })

        return_info_dict = info_dict.copy()

        #
        try:
            # 5IKXV
            handler(info_dict)
        except Exception:
            #
            error_msg = '# Error when calling pre-call handler:\n---\n{}---\n'\
                .format(
                    traceback.format_exc()
                )

            #
            print_error(error_msg)

        try:
            if func is object.__new__:
                call_result = func(args[0])
            elif func is object.__init__:
                call_result = func(args[0])
            elif isinstance(func, STATICMETHOD_TYPE):
                call_result = func.__func__(*args, **kwargs)
            else:
                call_result = func(*args, **kwargs)
        except:
            call_result = ExceptionInfo(sys.exc_info())

            raise
        finally:
            #
            return_info_dict['trace_hook_type'] = 'post_call'

            #
            return_info_dict['call_result'] = call_result

            #
            try:
                # 6VPTM
                handler(return_info_dict)
            except Exception:
                #
                error_msg = (
                    '# Error when calling post-call handler:\n---\n{}---\n'
                ).format(
                    traceback.format_exc()
                )

                #
                print_error(error_msg)

            # Decrement level
            new_level = level_add(-1)

            # If new level is not EQ expected value.
            # This is possible if `importlib.util.find_spec` is called by the
            # traced code.
            if new_level != level - 1:
                #
                msg = \
                    '# Warning: Unmatched level: {} != {}. {}'.format(
                        new_level,
                        level - 1,
                        format_info_dict_uris(info)
                    )

                # Print warning
                print_info(msg)

                # Set to the expected level
                level_set(level - 1)

        #
        return call_result

    #
    if inspect.isclass(func):
        # If is Python 2.
        # Python 2 not supports `__new__` mechanism.
        if IS_PY2:
            #
            return func

        #
        old_cls = func

        class new_cls(old_cls):

            def __new__(cls, *args, **kwargs):
                return new_func(*args, **kwargs)

        if hasattr(old_cls, '__name__'):
            new_cls.__name__ = getattr(old_cls, '__name__')

        if hasattr(old_cls, '__module__'):
            new_cls.__module__ = getattr(old_cls, '__module__')

        res_func = new_cls
    else:
        res_func = new_func

    #
    return res_func


def wrap_class_attrs(
    cls,
    filter=None,
    handler=None,
    module=None,
    class_onwrap_uri=None,
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

    # Get class origin URI
    class_origin_uri = to_uri(module=module, cls=cls)

    #
    if not class_onwrap_uri:
        class_onwrap_uri = class_origin_uri

    #
    msg = '\n# ----- Process class `{}` -----'.format(class_onwrap_uri)

    #
    print_debug(msg)

    #
    class_info = {
        'info_type': 'class',
        'module': module,
        'class': cls,
        'obj': cls,
        'onwrap_uri': class_onwrap_uri,
        'origin_uri': class_origin_uri,
        'attr_name': class_onwrap_uri.rpartition('.')[2],
        'origin_attr_uri': None,
        'origin_attr_class': None,
    }

    #
    msg = pformat(class_info, indent=4, width=1) + '\n'

    #
    print_debug(msg)

    # 5WGOF
    class_info = filter(class_info)

    if not isinstance(class_info, dict):
        return None

    #
    ex_class_info_s = _MAP_MODULE_OR_CLASS_TO_WRAP_INFOS.setdefault(
        cls, []
    )

    if ex_class_info_s:
        #
        if class_existwrap is not None:
            # 7EFWJ
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

    #
    map_attr_name_to_info = {}

    #
    map_orig_func_to_new_info = {}

    # For each class in the MRO class list, from base class to given class
    for mro_class in reversed(mro_class_s):
        if mro_class is cls:
            #
            mro_class_uri = class_onwrap_uri

            #
            msg = '\n# ---- Search class `{}` ----'.format(
                mro_class_uri
            )

            #
            print_debug(msg)
        else:
            #
            mro_class_uri = to_uri(cls=mro_class)

            #
            msg = '\n# ---- Search base class `{}` ----'.format(
                mro_class_uri
            )

            #
            print_debug(msg)

        # For the MRO class' each attribute
        for attr_name, attr_obj in sorted(
            vars(mro_class).items(), key=(lambda x: x[0])
        ):
            #
            msg = '\n# --- Attribute `{}.{}` ---\nType: {}'.format(
                mro_class_uri,
                attr_name,
                type(attr_obj),
            )

            #
            print_debug(msg)

            # If the attribute is not wrappable
            if not is_wrappable(attr_obj):
                #
                msg = 'Not wrappable.\n'

                #
                print_debug(msg)

            # If the attribute is wrappable
            else:
                #
                orig_func = get_wrapped_obj(attr_obj, default=attr_obj)

                assert orig_func is not None

                #
                existing_info = None

                #
                try:
                    existing_info_s = _MAP_CALLABLE_TO_WRAP_INFOS.get(
                        orig_func, None
                    )
                except TypeError:
                    continue

                if existing_info_s:
                    existing_info = existing_info_s[0]

                #
                if existing_info is None:
                    existing_info = map_orig_func_to_new_info.get(
                        orig_func, None
                    )

                #
                origin_attr_class = None

                #
                origin_attr_uri = None

                #
                if existing_info is not None:
                    #
                    origin_attr_class = existing_info.get(
                        'origin_attr_class', None
                    )

                    #
                    origin_attr_uri = existing_info.get(
                        'origin_attr_uri', None
                    )

                #
                if origin_attr_class is None:
                    # Get the class containing the attribute
                    origin_attr_class = mro_class

                #
                if origin_attr_uri is None:
                    #
                    origin_attr_uri = to_uri(
                        module=module,
                        cls=origin_attr_class,
                        attr_obj=orig_func,
                        attr_name=attr_name,
                    )

                #
                onwrap_uri = '{}.{}'.format(class_onwrap_uri, attr_name)

                #
                origin_uri = '{}.{}'.format(class_origin_uri, attr_name)

                #
                info = {
                    'info_type': 'class_attr',
                    'module': module,
                    'class': cls,
                    'obj': orig_func,
                    'onwrap_uri': onwrap_uri,
                    'origin_uri': origin_uri,
                    'attr_name': attr_name,
                    'origin_attr_uri': origin_attr_uri,
                    'origin_attr_class': origin_attr_class,
                }

                #
                map_attr_name_to_info[attr_name] = info

                #
                if existing_info is None:
                    map_orig_func_to_new_info[orig_func] = info

                #
                msg = 'Info:\n' + pformat(info, indent=4, width=1) + '\n'

                #
                print_debug(msg)

    #
    msg = '\n# ---- Process class `{}`\'s attributes ----\n'.format(
        class_onwrap_uri
    )

    #
    print_debug(msg)

    #
    for _, func_info in sorted(
        map_attr_name_to_info.items(), key=(lambda x: x[0])
    ):
        #
        onwrap_uri = func_info['onwrap_uri']

        #
        msg = '\n# --- Wrapper `{}` ---\nInfo:\n{}\n'.format(
            onwrap_uri,
            pformat(func_info, indent=4, width=1),
        )

        #
        print_debug(msg)

        #
        func = func_info['obj']

        try:
            new_func = wrap_call(
                func=func,
                info=func_info,
                filter=filter,
                handler=handler,
                module=module,
                existwrap=call_existwrap,
            )
        except Exception:
            #
            error_msg = (
                '# Error when wrapping class attribute:\n---\n{}---\n'
            ).format(
                traceback.format_exc()
            )

            #
            print_error(error_msg)

            #
            msg = pformat(func_info, indent=4, width=1)

            #
            print_error(msg)

            #
            continue

        cls = func_info['class']

        attr_name = func_info['attr_name']

        if new_func is not None:
            try:
                setattr(cls, attr_name, new_func)
            except Exception:
                #
                error_msg = (
                    '# Error when setting wrapper attribute:\n---\n{}---\n'
                ).format(
                    traceback.format_exc()
                )

                #
                print_error(error_msg)

                #
                msg = pformat(func_info, indent=4, width=1)

                #
                print_error(msg)

                #
                continue

    #
    msg = '# ===== Process class `{}` =====\n'.format(class_origin_uri)

    #
    print_debug(msg)

    #
    return orig_cls


def wrap_module_attrs(
    module,
    filter=None,
    handler=None,
    module_origin_uri=None,
    module_onwrap_uri=None,
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
    if not module_origin_uri:
        module_origin_uri = module.__name__

    #
    if not module_onwrap_uri:
        module_onwrap_uri = module_origin_uri

    #
    module_info = {
        'info_type': 'module',
        'module': module,
        'class': None,
        'obj': None,
        'onwrap_uri': module_onwrap_uri,
        'origin_uri': module_origin_uri,
        'attr_name': None,
        'origin_attr_uri': None,
        'origin_attr_class': None,
    }

    #
    msg = '\n# ----- Process module `{}` -----\n{}\n'.format(
        module_onwrap_uri,
        pformat(module_info, indent=4, width=1),
    )

    print_debug(msg)

    # 2D5HA
    module_info = filter(module_info)

    if not isinstance(module_info, dict):
        return None

    #
    ex_module_info_s = _MAP_MODULE_OR_CLASS_TO_WRAP_INFOS.setdefault(
        module, []
    )

    if ex_module_info_s:
        #
        if module_existwrap is not None:
            # 2A5RL
            module_existwrap(module_info, ex_module_info_s)

        #
        return None
    else:
        ex_module_info_s.append(module_info)

    #
    for mod_attr_name, mod_attr_obj in vars(module).items():
        #
        onwrap_uri = '{}.{}'.format(module_onwrap_uri, mod_attr_name)

        #
        if inspect.isclass(mod_attr_obj):
            #
            class_onwrap_uri = '{}.{}'.format(module_onwrap_uri, mod_attr_name)

            wrap_class_attrs(
                cls=mod_attr_obj,
                handler=handler,
                filter=filter,
                module=module,
                class_onwrap_uri=class_onwrap_uri,
                class_existwrap=class_existwrap,
                call_existwrap=call_existwrap,
            )
        #
        elif is_wrappable(mod_attr_obj):
            #
            msg = '\n# ----- Process callable `{}` -----'.format(onwrap_uri)

            #
            print_debug(msg)

            #
            origin_uri = to_origin_uri(
                module=module,
                attr_obj=mod_attr_obj,
                attr_name=mod_attr_name,
            )

            #
            info = {
                'info_type': 'callable',
                'module': module,
                'class': None,
                'obj': mod_attr_obj,
                'onwrap_uri': onwrap_uri,
                'origin_uri': origin_uri,
                'attr_name': mod_attr_name,
                'origin_attr_uri': None,
                'origin_attr_class': None,
            }

            #
            msg = pformat(info, indent=4, width=1) + '\n'

            #
            print_debug(msg)

            #
            if isinstance(info, dict):
                try:
                    new_func = wrap_call(
                        func=mod_attr_obj,
                        info=info,
                        filter=filter,
                        handler=handler,
                        module=module,
                        existwrap=call_existwrap,
                    )

                except Exception:
                    #
                    error_msg = (
                        '# Error when wrapping callable:\n---\n{}---\n'
                    ).format(
                        traceback.format_exc()
                    )

                    #
                    print_error(error_msg)

                    #
                    msg = pformat(info, indent=4, width=1)

                    #
                    print_error(msg)

                    #
                    continue

                if new_func is not None:
                    try:
                        setattr(module, mod_attr_name, new_func)
                    except Exception:
                        #
                        error_msg = (
                            '# Error when setting wrapper attribute:'
                            '\n---\n{}---\n'
                        ).format(
                            traceback.format_exc()
                        )

                        #
                        print_error(error_msg)

                        #
                        msg = pformat(info, indent=4, width=1)

                        #
                        print_error(msg)

                        #
                        continue
        else:
            continue

    #
    msg = '# ===== Process module `{}` =====\n'.format(module_onwrap_uri)

    #
    print_debug(msg)

    #
    return module
