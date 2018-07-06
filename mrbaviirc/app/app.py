""" App app helper functions and classes. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


import threading
import argparse


from ..util.imp import Exporter
from .base import BaseAppHelper
from .argparse import ArgumentParser


export = Exporter(globals())


@export
class AppHelper(BaseAppHelper):
    """ The application helper oject. """

    # Initialization

    def __init__(self):
        """ Initialize. """

        BaseAppHelper.__init__(self)

        self._args = None

    @property
    def args(self):
        """ Return the command line. arguments. """
        return self._args

    def create_arg_parser(self):
        """ Create and return the command line argument parser. """
        parser = ArgumentParser(description=self.description)

        return parser

    def parse_args(self, parser):
        """ Parse the command line arguments. """
        return self._parser.parse_args()

    # Execution related methods. """

    def execute(self):
        """ External method to execute the application. """
        self.startup()
        self.main()
        self.shutdown()

    def startup(self):
        """ Perform startup here. """
        BaseAppHelper.startup(self)

        parser = self.create_arg_parser()
        if parser:
            self._args = self.parse_args(parser)

    def main(self):
        """ Run application main code here. """
        raise NotImplementedError

