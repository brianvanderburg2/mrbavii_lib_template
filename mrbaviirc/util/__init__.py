""" Utility functions and classes. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


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


def updateall(item_or_name):
    """
        Update the __all__ list of the calling module with the function or class name. 
        
            @updateall
                def fn(...):
                ...

            @updateall
                class cls(...):
                ...

        This method also supports updating the __all_ list with variables:

        updateall("var")
        var = var1
    """
    from types import StringTypes
    import inspect

    caller = inspect.stack()[1]
    module = inspect.getmodule(caller[0])
    real_all = module.__all__

    if isinstance(item, StringTypes):
        # Being calld directly, not as a decorator
        real_all.append(item)
    else:
        # Being called as a decorator
        real_all.append(item.__name__)
        return item

