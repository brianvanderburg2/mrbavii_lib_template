""" Some platform helper functions. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import sys
import os


from ..util.imp import Exporter
export = Exporter(globals())


# Path
###############################################################################


def _detect_platform_path():
    platform = sys.platform

    if platform == "win32":
        from .winpath import WinPaths as path
    elif platform == "darwin":
        from .macpath import MacPaths as path
    else:
        from .linuxpath import LinuxPaths as path

    return path()


export(path = _detect_platform_path())


