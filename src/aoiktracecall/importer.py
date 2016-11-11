# coding: utf-8
from __future__ import absolute_import

# Standard imports
import imp
import sys

# Internal imports
from aoiktracecall.wrap import wrap_module


IS_PY2 = (sys.version_info[0] == 2)


def import_module(
    module_name,
    sys_path=None,
):
    #
    existing_module = sys.modules.get(module_name, None)

    if existing_module is not None:
        return existing_module

    # E.g. Module name "a.b.c" is split to three step names ['a', 'b', 'c'].
    step_name_s = module_name.split('.')

    # Parent module name in each step.
    parent_module_name = ''

    # "sys.path" list used by "imp.find_module" in each step
    sys_path_list = sys_path

    #
    for step_name in step_name_s:
        # If is the first step
        if not parent_module_name:
            current_module_name = step_name
        # If is not the first step
        else:
            current_module_name = parent_module_name + '.' + step_name

        #
        mod_obj = sys.modules.get(current_module_name, None)

        #
        if mod_obj is None:
            # Module file object returned by "imp.find_module"
            module_file = None

            try:
                # Raise ImportError
                module_file, module_dir, desc = imp.find_module(
                    step_name, sys_path_list)

                # Raise any error caused by the imported module
                mod_obj = imp.load_module(
                    step_name, module_file, module_dir, desc)
            finally:
                if module_file is not None:
                    module_file.close()

        # Use current module name as parent module name for next step
        parent_module_name = current_module_name

        # If the module is a package
        if hasattr(mod_obj, '__path__'):
            # Use its directory paths as "sys.path" list for the next step
            sys_path_list = mod_obj.__path__

    #
    return mod_obj


class WrapperLoader(object):

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


class WrapperFinder(object):

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


class TraceLoader(WrapperLoader):

    def __init__(
        self,
        filter=None,
        handler=None,
        module_spec=None,
        module_failload=None,
        module_postload=None,
        module_existwrap=None,
        class_existwrap=None,
        call_existwrap=None,
    ):
        #
        super(TraceLoader, self).__init__(module_spec)

        #
        self.trace_filter = filter

        self.trace_handler = handler

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
            super(TraceLoader, self).exec_module(module)
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
        wrap_module(
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
            module = super(TraceLoader, self).load_module(module_name)
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
        wrap_module(
            module=module,
            filter=self.trace_filter,
            handler=self.trace_handler,
            module_existwrap=self.module_existwrap,
            class_existwrap=self.class_existwrap,
            call_existwrap=self.call_existwrap,
        )

        #
        return module


class TraceFinder(WrapperFinder):

    def __init__(
        self,
        meta_path,
        loader_factory,
        filter,
        handler,
        module_preload=None,
        module_failload=None,
        module_existwrap=None,
        class_existwrap=None,
        call_existwrap=None,
    ):
        #
        super(TraceFinder, self).__init__(
            meta_path=meta_path,
            loader_factory=loader_factory,
            module_preload=module_preload,
            module_failload=module_failload,
        )

        #
        self.trace_filter = filter

        self.trace_handler = handler

        #
        for module in sys.modules.values():
            # This happens in Python 2
            if module is None:
                continue

            #
            if module.__name__ == '__main__':
                continue

            #
            wrap_module(
                module=module,
                filter=self.trace_filter,
                handler=self.trace_handler,
                module_existwrap=module_existwrap,
                class_existwrap=class_existwrap,
                call_existwrap=call_existwrap,
            )


def finder_factory(
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
    def loader_factory(module_spec):
        """
        In Python 2, "WrapperFinder" will pass None to "module_spec".
        In Python 3, "WrapperFinder" will pass the module spec found.
        """
        #
        return TraceLoader(
            filter=filter,
            handler=handler,
            module_spec=module_spec,
            module_failload=module_failload,
            module_postload=module_postload,
            module_existwrap=module_existwrap,
            class_existwrap=class_existwrap,
            call_existwrap=call_existwrap,
        )

    #
    finder = TraceFinder(
        meta_path=sys.meta_path,
        loader_factory=loader_factory,
        filter=filter,
        handler=handler,
        module_preload=module_preload,
        module_failload=module_failload,
        module_existwrap=module_existwrap,
        class_existwrap=class_existwrap,
        call_existwrap=call_existwrap,
    )

    #
    return finder
