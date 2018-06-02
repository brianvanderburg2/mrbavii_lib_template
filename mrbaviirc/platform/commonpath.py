""" Common path functions. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import os


from ..util.imp import Exporter
export = Exporter(globals())


@export
class CommonPaths(object):
    """ A base paths object. """

    @staticmethod
    def get_package_data_dir(package, all=True):
        """ Get the package data directory.  For now this assumes a "data"
            subdirectory beside the package. """

        p = os.path

        paths = getattr(package, "__path__")
        dirs = tuple(p.abspath(p.join(part, "data")) for part in paths)

        return dirs if all else dirs[0]

    @staticmethod
    def get_temp_dir():
        import tempfile
        return tempfile.mkdtemp()

