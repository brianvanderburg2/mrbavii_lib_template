""" Customer wxPython Art provider """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


__all__ = ["ArtProvider"]

import os

from collections import OrderedDict

import wx


class ArtProvider(wx.ArtProvider):
    """ This art provider allow specification of a directory that contains
        PNG images.  The available sizes are auto-discovered based on a
        dictory naming of <width>x<height> (ie 32x32).  A "default" directory
        is used as a fallpback directory.
    """
    
    def __init__(self, path):
        """ Create the art provider with the specified path and auto-discover
            available sizes from subdirectories. """

        wx.ArtProvider.__init__(self)
        self._default = None
        self._sizes = OrderedDict()

        # Learn our paths
        try:
            subdirs = os.listdir(path)
        except (IOError, OSError) as e:
            return
        
        widths = {}
        for subdir in subdirs:
            # Ignore starting with "."
            if subdir[0:1] == ".":
                continue

            # Dirs only
            fullpath = os.path.join(path, subdir)
            if not os.path.isdir(fullpath):
                continue

            # Is it our default dir
            if subdir == "default":
                self._default = fullpath
                continue

            # Only support WxH
            parts = subdir.split("x")
            if len(parts) != 2:
                continue

            try:
                (width, height) = (int(parts[0]), int(parts[1]))
            except ValueError:
                continue

            if width < 1 or height < 1:
                continue

            # We now have our width and height
            if not width in widths:
                widths[width] = {}
            widths[width][height] = fullpath


        # Now we want to sort them
        self._sizes = OrderedDict()
        for width in sorted(widths.keys()):
            self._sizes[width] = OrderedDict()
            for height in sorted(widths[width].keys()):
                self._sizes[width][height] = widths[width][height]


    def _find_file(self, filename, width, height):
        """ Find a file that best matches the requested size. """
        # Do we have an exact match
        if width in self._sizes and height in self._sizes[width]:
            path = self._sizes[width][height]
            fullpath = os.path.join(path, filename)

            if os.path.isfile(fullpath):
                return fullpath

        # Find best image based on aspect ratios just larger than or equal to
        # our desired size if available.  If a larger image is not available
        # then a smaller image, if available, will be used and scaled up
        ZERODIFF = 0.01 # To deal with rounding errors, etc
        best = None
        requested_aspect = float(width) / float(height)

        for our_width in self._sizes:
            for our_height in self._sizes[our_width]:

                # First make sure the file exists under the size directory
                path = self._sizes[our_width][our_height]
                fullpath = os.path.join(path, filename)

                if not os.path.isfile(fullpath):
                    continue

                # Determine the difference in aspect ratio of the current
                # size directory and our requested size
                our_aspect = float(our_width) / float(our_height)
                diff = abs(requested_aspect - our_aspect)

                if diff < ZERODIFF and our_width >= width:
                    # If the aspect is essentially the same, return the first
                    # larger or equal image
                    return fullpath

                if best is None or diff < best[0] - ZEORDIFF:
                    # First found image or found a closer aspect ratio
                    best = (diff, fullpath, our_width)
                elif abs(diff - best[0]) < ZERODIFF and best[2] < width:
                    # Found an equal aspect ratio to the last found one (but
                    # maybe not equal to target), and last image was smaller than
                    # target so prefer this image
                    best = (diff, fullpath, our_width)
                    
        if best:
            return best[1]

        if self._default:
            fullpath = os.path.join(self._default, filename)

            if os.path.isfile(fullpath):
                return fullpath

        return None


    def CreateBitmap(self, artid, artclient, size):
        """ Create a bitmap based on the requested artid name and size.
            Currently we do not use art client. """
        
        filename = str(artid) + ".png"
        fullpath = self._find_file(filename, size.width, size.height)

        if fullpath:
            return wx.BitmapFromImage(wx.Image(fullpath))
        else:
            return wx.NullBitmap




