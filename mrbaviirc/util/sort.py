""" Sorting related functions. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


__all__ = ["depends_sort"]


def depends_sort(data):
    """
    Sort a set of dependencies.

    data - A dictionary of name : [depends names] mappings.

    Returns a list of names such that for any given name, the depends for that
    name will occur before that name.

        {
            "libpng": ["libz"],
            "libz": [],
            "app": ["libpng", "libz"]
        }

    Returns:

        ["libz", "libpng", "app"]

    """

    return _depends_sort_helper(tuple(data.keys()), data, [], [])

def _depends_sort_helper(names, data, _stack, _results):
    """ Sort all names by dependency. """

    for name in names:
        if name in _results:
            continue

        # Add dependencies first, prevent recusrive dependencies
        depends = data.get(name)
        if depends:
            if name in _stack:
                 raise Exception("Depenency loop: " + str(_stack + [name]))
            _stack.append(name)
            _depends_sort_helper(depends, data, _stack, _results)
            _stack.pop()

        # Finally add this name
        _results.append(name)

    return _results 

