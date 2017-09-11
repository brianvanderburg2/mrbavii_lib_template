""" Provide a listener mixin """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2016-2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import weakref

from ..util.functools import StrongCallback, WeakCallback


class _WeakCallback(WeakCallback):
    """ Store a weak reference to a callback. """

    def __init__(self, callback, listener):
        self._listener = weakref.ref(listener)
        WeakCallback.__init__(self, callback)

    def cleanup(self, ref):
        listener = self._listener()
        if listener:
            listener.remove_listener(id(self))


__all__.append("ListenerMixin")
class ListenerMixin(object):
    """ This class provides methods to a a derived class to allow
        the registration of listeners/event hooks for named events. """

    def __init__(self):
        """ Create the listener data. """

        self.__listeners = {}

    def add_listener(self, event, callback, weak=True):
        """ Add a listener callback for a given event. """
        queue = self.__listeners.setdefault(event, [])
        
        if weak:
            cbobj = _WeakCallback(callback, self)
        else:
            cbobj = StrongCallback(callback)

        queue.append(cbobj)
        return id(cbobj)

    def remove_listener(self, cbid):
        """ Return a listerner previously added. """
        for queue in self.__listeners.values():
            for (index, cbobj) in enumerate(queue):
                if id(cbobj) == cbid:
                    del queue[index]
                    return # IDs are unique so once we find the item, we return

    def notify_listeners(self, event, *args, **kwargs):
        """ Notify all listeners. """
        if event not in self.__listeners:
            return

        queue = self.__listeners[event]

        for callback in queue:
            callback.execute(*args, **kwargs)

