""" Import utility functions. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


__all__ = []

import sys
import pkgutil
import importlib
import types


__all__.append("export")
def export(obj):
    """ Export the given object by appending it's name to the modules __all__"""

    mod = sys.modules[obj.__module__]
    if hasattr(mod, "__all__"):
        if not obj.__name__ in mod.__all__:
            mod.__all__.append(obj.__name__)
    else:
        mod.__all__ = [obj.__name__]

    return obj

@export
def import_submodules(package_name, recursive=False):
    """ Import submodules and return a dictionary of name:module """

    package = sys.modules[package_name]
    func = pkgutil.walk_packages if recursive else pkgutil.iter_modules

    return {
        name: importlib.import_module(package_name + "." + name)
        for (loader, name, ispkg) in func(package.__path__)
    }

@export
def import_submodules_symbols(package_name, symbol, recursive=False):
    """ Return a list of the specified symbols from all loaded modules. """
    submodules = import_submodules(package_name, recursive)
    
    results = []
    for name in submodules:
        value = getattr(submodules[name], symbol, None)
        if(value):
            results.append(value)

    return results

@export
def import_submodules_symbolref(package_name, symbol, recursive=False):
    """ For each submodule, return a list containing the objects referred
        to by a given symbol.  If the symbol's value is not a list form, it
        will be made into a list for.  Then for each item in the list,
        if it is a string, it will refer to the name of an object in the
        module.  If not a string, then it is treated as the object in the
        module.
    """

    submodules = import_submodules(package_name, recursive)
    results = []
    for name in submodules:
        module = submodules[name]

        value = getattr(module, symbol, None)
        if value is None:
            continue

        if not isinstance(value, (tuple, list)):
            value = [value]

        for item in value:
            if isinstance(item, types.StringTypes):
                item = getattr(module, item, None)

            if item is not None:
                results.append(item)

    return results            

