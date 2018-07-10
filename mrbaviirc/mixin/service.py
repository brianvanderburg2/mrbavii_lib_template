""" A mixin to provide service factory related methods. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import threading


from ..util.imp import Exporter
from ..constants import SENTINEL


export = Exporter(globals())


@export
class ServiceContainerMixin(object):
    """ A mixing object providing configuration-related methods. """

    def __init__(self):
        """ Initialize the service container mixin. """
        self._service_registry = {}
        self._service_instances = {}
        self._service_lock = threading.RLock()
    
    def register_factory(self, name, factory):
        """ Registry a given service factory. This should occur in the main thread. """
        self._service_registry[name] = (factory, False)

    def register_singleton(self, name, factory):
        """ Registry a given service factory which should be resolved only once
        This should occur in the main thread. """
        self._service_registry[name] = (factory, True)

    def unregister_service(self, name):
        """ Remove a registered service. This should occur in the main thread. """
        self._service_registry.pop(name, None)
        self.clear_service(name)

    def resolve_service(self, name, *args, **kwargs):
        """ Get the service instance. """
        if not name in self._service_registry:
            raise KeyError("No such service {0}".format(str(name)))

        with self._service_lock:
            (factory, singleton) = self._service_registry[name]

            if not singleton:
                # We always create a new object and never store it
                return factory(*args, **kwargs)

            # If it is a singleton, we should not pass any arguments
            assert(len(args) == 0 and len(kwargs) == 0)

            if name in self._service_instances:
                return self._service_instances[name]

            # Object not set yet:
            obj = self._service_instances[name] = factory()
            return obj

    def clear_service(self, name):
        """ Remove the current service instance if any. """
        with self._service_lock:
            self._service_instances.pop(name, None)
    
    def clear_services(self):
        """ Remove all service instances. """
        with self._service_lock:
            self._service_instances.clear()

    def set_service(self, name, instance):
        """ Manually set the instance. """
        with self._service_lock:
            self._service_instances[name] = instance

