""" Modification of wx.lib.newevent to allow creation of multiple event types for a single event class. """

from __future__ import absolute_import

__author__      =   "Miki Tebeka <miki.tebeka@gmail.com>, Modified by Brian Allen Vanderburg II"

import itertools

import wx


__all__ = ["NewEvents", "NewCommandEvents"]

def NewEvents(count=1):
    """ Generate new event tuple (Event, Type1, Binder1, ..., TypeN, BinderN)

    As a result, any event created must also have the event type specified.
    """

    evttypes = (wx.NewEventType() for i in range(count))

    class _Event(wx.PyEvent):
        def __init__(self, evttype, **kw):
            wx.PyEvent.__init__(self)
            self.SetEventType(evttype)
            self.__dict__.update(kw)

    typebindings = ((i, wx.PyEventBinder(i)) for i in evttypes)
    return tuple(itertools.chain([Event], typebindings))


def NewCommandEvents(count=1):
    """ Generate new command event tuple (CmdEvent, Type1, Binder1, ... TypeN, BinderN)

    As a result, any event created must also have the event type specified.

    (MyButtonEvent,
    evtMY_BUTTON_CLICKED, EVT_MY_BUTTON_CLICKED,
    evtMY_BUTTON_DCLICKED, EVT_MY_BUTTON_DCLICKED) = NewCommandEvent(2)

    ...

    event = MyButtonEvent(evtMY_BUTTON_CLICKED, id)
    wx.PostEvent(handler, event)

    ...

    handler.Bind(EVT_MY_BUTTON_CLICKED, handle_func)
    """

    evttypes = (wx.NewEventType() for i in range(count))

    class _Event(wx.PyCommandEvent):
        def __init__(self, evttype, id, **kw):
            wx.PyCommandEvent.__init__(self, evttype, id)
            self.__dict__.update(kw)

    typebindings = ((i, wx.PyEventBinder(i, 1)) for i in evttypes)
    return tuple(itertools.chain([_Event], typebindings))



