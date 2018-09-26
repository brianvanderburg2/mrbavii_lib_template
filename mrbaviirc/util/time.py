""" Time utilities. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


try:
    from time import monotonic
    timenow = monotonic
    timedelta = lambda a, b: a - b
    timesecs = lambda a: a
except ImportError:
    from datetime import datetime
    timenow = datetime.now
    timedelta = lambda a, b: a - b
    timesecs = lambda a: a.total_seconds()

from .imp import Exporter


export = Exporter(globals())


@export
class StopWatch(object):
    """ A stop-able timer class. """

    def __init__(self, start=False, elapsed=0.0):
        """ Initialize the stopwatch. """
        self._elapsed = elapsed
        self._timer = None

        if start:
            self.start()

    def start(self):
        """ Start the stopwatch. """

        if self._timer is None:
            self._timer = timenow()

    def stop(self):
        """ Stop the stopwatch. """
        if self._timer is not None:
            now = timenow()
            delta = timedelta(now, self._timer)
            self._timer = None

            self._elapsed += timesecs(delta)

        return self._elapsed

    def reset(self):
        """ Reset the timer. """
        current = self.stop()
        self._elapsed = 0.0
        self._timer = None

        return current

    @property
    def time(self):
        """ Return the elapsed stopwatch time. """
        if self._timer:
            now = timenow()
            delta = timedelta(now, self._timer)
            
            return self._elapsed + timesecs(delta)
        else:
            return self._elapsed

    def __enter__(self):
        """ Allow use as context manager. """
        self.start()
        return self

    def __exit__(self, type, value, tb):
        """ Stop stopwatch on exit. """
        self.stop()

    def __int__(self):
        """ Cast to integer. """
        return int(self.time)

    def __float__(self):
        """ Cast to float value. """
        return float(self.time)

    def __bool__(self):
        """ Return if the stopwatch is running. """
        return self._timer is not None

    __nonzero__ = __bool__

    def __str__(self):
        """ Return the value as a string. """
        return str(self.time)

    def __repr__(self):
        return "{0}.{1}({2}, {3})".format(
            self.__class__.__module__,
            self.__class__.__name__,
            bool(self),
            float(self)
        )



