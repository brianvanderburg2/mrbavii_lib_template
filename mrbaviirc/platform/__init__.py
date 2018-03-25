""" Some platform helper functions. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


__all__ = []


import sys
import os


# Path
###############################################################################

__all__.extend(["path", "Path"])


def _detect_platform_path(portable=False):
    if portable:
        from . import portpath
        return portpath
    
    platform = sys.platform

    if platform == "win32":
        from . import winpath as path
    elif platform == "darwin":
        from . import macpath as path
    else:
        from . import linuxpath as path

    return path


path = _detect_platform_path()


# Some common functions a




class Path(object):
    
    def __init__(self, appname, version=None, portable=False):
        self._appname = appname
        self._version = version

        self._tempdir = None

        self._path = _detect_platform_path(portable)

    def get_user_data_dir(self, version=True):
        return self._path.get_user_data_dir(
            self._appname,
            self._version if version else None
        )

    def get_sys_data_dir(self, version=True, all=True):
        return self._path.get_sys_data_dir(
            self._appname,
            self._version if version else None,
            all
        )

    def get_package_data_dir(self, package, all=True):
        """ Get the package data directory. """
        return self._path.get_package_data_dir(
            package,
            all
        )

    def get_user_config_dir(self, version=True):
        return self._path.get_user_config_dir(
            self._appname,
            self._version if version else None
        )

    def get_sys_config_dir(self, version=True, all=True):
        return self._path.get_sys_config_dir(
            self._appname,
            self._version if version else None,
            all
        )

    def get_cache_dir(self, version=True):
        return self._path.get_cache_dir(
            self._appname,
            self._version if version else None
        )

    def get_runtime_dir(self, version=True):
        return self._path.get_runtime_dir(
            self._appname,
            self._version if version else None
        )

    def get_temp_dir(self, version=False, newdir=False):
        if self._tempdir is None or newdir or not os.path.isdir(self._tempdir):
            import tempfile
            self._tempdir =  tempfile.mkdtemp(self.version if version else "")

        return self._tempdir

