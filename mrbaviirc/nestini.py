""" This code parses INI files in a nested manor. """

__author__      = "Brian Allen Vanderburg II"
__copyright__   = "Copyright 2016"
__license__     = "Apache License 2.0"


class NestedIniParser(object):
    
    def __init__(self, parser):
        """ Initialize the nexted INI parser. """
        self.parser = parser

    def parse(self):
        """ Parse the INI data and return the results. """

        results = {}
        parser = self.parser
        for section in parser.sections():
            target = self._get_target(results, section)
            for option in parser.options(section):
                target[option] = parser.get(section, option)

        return results
    
    def _isint(self, value):
        """ Is a value an integer. """
        try:
            result = int(value)
            return True
        except ValueError:
            return False

    def _get_target(self, results, section):
        """ Find out where we should put items. """
        parts = section.split(".")
        target = results
        count = len(parts)
        
        for pos in range(count):
            # What kind is it:
            part = parts[pos]

            if self._isint(part):
                # Item before us should be a list
                if not isinstance(target, list):
                    raise ValueError("Must be a list")
                value = int(part)
                if value < 0 or value > len(target):
                    raise ValueError("Invalid index.")
                if value == len(target):
                    if (pos == count - 1) or not self._isint(parts[pos + 1]):
                        target.append({})
                    else:
                        target.append([])
                target = target[value]
            else:
                # Item before us should be a dict
                if not isinstance(target, dict):
                    raise ValueError("Must be a dict")

                value = part
                if not value in target:
                    if (pos == count - 1) or not self._isint(parts[pos + 1]):
                        target[value] = {}
                    else:
                        target[value] = []

                target = target[value]

        if not isinstance(target, dict):
            raise ValueError("Final result must be a dict.")

        return target

