# coding: utf-8
from __future__ import absolute_import

# Standard imports
import inspect
import sys
from types import ModuleType

# Internal imports
from aoiktracecall.figlet import print_text
from aoiktracecall.filter.factory import filter_factory
from aoiktracecall.handler.factory import handler_factory
from aoiktracecall.importer import finder_factory
from aoiktracecall.state import call_existwrap_get
from aoiktracecall.state import call_existwrap_set
from aoiktracecall.state import class_existwrap_get
from aoiktracecall.state import class_existwrap_set
from aoiktracecall.state import filter_get
from aoiktracecall.state import filter_set
from aoiktracecall.state import handler_get
from aoiktracecall.state import handler_set
from aoiktracecall.state import module_existwrap_get
from aoiktracecall.state import module_existwrap_set
from aoiktracecall.state import module_failload_set
from aoiktracecall.state import module_postload_set
from aoiktracecall.state import module_preload_set
from aoiktracecall.wrap import wrap_call
from aoiktracecall.wrap import wrap_class
from aoiktracecall.wrap import wrap_module


def trace_calls(
    specs,
    filter,
    handler,
    module_preload=None,
    module_postload=None,
    module_failload=None,
    module_existwrap=None,
    class_existwrap=None,
    call_existwrap=None,
):
    #
    filter_set(filter)

    #
    handler_set(handler)

    #
    module_preload_set(module_preload)

    #
    module_postload_set(module_postload)

    #
    module_failload_set(module_failload)

    #
    module_existwrap_set(module_existwrap)

    #
    class_existwrap_set(class_existwrap)

    #
    call_existwrap_set(call_existwrap)

    #
    finder = finder_factory(
        filter=filter,
        handler=handler,
        module_preload=module_preload,
        module_postload=module_postload,
        module_failload=module_failload,
        module_existwrap=module_existwrap,
        class_existwrap=class_existwrap,
        call_existwrap=call_existwrap,
    )

    #
    sys.meta_path = [finder]


def trace_calls_easily(specs, **kwargs):
    #
    print_text('+ trace_calls_easily', level_step_before=1, figlet=True)

    #
    def module_preload(info):
        module_name = info['module_name']

        print_text(
            '+ * {}'.format(module_name), level_step_before=1, count=False)

    #
    def module_failload(info):
        module_name = info['module_name']

        print_text(
            '! * {}'.format(module_name), level_step_after=-1, count=False)

    #
    def module_postload(info):
        module_name = info['module_name']

        print_text(
            '- * {}'.format(module_name), level_step_after=-1, count=False)

    #
    def existwrap(info):
        ex_info = info['ex_info']

        uri = info['uri']

        ex_uri = ex_info['uri']

        if uri != ex_uri:
            print('Exists: {} == {}'.format(uri, ex_uri))

    #
    showhide_filter = dict(
        specs=specs,
    )

    showhide_filter_kwargs = kwargs.get('showhide_filter', None)

    if showhide_filter_kwargs is not None:
        showhide_filter.update(showhide_filter_kwargs)

    #
    def printing_handler_pre_handler(info):
        return info

    #
    trace_calls(
        specs=specs,
        filter=filter_factory(
            regex_attr_filter={
                'specs': [
                    '.+[.]__getattr__',
                    '.+[.]__getattribute__',
                    '.+[.]__new__',
                    '.+[.]__str__',
                    '.+[.]__repr__',
                    '.+[.]__hash__',
                    '.+[.]__format__',
                    '.+[.]copy',
                ],
                'allow': False,
            },
            exception_filter=True,
            showhide_filter=showhide_filter,
        ),
        handler=handler_factory(
            showhide_handler=True,
            printing_handler={
                'pre_handler': printing_handler_pre_handler,
            },
        ),
        module_preload=module_preload,
        module_postload=module_postload,
        module_failload=module_failload,
        module_existwrap=existwrap,
        class_existwrap=existwrap,
    )

    #
    parsed_specs = showhide_filter['parsed_specs']

    #
    print('\n# Parsed specs:')

    for uri, opts_dict in parsed_specs.items():
        print((uri, opts_dict))

    #
    print_text('- trace_calls_easily', level_step_after=-1, figlet=True)


def trace_easily(
    obj,
    info=None,
    filter=None,
    handler=None,
    module=None,
    class_uri=None,
    attr_names=None,
    module_existwrap=None,
    class_existwrap=None,
    call_existwrap=None,
):
    #
    if filter is None:
        filter = filter_get()

    #
    if handler is None:
        handler = handler_get()

    #
    if module_existwrap is None:
        module_existwrap = module_existwrap_get()

    #
    if class_existwrap is None:
        class_existwrap = class_existwrap_get()

    #
    if call_existwrap is None:
        call_existwrap = call_existwrap_get()

    #
    if isinstance(obj, ModuleType):
        return wrap_module(
            module=obj,
            filter=filter,
            handler=handler,
            module_existwrap=module_existwrap,
            class_existwrap=class_existwrap,
            call_existwrap=call_existwrap,
        )
    elif inspect.isclass(obj):
        return wrap_class(
            cls=obj,
            filter=filter,
            handler=handler,
            module=module,
            class_uri=class_uri,
            attr_names=attr_names,
            class_existwrap=class_existwrap,
            call_existwrap=call_existwrap,
        )
    else:
        return wrap_call(
            func=obj,
            info=info,
            filter=filter,
            handler=handler,
            module=module,
            existwrap=call_existwrap,
        )


def trace_main_module():
    return trace_easily(
        sys.modules['__main__'],
    )
