""" Base app helper functions and classes. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import threading


from ..constants import SENTINEL
from ..util.imp import Exporter
from ..util.functools import lazyprop, lazypropro
from ..pattern.event import Events
from .path import AppPath
from ..mixin.config import ConfigMixin
from ..mixin.service import ServiceContainerMixin

export = Exporter(globals())


@export
class BaseAppHelper(ConfigMixin, ServiceContainerMixin):
    """ The base application helper oject. """

    # Provide access to the global instance as well as named instances
    __instances = {}
    __lock = threading.RLock()

    @classmethod
    def get(cls, name=None):
        """ Return the instance of the app helper. """
        with cls.__lock:
            return cls.__instances.get(name, None)

    @classmethod
    def set(cls, instance, name=None):
        """ Set the instance of the app helper. """
        with cls.__lock:
            cur = cls.__instances.get(name, None)
            cls.__instances[name] = instance
            return cur

    # Initialization
    def __init__(self):
        """
            Initialize.  Note the construction shouldn't perform any active
            operations, it's really just a place to specify configurations.
        """

        ConfigMixin.__init__(self)
        ServiceContainerMixin.__init__(self)

        self.set(self) # Set as the global instance

        self._lock = threading.RLock()
        self._local = threading.local()
        self._main_thread = threading.current_thread()
        self._storage = {}

        self.setup()

    def setup(self):
        """ Setup configs and registry here. """
        self.set_config("appname", lambda: self.appname)
        self.set_config("appversion", lambda: self.appversion)

        self.register_singleton("path", lambda: AppPath(self.appname, self.appversion))

    # Event listeners
    # Threads?
    # TODO: move to mixin
    def listen(self, event, callback):
        return self.event.listen(event, callback)

    def notify(self, event, *args, **kwargs):
        self.event.fire(event, *args, **kwargs)

    def ignore(self, cbid):
        self.event.remove(cbid)

    # Value storage
    # How to handle threads?
    def remember(self, name, value, timeout=0):
        self._storage[name] = value

    def recall(self, name, defval=SENTINEL):
        if defval is SENTINEL:
            return self._storage.get(name)
        else:
            return self._storage.get(name, defval)

    def forget(self, name):
        self._storage.pop(name, None)

    # Some common properties that should be defined if needed

    @property
    def lock(self):
        """ Return the application thread lock. """
        return self._lock

    @property
    def main_thread(self):
        """ Return the main thread. """
        return self._main_thread

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
    def path(self):
        """ Return the application paths."""
        return self.resolve_service("path")

    @lazypropro
    def event(self):
        """ Return events object. """
        return Events()


    # Execution related methods. """

    def startup(self):
        """ Perform startup here. """
        pass

    def shutdown(self):
        """ Perform shutdown here. """
        pass


