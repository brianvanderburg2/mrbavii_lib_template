""" Utility functions and classes. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []

__all__.append("updatedoc")
def updatedoc(prepend, append):
    """ A decorator to prepend or append to an object's doc string. """
    def wrapper(obj):
        obj.__doc__ = "{0}{1}{2}".format(
            prepend if prepend else "",
            obj.__doc__ if obj.__doc__ else "",
            append if append else ""
        )
        return obj

    return wrapper


