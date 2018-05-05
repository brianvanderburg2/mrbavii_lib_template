""" Application helper functions and classes. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import argparse


from .. import platform
from ..util.imp import export
from ..util.functools import lazyprop
from ..pattern.event import Events

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
class ConfigRef(object):
    """ Reference a configuration item. """

    def __init__(self, name, defval=None):
        self.name = name
        self.defval = defval


@export
class ServiceRef(object):
    """ Reference a service item. """

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs


@export
class AppHelper(object):
    """ The application helper oject. """

    # Provide access to the global instance as well as named instances
    __instances = {}

    @classmethod
    def get(cls, name=None):
        """ Return the instance of the app helper. """
        return cls.__instances.get(name, None)

    @classmethod
    def set(cls, instance, name=None):
        """ Set the instance of the app helper. """
        cur = cls.__instances.get(name, None)
        cls.__instances[name] = instance
        return cur

    # Initialization

    def __init__(self):
        """ Initialize.  Note the construction shouldn't perform any active
            opterations, it's really just a place to specify configurations.
        """
        self.set(self) # Set as the global instance

        self._configs = {}
        self._registry = {}
        self._services = {}

        self.setup()

    def setup(self):
        """ Setup configs and registry here. """
        pass

    # Service/config registry

    def config(self, data):
        """ Update our configurations. """
        self._configs.update(data)

    def register(self, name, factory, args=(), kwargs={}, single=True):
        """ Registry a given service. """
        self._registry[name] = (factory, args, kwargs, single)

    def resolve(self, name, *args, **kwargs):
        """ Resolve a given service. """
        if not name in self._registry:
            return

        (factory, _args, _kwargs, single) = self._registry[name]

        if single and name in self._services:
            return self._services[name]

        if isinstance(factory, str):
            factory = self._getconfig(factory)

        # Merge our args
        newargs = list(_args)
        newargs[0:len(args)] = args

        newkwargs = dict(_kwargs)
        newkwargs.update(kwargs)

        newargs = self._getconfig(newargs)
        newkwargs = self._getconfig(newkwargs)

        # Create the result
        result = factory(*newargs, **newkwargs)
        if single:
            self._services[name] = result

        return result

    def _getconfig(self, what):
        """ Recursively resolve a configuration. """

        if isinstance(what, tuple):
            return tuple(self._getconfig(i) for i in what)
        elif isinstance(what, list):
            return list(self._getconfig(i) for i in what)
        elif isinstance(what, dict):
            return {i: self._getconfig(i) for i in what}
        elif isinstance(what, ConfigRef):
            if what.name in self._configs:
                value = self._configs[what.name]
            else:
                value = what.default
            return self._getconfig(value)
        elif isinstance(what, ServiceRef):
            return self.resolve(what.name, *what.args, **what.kwargs)
        else:
            return what


    # Event listeners
    def listen(self, event, callback):
        return self.event.listen(event, callback)

    def notify(self, event, *args, **kwargs):
        self.event.fire(event, *args, **kwargs)

    def ignore(self, cbid):
        self.event.remove(cbid)


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

    @lazyprop
    def args(self):
        """ Return the command line. arguments. """
        return self.parse_args()

    @lazyprop
    def path(self):
        """ Return the application paths."""
        return AppPath(self.appname, self.appversion)

    @lazyprop
    def event(self):
        """ Return events object. """
        return Events()


    def create_arg_parser(self):
        """ Create and return the command line argument parser. """
        parser = ArgumentParser(description=self.description)

        return parser

    def parse_args(self):
        """ Parse the command line arguments. """
        parser = self.create_arg_parser()

        return parser.parse_args()

    # Execution related methods. """

    def execute(self):
        """ External method to execute the application. """
        self.startup()
        self.main()
        self.shutdown()

    def startup(self):
        """ Perform startup here. """
        pass

    def shutdown(self):
        """ Perform shutdown here. """
        pass


    def main(self):
        """ Run application main code here. """
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
