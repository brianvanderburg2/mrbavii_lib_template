""" wxConfig related code. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import wx

__all__.append("ConfigPathChanger")
class ConfigPathChanger(object):
    """ Allow use of ConfigPathChanger in a with statement """
    
    def __init__(self, config, entry):
        self._changer = wx.ConfigPathChanger(config, entry)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        del self._changer
        self._changer = None

