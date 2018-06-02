""" Path helpers for applications. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


from ..util.imp import Exporter
from .. import platform


export = Exporter(globals())


@export
class AppPath(object):
    """ An application path aobject. """
    def __init__(self, appname, version=None):
        self._appname = appname
        self._version = version

        self._tempdir = None

        self._path = platform.path

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

    def get_temp_dir(self, newdir=False):
        if self._tempdir is None or newdir or not os.path.isdir(self._tempdir):
            self._tempdir =  self._path.get_temp_dir()

        return self._tempdir


