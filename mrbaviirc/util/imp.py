""" Import utility functions. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import sys
import pkgutil
import importlib


class ExportError(Exception):
    """ An exception caused when using export. """
    pass


class Exporter(object):
    """ A helper class for exporting names from a module. """

    def __init__(self, _globals):
        """ Initialize the exporter. """
        self._all = _globals.setdefault("__all__", [])
        self._globals = _globals
        self._package = _globals["__package__"]


    def __call__(self, _obj=None, **kwargs):
        """ Add to the all list. """
        if _obj is not None:
            name = _obj.__name__
            if name in self._all:
                raise ExportError("name already exists in __all__: {}".format(name))

            self._all.append(name)

        for name in kwargs:
            if name in self._all:
                raise ExportError("name already exists in __all__: {}".format(name))
            self._all.append(name)
            self._globals[name] = kwargs[name]

        return _obj

    def extend(self, *modules):
        """ Extend the all list from other modules. """
        for module in modules:
            if isinstance(module, str):
                module = importlib.import_module(module, self._package)

            mname = module.__name__
            mdict = module.__dict__

            if "__all__" in mdict:
                impnames = tuple(mdict["__all__"])
            else:
                impnames = [
                    name for name in mdict if not name.startswith("_")
                ]

            for impname in impnames:
                if impname in self._all:
                    raise ExportError("name imported from {} already exists in __all__: {}".format(mname, impname))
                self._all.append(impname)
                self._globals[impname] = mdict[impname]


# Use our exporter from here out.  Call it _export to prevent accidental
# from imp import export
_export = Exporter(globals())
_export(Exporter)
_export(ExportError)



@_export
def import_submodules(package, recursive=False, absolute=False):
    """ Import submodules and return a tuple of (name,module) """

    # We must pass the package prefix to walk_packages else when it calls
    # iter_modules it will not have the full module path and doesn't seem
    # to load submodules of found packages correctly if at all.

    if isinstance(package, str):
        package = importlib.import_module(package)

    func = pkgutil.walk_packages if recursive else pkgutil.iter_modules
    prefix = package.__name__ + "."
    prefix_len = len(prefix)

    # Return a tuple of tuples (name, module)
    return tuple(
        (name if absolute else name[prefix_len:], importlib.import_module(name))
        for (loader, name, ispkg) in func(package.__path__, prefix)
    )

    return loaded


@_export
def import_submodules_symbols(package_name, symbol, recursive=False):
    """ Return a list of the specified symbols from all loaded modules. """
    submodules = import_submodules(package_name, recursive)
    
    results = []
    for (name, module) in submodules:
        value = getattr(module, symbol, None)
        if(value):
            results.append(value)

    return results

@_export
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
    for (name, module) in submodules:
        value = getattr(module, symbol, None)
        if value is None:
            continue

        if not isinstance(value, (tuple, list)):
            value = [value]

        for item in value:
            if isinstance(item, str):
                item = getattr(module, item, None)

            if item is not None:
                results.append(item)

    return results            

