# coding: utf-8
from __future__ import absolute_import

# Standard imports
import imp
import sys

# Internal imports
from aoiktracecall.wrap import wrap_module_attrs


# Whether is Python 2
IS_PY2 = (sys.version_info[0] == 2)


class ModuleLoader(object):

    def __init__(self, spec=None):
        #
        self.spec = spec

        #
        if not IS_PY2:
            if spec is not None:
                self.old_loader = spec.loader
            else:
                self.old_loader = None

    def load_module(self, module_name):
        """
        Python 2 only.
        """
        #
        module = imp.load_module(module_name, *self.spec)

        #
        return module

    def create_module(self, spec):
        """
        Python 3 only.
        """
        if hasattr(self.old_loader, 'create_module'):
            return self.old_loader.create_module(spec)
        else:
            return None

    def exec_module(self, module):
        """
        Python 3 only.
        """
        if self.old_loader is None:
            return module
        else:
            self.old_loader.exec_module(module)


class ModuleFinder(object):

    def __init__(
        self,
        meta_path,
        loader_factory,
        module_preload=None,
        module_failload=None,
    ):
        #
        self.meta_path = list(meta_path)

        #
        self.loader_factory = loader_factory

        #
        self.module_preload = module_preload

        #
        self.module_failload = module_failload

    def find_spec(self, fullname, path, target=None):
        #
        if self.module_preload is not None:
            self.module_preload({
                'module_name': fullname,
            })

        #
        spec = None
        for loader in self.meta_path:
            if hasattr(loader, 'find_spec'):
                spec = loader.find_spec(fullname, path, target)
                if spec is not None:
                    break

        if spec is not None:
            spec.loader = self.loader_factory(spec)
        else:
            if self.module_failload is not None:
                self.module_failload({
                    'module': None,
                    'module_name': fullname,
                })

        return spec

    def find_module(self, fullname, path=None):
        #
        if self.module_preload is not None:
            self.module_preload({
                'module_name': fullname,
            })

        #
        last_step_name = fullname.split('.')[-1]

        #
        path_list = path

        #
        try:
            spec = imp.find_module(last_step_name, path_list)
        except Exception:
            #
            if self.module_failload is not None:
                self.module_failload({
                    'module': None,
                    'module_name': fullname,
                })

            #
            raise ImportError(fullname)

        #
        return self.loader_factory(spec)


class TracedCallModuleLoader(ModuleLoader):

    def __init__(
        self,
        trace_filter=None,
        trace_handler=None,
        module_spec=None,
        module_failload=None,
        module_postload=None,
        module_existwrap=None,
        class_existwrap=None,
        call_existwrap=None,
    ):
        #
        super(TracedCallModuleLoader, self).__init__(module_spec)

        #
        self.trace_filter = trace_filter

        #
        self.trace_handler = trace_handler

        #
        self.module_failload = module_failload

        #
        self.module_postload = module_postload

        #
        self.module_existwrap = module_existwrap

        #
        self.class_existwrap = class_existwrap

        #
        self.call_existwrap = call_existwrap

    def exec_module(self, module):
        #
        try:
            super(TracedCallModuleLoader, self).exec_module(module)
        except Exception:
            #
            if self.module_failload is not None:
                self.module_failload({
                    'module_name': module.__name__,
                })

            #
            raise

        #
        if self.module_postload is not None:
            #
            self.module_postload({
                'module': module,
                'module_name': module.__name__,
            })

        #
        wrap_module_attrs(
            module=module,
            filter=self.trace_filter,
            handler=self.trace_handler,
            module_existwrap=self.module_existwrap,
            class_existwrap=self.class_existwrap,
            call_existwrap=self.call_existwrap,
        )

    def load_module(self, module_name):
        #
        try:
            module = super(TracedCallModuleLoader, self).load_module(
                module_name
            )
        except Exception:
            #
            if self.module_failload is not None:
                self.module_failload({
                    'module_name': module_name,
                })

            #
            raise

        #
        module.__name__ = module_name

        #
        if self.module_postload is not None:
            self.module_postload({
                'module': module,
                'module_name': module.__name__,
            })

        #
        wrap_module_attrs(
            module=module,
            filter=self.trace_filter,
            handler=self.trace_handler,
            module_existwrap=self.module_existwrap,
            class_existwrap=self.class_existwrap,
            call_existwrap=self.call_existwrap,
        )

        #
        return module


class TracedCallModuleFinder(ModuleFinder):

    def __init__(
        self,
        meta_path,
        loader_factory,
        trace_filter,
        trace_handler,
        module_preload=None,
        module_failload=None,
        module_existwrap=None,
        class_existwrap=None,
        call_existwrap=None,
    ):
        #
        super(TracedCallModuleFinder, self).__init__(
            meta_path=meta_path,
            loader_factory=loader_factory,
            module_preload=module_preload,
            module_failload=module_failload,
        )

        #
        self.trace_filter = trace_filter

        self.trace_handler = trace_handler

        #
        for module in sys.modules.values():
            # This happens in Python 2
            if module is None:
                continue

            #
            if module.__name__ == '__main__':
                continue

            #
            wrap_module_attrs(
                module=module,
                filter=self.trace_filter,
                handler=self.trace_handler,
                module_existwrap=module_existwrap,
                class_existwrap=class_existwrap,
                call_existwrap=call_existwrap,
            )


def module_finder_factory(
    trace_filter,
    trace_handler,
    module_preload=None,
    module_postload=None,
    module_failload=None,
    module_existwrap=None,
    class_existwrap=None,
    call_existwrap=None,
):
    # Create module loader factory
    def module_loader_factory(module_spec):
        """
        In Python 2, "ModuleFinder" will pass None to "module_spec".
        In Python 3, "ModuleFinder" will pass the module spec found.
        """
        # Create module loader
        return TracedCallModuleLoader(
            trace_filter=trace_filter,
            trace_handler=trace_handler,
            module_spec=module_spec,
            module_failload=module_failload,
            module_postload=module_postload,
            module_existwrap=module_existwrap,
            class_existwrap=class_existwrap,
            call_existwrap=call_existwrap,
        )

    # Create module finder
    module_finder = TracedCallModuleFinder(
        meta_path=sys.meta_path,
        loader_factory=module_loader_factory,
        trace_filter=trace_filter,
        trace_handler=trace_handler,
        module_preload=module_preload,
        module_failload=module_failload,
        module_existwrap=module_existwrap,
        class_existwrap=class_existwrap,
        call_existwrap=call_existwrap,
    )

    # Return module finder
    return module_finder
