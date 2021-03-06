""" Event related functions and classes. """

# Portions of the below are inspired by wx.lib.newevent

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2016 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = [
    "NewEventTypes", "NewEvents", "NewCommandEvents", "NotifyEvent"
]

import itertools

import wx


def NewEventTypes(count=1, expectedIDs=0):
    """ Generate new event types and bindings for the events (Type1, Binder1, ..., TypeN, BinderN)

    This allows creating new event types that can be used with existing event classes.

        (evtBUTTONBOOK_PAGE_CHANGING, BUTTONBOOK_PAGE_CHANGING) = NewEventTypes(1)

        ...

        event = wx.BookCtrlEvent(evtBUTTONBOOK_PAGE_CHANGING, ...)
        wx.PostEvent(handler, event)

        ...

        handler.Bind(BUTTONBOOK_PAGE_CHANGING, handler_func)
    
    """

    # Note: These are generators, once used they will be exhuasted
    evttypes = (wx.NewEventType() for i in range(count))
    types_and_binders = ((i, wx.PyEventBinder(i, expectedIDs)) for i in evttypes)

    return tuple(itertools.chain(*types_and_binders))


def NewEvents(count=1):
    """ Generate new event tuple (Event, Type1, Binder1, ..., TypeN, BinderN)

    As a result, any event created must also have the event type specified.

    The returned event object takes only the event type and keyword arguments
    for attributes.  To set an event id, use SetId.
    """

    class _Event(wx.PyEvent):
        def __init__(self, evttype, **kw):
            wx.PyEvent.__init__(self)
            self.SetEventType(evttype)
            self.__dict__.update(kw)

    return (_Event,) + NewEventTypes(count)


def NewCommandEvents(count=1):
    """ Generate new command event tuple (CmdEvent, Type1, Binder1, ... TypeN, BinderN)

    As a result, any event created must also have the event type specified.
    
    The returned event object takes only the event type and id, and keyword
    arguments for attributes.

        (MyButtonEvent,
        evtMY_BUTTON_CLICKED, EVT_MY_BUTTON_CLICKED,
        evtMY_BUTTON_DCLICKED, EVT_MY_BUTTON_DCLICKED) = NewCommandEvent(2)

        ...

        event = MyButtonEvent(evtMY_BUTTON_CLICKED, id)
        wx.PostEvent(handler, event)

        ...

        handler.Bind(EVT_MY_BUTTON_CLICKED, handle_func)
    """

    class _Event(wx.PyCommandEvent):
        def __init__(self, evttype, id, **kw):
            wx.PyCommandEvent.__init__(self, evttype, id)
            self.__dict__.update(kw)

    return (_Event,) + NewEventTypes(count, 1)


class NotifyEvent(wx.PyCommandEvent):
    """ This class provides a simple notification-like event. """

    def __init__(self, evttype, id, **kw):
        wx.PyCommandEvent.__init__(self, evttype, id)
        self.__dict__.update(kw)

        self._allowed = True

    def Allow(self):
        self._allowed = True

    def Veto(self):
        self._allowed = False

    def IsAllowed(self):
        return self._allowed

