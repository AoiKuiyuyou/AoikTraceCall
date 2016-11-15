# coding: utf-8
"""
Package.
"""
from __future__ import absolute_import

# Local imports
from . import aoikinspectargs as _aoikinspectargs


# Support usage like:
# `from aoikinspectargs import inspect_arguments`
# instead of:
# `from aoikinspectargs.aoikinspectargs import inspect_arguments`
#
# The use of `getattr` aims to bypass `pydocstyle`'s `__all__` check.
#
# For `aoikinspectargs.aoikinspectargs`'s each public attribute name
for key in getattr(_aoikinspectargs, '__all__'):
    # Store the attribute in this module
    globals()[key] = getattr(_aoikinspectargs, key)

# Delete the module reference
del _aoikinspectargs
