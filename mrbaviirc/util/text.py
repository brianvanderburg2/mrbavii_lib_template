""" Text utilities. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2018 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


from .imp import export

@export
def dedent(text):
    """ Removing unneeded whitespace, newlines. """
    import textwrap

    return textwrap.dedent(text).strip()

@export
def striplines(text):
    """ Remove all leading/trailing whitespaces from lines and blank lines. """
    return "\n".join(line.strip() for i in text.splitlines() if len(i.strip()))

@export
def makesingle(text):
    """ Make multiple lines into a single line joined by a space. """
    return " ".join(i.strip() for i in text.splitlines() if len(i.strip()))

