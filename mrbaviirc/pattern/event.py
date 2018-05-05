""" Provide an event hooks system """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import weakref

from ..util.functools import StrongCallback, WeakCallback


class _WeakCallback(WeakCallback):
    """ Store a weak reference to a callback. """

    def __init__(self, callback, events):
        self._events = weakref.ref(events)
        WeakCallback.__init__(self, callback)

    def cleanup(self, ref):
        events = self._events()
        if events:
            events.remove(id(self))


__all__.append("Events")
class Events(object):
    """ This class provides methods to register and fire events. """

    def __init__(self):
        """ Create the events data. """
        self.__events = {}
        self.__queue = []

    def listen(self, event, callback, weak=True):
        """ Add a event callback for a given event. """
        queue = self.__events.setdefault(event, [])
        
        if weak:
            cbobj = _WeakCallback(callback, self)
        else:
            cbobj = StrongCallback(callback)

        queue.append(cbobj)
        return id(cbobj)

    def remove(self, cbid):
        """ Return a event callback previously added. """
        for queue in self.__events.values():
            for (index, cbobj) in enumerate(queue):
                if id(cbobj) == cbid:
                    del queue[index]
                    return # IDs are unique so once we find the item, we return

    def fire(self, event, *args, **kwargs):
        """ Notify all event callbacks. """
        if event not in self.__events:
            return

        queue = self.__events[event]

        for callback in queue:
            callback.execute(*args, **kwargs)

    def queue(self, event, *args, **kwargs):
        """ Queue an event for later dispatch. """
        self.__queue.append((event, args, kwargs))

    def flush(self, event=None):
        """ Flush events. """
        for (_event, args, kwargs) in self.__queue:
            if event is None or event == _event:
                self.fire(_event, *args, **kwargs)

        if event:
            self.__queue = [i for i in self.__queue if i[0] != event]
        else:
            self.__queue = []

