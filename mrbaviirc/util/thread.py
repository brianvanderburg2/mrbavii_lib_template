""" Threading utilities. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import threading
import weakref

from ..constants import SENTINEL
from .imp import Exporter


export = Exporter(globals())


@export
class threadattr(object):
    """ Class for thread-local class members. """

    def __init__(self, defval=SENTINEL):
        """ Initialize the thread attribute. """
        self._vars = threading.local()
        self._defval = defval

    def __get__(self, instance, owner):
        assert(instance is not None)
        try:
            return self._vars.data[instance]
        except (KeyError, AttributeError):
            if self._defval is not SENTINEL:
                return self._defval
            else:
                raise AttributeError("Thread-local attribute value not yet set.")

    def __set__(self, instance, value):
        assert(instance is not None)
        try:
            v = self._vars.data
        except AttributeError:
            v = self._vars.data = weakref.WeakKeyDictionary()

        v[instance] = value

    def __delete__(self, instance):
        try:
            self._vars.data.pop(instance, None)
        except AttributeError:
            pass

