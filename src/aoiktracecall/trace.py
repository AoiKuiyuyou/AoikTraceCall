# coding: utf-8
from __future__ import absolute_import

# Standard imports
from functools import partial
import inspect
import sys
from types import ModuleType

# Internal imports
from aoiktracecall.config import get_config
from aoiktracecall.importer import module_finder_factory
from aoiktracecall.logging import print_debug
from aoiktracecall.logging import print_info
from aoiktracecall.plugin.exception_plugin import reject_exception
from aoiktracecall.plugin.printing_plugin import printing_filter
from aoiktracecall.plugin.printing_plugin import printing_handler
from aoiktracecall.plugin.showhide_plugin import showhide_filter
from aoiktracecall.plugin.showhide_plugin import showhide_handler
from aoiktracecall.spec import parse_specs
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
from aoiktracecall.util import chain_filters
from aoiktracecall.util import format_func_name
from aoiktracecall.wrap import wrap_call
from aoiktracecall.wrap import wrap_class_attrs
from aoiktracecall.wrap import wrap_module_attrs


def create_and_hook_module_finder(
    trace_filter,
    trace_handler,
    module_preload=None,
    module_postload=None,
    module_failload=None,
    module_existwrap=None,
    class_existwrap=None,
    call_existwrap=None,
):
    """
    Create and hook module finder for tracing callables.

    The created module finder will use given filter function to filter each \
        imported module's callables. Callables accepted by the filter will be
        wrapped for tracing calls. When the wrapper is called, given handler
        function will be called. The handler function can do arbitrary things,
        e.g. printing the call arguments and result value.

    :param trace_filter: Trace filter function.

    It is called to decide whether to trace an object.

    Called at 2D5HA to filter a module.
    Called at 5WGOF to filter a class.
    Called at 7AETC to filter a callable.

    :param trace_handler: Trace handler function.

    It is called before and after a traced callable is called.

    Called at 5IKXV before a traced callable is called.
    Called at 6VPTM after a traced callable is called.

    :param module_preload: Module pre-load callback.

    :param module_postload: Module post-load callback.

    :param module_failload: Module fail-load callback.

    :param module_existwrap: Module exist-wrapper callback. Called at 2A5RL.

    :param class_existwrap: Class exist-wrapper callback. Called at 7EFWJ.

    :param call_existwrap: Function exist-wrapper callback. Called at 3QWOT.

    :return: None.
    """
    # Set global filter function
    filter_set(trace_filter)

    # Set global handler function
    handler_set(trace_handler)

    # Set global module pre-load callback
    module_preload_set(module_preload)

    # Set global module post-load callback
    module_postload_set(module_postload)

    # Set global module fail-load callback
    module_failload_set(module_failload)

    # Set global module exist-wrapper callback
    module_existwrap_set(module_existwrap)

    # Set global class exist-wrapper callback
    class_existwrap_set(class_existwrap)

    # Set global function exist-wrapper callback
    call_existwrap_set(call_existwrap)

    # Create module finder
    module_finder = module_finder_factory(
        trace_filter=trace_filter,
        trace_handler=trace_handler,
        module_preload=module_preload,
        module_postload=module_postload,
        module_failload=module_failload,
        module_existwrap=module_existwrap,
        class_existwrap=class_existwrap,
        call_existwrap=call_existwrap,
    )

    # Hook module finder
    sys.meta_path = [module_finder]


def trace_calls_in_obj(
    obj,
    info=None,
    filter=None,
    handler=None,
    module=None,
    module_existwrap=None,
    class_existwrap=None,
    call_existwrap=None,
):
    """
    Trace callables in given module, class, or function.

    :param obj: Module, class, or function.

    :param info: Info dict.

    :param filter: Filter function. Default is use global one.

    :param handler: Handler function. Default is use global one.

    :param module: Containing module for class or function. Unused if given \
        object is module.

    :param module_existwrap: Module exist-wrapper callback. Default is use \
        global one.

    :param class_existwrap: Class exist-wrapper callback. Default is use \
        global one.

    :param call_existwrap: Function exist-wrapper callback. Default is use \
        global one.

    :return: Wrapped object.
    """
    # If filter function is not given
    if filter is None:
        # Use global one
        filter = filter_get()

    # If handler function is not given
    if handler is None:
        # Use global one
        handler = handler_get()

    # If module exist-wrapper callback is not given
    if module_existwrap is None:
        # Use global one
        module_existwrap = module_existwrap_get()

    # If class exist-wrapper callback is not given
    if class_existwrap is None:
        class_existwrap = class_existwrap_get()

    # If function exist-wrapper callback is not given
    if call_existwrap is None:
        # Use global one
        call_existwrap = call_existwrap_get()

    # If given object is module
    if isinstance(obj, ModuleType):
        # Delegate call to `wrap_module_attrs`
        return wrap_module_attrs(
            module=obj,
            filter=filter,
            handler=handler,
            module_existwrap=module_existwrap,
            class_existwrap=class_existwrap,
            call_existwrap=call_existwrap,
        )

    # If given object is class
    elif inspect.isclass(obj):
        # Delegate call to `wrap_class_attrs`
        return wrap_class_attrs(
            cls=obj,
            filter=filter,
            handler=handler,
            module=module,
            class_existwrap=class_existwrap,
            call_existwrap=call_existwrap,
        )

    # If given object is not module or class
    else:
        # Delegate call to `wrap_call`
        return wrap_call(
            func=obj,
            info=info,
            filter=filter,
            handler=handler,
            module=module,
            existwrap=call_existwrap,
        )


def trace_calls_in_this_module():
    """
    Trace callables in caller's module.

    This function should be called at the end of the main module, after all
    callables in the main module are defined, before the main function is
    called to run the application logic. Calling this function is needed
    because at the time `create_and_hook_module_finder` is called, the main
    module has been imported already, so callables in the main module will not
    be traced by `create_and_hook_module_finder`.

    :return: Wrapped object.
    """
    # Get caller info
    info = inspect.stack()[1]

    # Get caller frame
    frame = info[0]

    # Get caller function's containing module
    func_module = inspect.getmodule(frame)

    # Delegate call to `trace_calls_in_obj`
    trace_calls_in_obj(func_module)


def trace_calls_in_specs(
    specs,
    printing_handler_filter_func=None,
):
    """
    Trace callables according to given specs.

    :param specs: Specs.

    :param printing_handler_filter_func: `printing_handler`'s filter function.

    :return: None.
    """
    # Print message
    print_debug(
        format_func_name(
            '+ trace_calls_in_specs', level_step_before=1, figlet=True
        )
    )

    # Print message
    print_debug('\n# ----- Parse specs -----')

    # Parse specs
    parsed_specs = parse_specs(specs)

    # For each parsed spec item
    for uri, opts_dict in parsed_specs.items():
        # Print the parsed spec item
        print_debug((uri, opts_dict))

    # Create module pre-load callback
    def module_preload(info):
        module_name = info['module_name']

        print_info(
            format_func_name(
                '+ {}'.format(module_name), level_step_before=1, count=False
            )
        )

    # Create module fail-load callback
    def module_failload(info):
        module_name = info['module_name']

        print_info(
            format_func_name(
                '! {}'.format(module_name), level_step_after=-1, count=False
            )
        )

    # Create module post-load callback
    def module_postload(info):
        module_name = info['module_name']

        print_info(
            format_func_name(
                '- {}'.format(module_name), level_step_after=-1, count=False
            )
        )

    def existwrap(info, ex_info_s):
        # Get info type.
        # Allowed values: 'module', 'class', 'class_attr', 'callable'.
        info_type = info['info_type']

        #
        if info_type != 'class_attr':
            # Get onwrap URI
            onwrap_uri = info['onwrap_uri']

            # Get the first existing info
            ex_info = ex_info_s[0]

            # If info type is `callable`
            if info_type == 'callable':
                # Print message
                print_debug('@@: {0} == {1}'.format(
                    onwrap_uri, ex_info['onwrap_uri'])
                )

            # If info type is not `callable`
            else:
                # Print message
                print_debug('!!: {0} == {1}'.format(
                    onwrap_uri, ex_info['onwrap_uri'])
                )

    # Create filter function
    def showhide_filter_wrapper(info):
        # Get info type.
        # Allowed values: 'module', 'class', 'class_attr', 'callable'.
        info_type = info['info_type']

        # Get onwrap URI
        onwrap_uri = info['onwrap_uri']

        # Get origin URI
        origin_uri = info.get('origin_uri', None)

        # Get origin attribute URI
        origin_attr_uri = info.get('origin_attr_uri', None)

        # If info type is `class_attr`
        if info_type == 'class_attr':
            # If origin attribute URI and onwrap URI are different
            if origin_attr_uri and (origin_attr_uri != onwrap_uri):
                # If config `WRAP_BASE_CLASS_ATTRIBUTES` is disabled
                if not get_config('WRAP_BASE_CLASS_ATTRIBUTES'):
                    # Print message
                    print_debug(
                        '!: {0} == {1}'.format(onwrap_uri, origin_attr_uri)
                    )

                    # Return False to not trace the item
                    return False

        # If info type is not `class_attr`
        else:
            # If origin URI and onwrap URI are different
            if origin_uri and (origin_uri != onwrap_uri):
                # Print message
                print_debug('!: {0} == {1}'.format(onwrap_uri, origin_uri))

                # Return False to not trace the item
                return False

        # Delegate call to `showhide_filter`
        info = showhide_filter(info=info, parsed_specs=parsed_specs)

        #
        print_debug('{0}: {1}'.format(
            '@' if isinstance(info, dict) else '!',
            onwrap_uri if (onwrap_uri == origin_uri or not origin_uri) else
            '{} == {}'.format(onwrap_uri, origin_uri),
        ))

        #
        return info

    # Create trace filter
    trace_filter = chain_filters([
        reject_exception,
        showhide_filter_wrapper,
        partial(printing_filter, parsed_specs=parsed_specs),
    ])

    # Create trace handler
    trace_handler = chain_filters([
        showhide_handler,
        partial(
            printing_handler,
            filter_func=printing_handler_filter_func,
        ),
    ])

    # Create and hook module finder for tracing callables
    create_and_hook_module_finder(
        trace_filter=trace_filter,
        trace_handler=trace_handler,
        module_preload=module_preload,
        module_postload=module_postload,
        module_failload=module_failload,
        module_existwrap=existwrap,
        class_existwrap=existwrap,
        call_existwrap=existwrap,
    )

    # Print message
    print_debug(
        format_func_name(
            '- trace_calls_in_specs', level_step_after=-1, figlet=True
        )
    )
