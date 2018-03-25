""" Common path functions. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


__all__ = ["get_package_data_dir"]


import os

def get_package_data_dir(package, all=True):
    """ Get the package data directory.  For now this assumes a "data"
        subdirectory beside the package. """

    p = os.path

    paths = getattr(package, "__path__")
    dirs = tuple(p.abspath(p.join(part, "data")) for part in paths)

    return dirs if all else dirs[0]
