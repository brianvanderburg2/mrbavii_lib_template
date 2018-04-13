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
def export(_obj=None, **kwargs):
    """ Export the given object by appending it's name to the modules __all__"""

    mdict = (
        sys.modules[_obj.__module__].__dict__
        if _obj
        else sys._getframe(1).f_globals
    )
    mall = mdict.setdefault("__all__", [])

    if not _obj is None:
        if not _obj.__name__ in mall:
            mall.append(_obj.__name__)

    for name in kwargs:
        if not name in mall:
            mall.append(name)
        mdict[name] = kwargs[name]

    return _obj

@export
def export_import_all(module):
    """ Perform a 'from <module> import *' and export all imported symbols. """
    mdict = sys._getframe(1).f_globals
    mall = mdict.setdefault("__all__", [])
    mpackage = mdict.get("__package__")

    impdict = importlib.import_module(module, mpackage).__dict__
    impnames = [
        name
        for name in impdict.get("__all__", impdict)
        if not name.startswith("_")
    ]

    for impname in impnames:
        if not impname in mall:
            mall.append(impname)
        mdict[impname] = impdict[impname]




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

