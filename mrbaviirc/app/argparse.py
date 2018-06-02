""" Argument parser for applications. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import argparse


from ..util.imp import Exporter
export = Exporter(globals())


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

