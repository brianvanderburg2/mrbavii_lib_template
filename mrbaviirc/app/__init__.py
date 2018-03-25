""" Application helper functions and classes. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


from .. import platform


class Traits(object):
    """ The traits of an application. """

    def __init__(self, app):
        self._app = app
        self._path = None

    @property
    def path(self):
        if self._path is None:
            self._path = platform.Path(
                self._app.appname,
                self._app.appversion
            )

        return self._path
        

class App(object):
    """ The application oject. """

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
            self._traits = Traits(self)

        return self._traits

    @property
    def cmdline(self):
        """ Return the command line. """
        return self._cmdline

    @property
    def path(self):
        """ Return the application paths."""
        if not self._path:
            self._path = self.traits.path

    def __init__(self):
        self._cmdline = None
        self._traits = None
        self._path = None

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



