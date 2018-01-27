""" Utility functions and classes. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import os
import shutil


__all__.append("updatedoc")
def updatedoc(prepend, append):
    """ A decorator to prepend or append to an object's doc string. """
    def wrapper(obj):
        obj.__doc__ = "{0}{1}{2}".format(
            prepend if prepend else "",
            obj.__doc__ if obj.__doc__ else "",
            append if append else ""
        )
        return obj

    return wrapper


__all__.append("FileMover")
class FileMover(object):
    """ A context manager class to remove a temporary file if not commited to a real file. """

    def __init__(self, realfile, tempfile):
        """ Specify the name of the real and temp files. """
        self._realfile = realfile
        self._tempfile = tempfile
        self._committed = False

    def commit(self):
        """ Move the tempfile to the realfile. """
        if os.path.exists(self._tempfile):
            shutil.move(self._tempfile, self._realfile)
            self._committed = True

    def release(self):
        """ Remove temp file if not commited. """
        if (not self._committed) and os.path.exists(self._tempfile):
            os.unlink(self._tempfile)

    def __enter__(self):
        """ Provide context manager to release at end of context/with statement. """
        return self

    def __exit__(self, type, value, traceback):
        """ Release the filemover. """
        self.release()
        return False


__all__.append("common_start")
def common_start(ina, inb):
    """ Return the common part at the beginning of two strings. """
    result = []
    for (a, b) in zip(ina, inb):
        if a == b:
            result.append(a)
        else:
            break

    return ''.join(result)

__all__.append("strip_unneeded_whitespace")
def strip_unneeded_whitespace(what):
    """ Strip empy leading and trailing lines, all whitespace from blank lines,
        common leading whitespace and all tailing whitespace from non-blank lines. """
    lines = what.splitlines()

    # Remove leading and trailing empty lines
    while lines and len(lines[0].strip()) == 0:
        lines.pop(0)

    while lines and len(lines[-1].strip()) == 0:
        lines.pop()

    # Need at least two lines for comparison
    if len(lines) == 0:
        return ""
    elif len(lines) == 1:
        return lines[0].strip()

    # Determine common leading portion of lines
    common = lines[0]
    for (i, line) in enumerate(lines[1:], 1):

        if len(line.strip()) == 0:
            # Ignore blank lines and strip any space on them
            lines[i] = ""
        else:
            # Find match between current common and current line
            common = common_start(common, line)

    # Remove common starting whitespace
    start = len(common) - len(common.lstrip())
    outlines = [line[start:].rstrip() if line else "" for line in lines]

    return '\n'.join(outlines)

