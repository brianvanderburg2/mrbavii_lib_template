""" Functions/classes to aid with downloading. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []

import contextlib

from ..util import updatedoc


# These function implement a generic method to download multiple files.

_download_doc = """

    host:
        The host name or IP to download from.
    root:
        The root directory on the host
    dest:
        The local root directory to save files to
    files:
        A list of files relative to the root to be downloaded.
    progress:
        A callback function to provide progress.
    onerror:
        A callback function to handle an error.  By default the exception
        is raised.
"""

# host: The HOST ip or name to download from
# root: The root directory under that host name to download from
# dest: A destination directory in which the files will be placed
# files: A list of files to download, related to the root on the host
# progress: A callback used to display progress:
# onerrr: A callback that can be called during errors.  If not set
#         the exception will be raised.

def _download_progress_fn(stage, url, filename, downloaded, size):
    """ The progress function called during a download.

        stage: Which stage is the download at.  This can be used to control
        the output such as printing a new line.
            0 - starting
            1 - in progress
            2 - done

        url: The url tht is being downloaded
        filename: The filename being saved to
        downloaded: The number of bytes downloaded so far
        size: The size of the download, may be None.
    """

def _download_error_fn():
    """ The error function called during a download. """
    pass


@updatedoc(None, _download_doc)
def _download_urllib(host, root, dest, files, progress=None, onerror=None, _method=None):
    """ Download files using python. """

    baseurl = _method + "://" + host
    if root:
        baseurl += "/" + root

    block_size = 8192
    
    for file in files:
        thisurl = baseurl + "/" + file
        thisdest = os.path.join(dest, file)

        thisdir = os.path.dirname(thisdest)
        if not os.path.exists(thisdir):
            os.makedirs(thisdir)

        # Python 2
        import urllib2

        if progress:
            progress(0, thisurl, thisdest, 0, 0)

        filegot = 0
        filesize = None
        try:
            with contextlib.closing(urllib2.urlopen(thisurl)) as inhandle, open(thisdest, "wb") as outhandle:
                info = inhandle.info()

                try:
                    filesize = int(info.getheaders("Content-Length")[0])
                except ValueError:
                    filesize = None

                while True:
                    inbuf = inhandle.read(block_size)
                    if not inbuf:
                        break

                    filegot += len(inbuf)
                    if progress:
                        progress(1, thisurl, thisdest, filegot, filesize)

                    outhandle.write(inbuf)
        finally:
            if progress:
                progress(2, thisurl, thisdest, filegot, filesize)


__all__.append("download_http")
@updatedoc(None, _download_doc)
def download_http(host, root, dest, files, progress=None, onerror=None):
    """ Download files using HTTP. """
    return _download_urllib(host, root, dest, files, progress, onerror, "http")

__all__.append("download_https")
@updatedoc(None, _download_doc)
def download_https(host, root, dest, files, progress=None, onerror=None):
    """ Download files using HTTPS. """
    return _download_urllib(host, root, dest, files, progress, onerror, "https")

__all__.append("download_ftp")
@updatedoc(None, _download_doc)
def download_ftp(host, root, dest, files, progress=None, onerror=None):
    """ Download files using FTP. """
    return _download_urllib(host, root, dest, files, progress, onerror, "ftp")


