""" Linux-style paths. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import os


from .commonpath import CommonPaths
from ..util.imp import Exporter


export = Exporter(globals())


@export
class LinuxPaths(CommonPaths):

    @staticmethod
    def get_user_data_dir(appname, version=None):
        """ Return the directory to read/write user data files. """
        datadir = os.path.join(
            os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
            appname
        )

        return os.path.join(datadir, version) if version else datadir

    @staticmethod
    def get_sys_data_dir(appname, version=None, all=True):
        """ Return the system data directories. """
        datadirs = os.environ.get(
            "XDG_DATA_DIRS", 
            os.pathsep.join(["/usr/local/share", "/usr/share"]),
        ).split(os.pathsep)

        suffix = os.path.join(appname, version) if version else appname
        datadirs = tuple(os.path.join(part, suffix) for part in datadirs)

        return datadirs if all else datadirs[0]

    @staticmethod
    def get_user_config_dir(appname, version=None):
        """ Return the directory to read/write user configuration files. """
        confdir = os.path.join(
            os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
            appname
        )

        return os.path.join(confdir, version) if version else confdir

    @staticmethod
    def get_sys_config_dir(appname, version=None, all=True):
        """ Return the system configuration directories. """
        confdirs = os.environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(os.pathsep)

        suffix = os.path.join(appname, version) if version else appname
        confdirs = tuple(os.path.join(part.rstrip(os.sep), suffix) for part in confdirs)

        return confdirs if all else confdirs[0]

    @staticmethod
    def get_cache_dir(appname, version=None):
        """ Return a cache directory. """

        cachedir = os.path.join(
            os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
            appname
        )

        return os.path.join(cachedir, version) if version else cachedir

    @staticmethod
    def get_runtime_dir(appname, version=None):
        """ Return directory for runtime files. """
        runtimedir = os.environ.get("XDG_RUNTIME_DIR")

        if os.path.isdir(runtimedir):
            suffix = os.path.join(appname, version) if version else appname
            return os.path.join(runtimedir, suffix)
        else:
            import tempfile
            # TODO: log warning
            return tempfile.mkdtemp(appname)
        
