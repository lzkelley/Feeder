"""

"""


def checkPath(tpath):
    """
    Create the given filepath if it doesn't already exist.
    """
    import os
    path,name = os.path.split(tpath)
    if( len(path) > 0 ):
        if( not os.path.isdir(path) ): os.makedirs(path)

    return path

# } _checkPath()


def checkURL(url, codemax=200, timeout=[1.0,1.0]):
    """
    Check that the given url exists.

    Note on ``status_code``s (see: 'https://en.wikipedia.org/wiki/List_of_HTTP_status_codes')
        1xx - informational
        2xx - success
        3xx - redirection
        4xx - client error
        5xx - server error

    """

    import requests, logging
    retval = False
    try:
        logging.getLogger("requests").setLevel(logging.WARNING)
        req = requests.head(url) #, timeout=timeout)
        retval = (req.status_code <= codemax)
    except:
        pass

    return retval

# } checkURL()
