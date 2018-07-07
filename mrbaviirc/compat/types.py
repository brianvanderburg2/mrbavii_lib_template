""" Compatibility issues. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


__all__.append("StringTypes")
try:
    from types import StringTypes
except AttributeError:
    StringTypes = (str,)

try:
    from types import StringType
except AttributeError:
    StringType = str

