""" Provide some function and method utilities """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2016-2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import weakref
from functools import wraps
import threading


from .imp import Exporter


export = Exporter(globals())


@export
class lazyprop(object):
    """ Create a proper that is evaulated once and remembered. """

    def __init__(self, method):
        """ Create our lazy attribute. """
        # Use a lock for thread-safety
        self._lock = threading.Lock()
        self._method = method
        self.__name__ = method.__name__
        self.__doc__ = method.__doc__

    def __get__(self, obj, owner):
        """ Get our lazy attribute in a thread-safe way. """
        if obj is None:
            return None

        # Convert name to a private form if needed
        name = self._method.__name__
        if name.startswith("__") and not name.endswith("__"):
            name = "_{0}{1}".format(method.__class__.__name__, name)

        # Make sure only one thread attempts to set initial value
        # After the initial set, the value is accessed directly and
        # may not be thread-safe if the value is changed.
        with self._lock:
            # Race condition: two different threads may enter __get__ at the
            # same time.  The other may end up locking and computing the value
            # so only set if it has not already been set
            if not name in obj.__dict__:
                obj.__dict__[name] = self._method(obj)

        # Value should be set at this point.
        return obj.__dict__[name]

@export
class lazypropro(object):
    """ Create a read-only property that is evaulated once and remembered. """

    def __init__(self, method):
        """ Create our lazy attribute. """
        # Use a lock for thread-safety
        self._lock = threading.Lock()
        self._method = method
        self.__name__ = method.__name__
        self.__doc__ = method.__doc__

    def __get__(self, obj, owner):
        """ Get our lazy attribute in a thread-safe way. """
        if obj is None:
            return None

        # Convert name to a private form if needed
        name = self._method.__name__
        if name.startswith("__") and not name.endswith("__"):
            name = "_{0}{1}".format(method.__class__.__name__, name)

        # Don't shadow the class name with an instance name
        name = "_lazyprop_{0}".format(name)

        # Make sure only one thread attempts to set initial value
        with self._lock:
            # Race condition: two different threads may enter __get__ at the
            # same time.  The other may end up locking and computing the value
            # so only set if it has not already been set
            if not name in obj.__dict__:
                obj.__dict__[name] = self._method(obj)

        # Value should be set at this point.
        return obj.__dict__[name]

    def __set__(self, obj, value):
        raise AttributeError("Unable to set read-only lazy property.")

@export
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


@export
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

