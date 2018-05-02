""" Application helper functions and classes. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import argparse


from ..util.imp import export
from .. import platform


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


@export
class AppTraits(object):
    """ The traits of an application. """

    def __init__(self, app):
        self._app = app
        self._path = None

    @property
    def path(self):
        if self._path is None:
            self._path = AppPath(
                self._app.appname,
                self._app.appversion
            )

        return self._path
        

@export
class AppHelper(object):
    """ The application helper oject. """

    # Some common properties that should be defined if needed

    @property
    def appname(self):
        """ Return the application name as used in paths. """
        raise NotImplementedError

    @property
    def appversion(self):
        """ Return the applicatoin vesion as used in paths. """
        return None

    @property
    def displayname(self):
        """ Return the application display name. """
        return self.appname

    @property
    def description(self):
        """ Return the application description. """
        return self.displayname

    @property
    def traits(self):
        """ Get the app traits. """
        if self._traits is None:
            self._traits = AppTraits(self)

        return self._traits

    @property
    def args(self):
        """ Return the command line. arguments. """
        if self._args is None:
            self._args = self.parse_args()

        return self._args

    @property
    def path(self):
        """ Return the application paths."""
        if not self._path:
            self._path = self.traits.path

        return self._path

    def __init__(self):
        """ Initialize base apps object. """
        self._args = None
        self._traits = None
        self._path = None

    def create_arg_parser(self):
        """ Create and return the command line argument parser. """
        parser = ArgumentParser(description=self.description)

        return parser

    def parse_args(self):
        """ Parse the command line arguments. """
        parser = self.create_arg_parser()

        return parser.parse_args()


    def execute(self):
        self.startup()
        self.main()
        self.shutdown()

    def startup(self):
        pass

    def shutdown(self):
        pass


    def main(self):
        raise NotImplementedError


@export
class ArgumentParser(argparse.ArgumentParser):
    """ A helper class for parsing arguments. """

    def __init__(self, *args, **kwargs):
        """ Initialize argument parser. """

        self.__remainder = None
        self.__remainder_added = False

        argparse.ArgumentParser.__init__(self, *args, **kwargs)

    def add_remainder(self, remainder):
        """ Add an argument to accept the remainder of the parameters. """
        self.__remainder = remainder

    def parse_args(self, *args, **kwargs):
        """ Parse the arguments. """

        if not self.__remainder_added:
            if self.__remainder:
                self.add_argument(self.__remainder, nargs=argparse.REMAINDER)
            self.__remainder_added = True

        args = argparse.ArgumentParser.parse_args(self, *args, **kwargs)

        if self.__remainder:
            # If the remainder started with "--", pop it off
            remainder = getattr(args, self.__remainder, [])
            if len(remainder) and remainder[0] == "--":
                setattr(args, self.__remainder, remainder[1:])

        return args
