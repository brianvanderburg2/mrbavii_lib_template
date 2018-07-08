""" A mixin to provide configuration-related methods. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


from ..util.imp import Exporter
from ..constants import SENTINEL


export = Exporter(globals())


@export
class ConfigMixin(object):
    """ A mixing object providing configuration-related methods. """

    def __init__(self):
        """ Initialize the service container mixin. """
        self._configs = {}

    def set_config(self, name, value):
        """ Update our configurations. """
        self._configs[name] = value

    def get_config(self, config, defval=SENTINEL):
        """ Get the value of a config. """
        if config in self._configs:
            return self.eval_config(self._configs[config], args, kwargs)
        elif defval is not _SENTNEL:
            return self.eval_config(defval, args, kwargs)
        else:
            raise KeyError("No such config: {0}".format(config))

    def eval_config(self, what):
        """ Recursively resolve a configuration. """

        if isinstance(what, tuple):
            return tuple(self.eval_config(i) for i in what)
        elif isinstance(what, list):
            return list(self.eval_config(i) for i in what)
        elif isinstance(what, dict):
            return {i: self.eval_config(what[i]) for i in what}
        elif callable(what):
            return self.eval_config(what())
        else:
            # TODO: handle config strings in the form "%CONFVAR% and %%"
            return what

