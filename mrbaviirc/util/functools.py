""" Provide some function and method utilities """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2016-2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import weakref


__all__.append("WeakCallback")
class WeakCallback(object):
    """ Store a weak callback. """

    def __init__(self, callback):
        """ Construct the weak callback. """

        if hasattr(callback, "im_self"):
            self._obj = weakref.ref(callback.im_self, self.cleanup)
            self._func = weakref.ref(callback.im_func, self.cleanup)
        else:
            self._obj = None
            self._func = weakref.ref(callback, self.cleanup)

    def __call__(self, *args, **kwargs):
        """ Execute the callback and return the result.

        If the callback is no longer valid, None will be returned. If
        you need to tell if the callback was executed, use the execute
        method instead."""

        (called, retval) = self.execute(*args, **kwargs)
        return retval

    def execute(self, *args, **kwargs):
        """ Execute the callback and return a tuple of (called, retval).

        called with be false if the callback was not executed due to the
        weak reference being invalidated.
        """
        obj = None
        if self._obj is not None:
            obj = self._obj()
            if obj is None:
                return (False, None)

        func = self._func()
        if func is None:
            return (False, None)

        if obj:
            return (True, func(obj, *args, **kwargs))
        else:
            return (True, func(*args, **kwargs))

    def cleanup(self, ref):
        """ This method is called when weakref is no longer valid. """
        pass


__all__.append("StrongCallback")
class StrongCallback(object):
    """ This class provides the same signature as WeakCallback but does
    not store a weak reference to the object/function. """

    def __init__(self, callback):
        """ Construct the strong callback. """
        self._func = callback

    def __call__(self, *args, **kwargs):
        """ Call the callback and return the result. """
        return self._func(*args, **kwargs)

    def execute(self, *args, **kwargs):
        """ Call the callback and return (True, retval). """
        return (True, self._func(*args, **kwargs))

