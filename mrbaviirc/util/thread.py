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


class threadattr(object):
    """ Class for thread-local class members. """

    def __init__(self, defval=SENTINEL):
        """ Initialize the thread attribute. """
        self._vars = threading.local()
        self._defval = defval

    @property
    def _data(self):
        try:
            return self._vars.data
        except AttributeError:
            data = self._vars.data = weakref.WeakKeyDictionary()
            return data

    def __get__(self, instance, owner):
        assert(instance is not None)

        try:
            return self._data[instance]
        except KeyError:
            if self._defval is not SENTINEL:
                return self._defval
            else:
                raise AttributeError("Thread-local storage value not yet set.")

    def __set__(self, instance, value):
        assert(instance is not None)
        self._data[instance] = value

    def __delete__(self, instance):
        self._data.pop(instance, None)

