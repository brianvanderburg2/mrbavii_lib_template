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


# Use for comparing some values
_SENTINEL = object()


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

    def __init__(self, name, defval=_SENTINEL):
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
class FuncRef(object):
    """ Evaluate a function to determine a value. """

    def __init__(self, func):
        self.func = func

@export
class StorageRef(object):
    """ Return a value from storage. """

    def __init__(self, name, defval=_SENTINEL):
        self.name = name
        self.defval = defval

@export
class PosRef(object):
    """ Represent a positional argument to resolve. """

    def __init__(self, pos):
        self.pos = pos

@export
class KeyRef(object):
    """ Represent a keyword argument to resolve. """

    def __init__(self, key):
        self.key = key


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
        self._storage = {}

        self.setup()

    def setup(self):
        """ Setup configs and registry here. """

        self.config("appname", FuncRef(lambda: self.appname))
        self.config("appversion", FuncRef(lambda: self.appversion))

        self.register(
            "path",
            AppPath,
            (
                ConfigRef("appname"),
                ConfigRef("appversion")
            )
        )

    # Service/config registry

    def config(self, name, value):
        """ Update our configurations. """
        self._configs[name] = value

    def register(self, name, factory, args=(), kwargs={}, single=True):
        """ Registry a given service. """
        self._registry[name] = (factory, args, kwargs, single)

    def resolve(self, name, *args, **kwargs):
        """ Resolve a given service. """
        if not name in self._registry:
            raise KeyError("No such service: {0}".format(str(name)))

        (factory, regargs, regkwargs, single) = self._registry[name]

        if single and name in self._services:
            return self._services[name]

        if isinstance(factory, str):
            factory = self._getconfig(factory, args, kwargs)

        # Merge our args
        factory_args = self._getconfig(regargs, args, kwargs)
        factory_kwargs = self._getconfig(regkwargs, args, kwargs)

        # Create the result
        result = factory(*factory_args, **factory_kwargs)
        if single:
            self._services[name] = result

        return result

    def getconfig(self, config, defval=_SENTINEL, args=(), kwargs={}):
        """ Get the value of a config. """
        if config in self._configs:
            return self._getconfig(self._configs[config], args, kwargs)
        elif defval is not _SENTNEL:
            return self._getconfig(defval, args, kwargs)
        else:
            raise KeyError("No such config: {0}".format(config))

    def _getconfig(self, what, args, kwargs):
        """ Recursively resolve a configuration. """

        if isinstance(what, tuple):
            return tuple(self._getconfig(i, args, kwargs) for i in what)
        elif isinstance(what, list):
            return list(self._getconfig(i, args, kwargs) for i in what)
        elif isinstance(what, dict):
            return {i: self._getconfig(what[i], args, kwargs) for i in what}
        elif isinstance(what, ConfigRef):
            return self.getconfig(what.name, what.defval, args, kwargs)
        elif isinstance(what, ServiceRef):
            newargs = self._getconfig(what.args, args, kwargs)
            newkwargs = self._getconfig(what.kwargs, args, kwargs)
            return self.resolve(what.name, *newargs, **newkwargs)
        elif isinstance(what, FuncRef):
            return self._getconfig(what.func(), args, kwargs)
        elif isinstance(what, StorageRef):
            return self.recall(what.name, what.defval)
        elif isinstance(what, PosRef):
            return args[what.pos]
        elif isinstance(what, KeyRef):
            return kwargs[what.key]
        else:
            return what


    # Event listeners
    def listen(self, event, callback):
        return self.event.listen(event, callback)

    def notify(self, event, *args, **kwargs):
        self.event.fire(event, *args, **kwargs)

    def ignore(self, cbid):
        self.event.remove(cbid)

    # Value storage
    def remember(self, name, value):
        self._storage[name] = value

    def recall(self, name, defval=_SENTINEL):
        if defval is _SENTINEL:
            return self._storage.get(name)
        else:
            return self._storage.get(name, defval)

    def forget(self, name):
        self._storage.pop(name, None)

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

    @property
    def path(self):
        """ Return the application paths."""
        return self.resolve("path")

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
