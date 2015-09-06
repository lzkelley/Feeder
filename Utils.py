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

# _checkPath()
