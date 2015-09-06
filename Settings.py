"""

Objects
-------
    Settings :


Methods
-------
    getSettings :
    getParser : Get a standard argument parser for the settings.
    getArgs : Modify the ``Settings`` object to the command line arguments, return arguments.


"""

import argparse

__version__ = 0.1


class Settings(object):

    def __init__(self):

        ## Basic Parameters
        #  ----------------
        self.verbose = True
        self.debug = False

        ## Files and Directories
        #  ---------------------
        self.dir_log = "./log/"
        self.dir_data = "./data/"
        
        self.file_src = self.dir_data + "sources.json"
        

        ## Internal Parameters
        #  -------------------
        self.version = __version__
        


# } class Settings


def getSettings(sets=None):
    """
    Get a Settings object.
    """
    if( isinstance(sets, Settings) ): return sets
    else: sets = Settings()
    return sets
# } getSettings()



def getParser(sets):
    """
    Get a standard argument parser for the Settings associated with the ``Settings`` class.
    """

    parser = argparse.ArgumentParser()

    ## Create Arguments
    #  ----------------
    parser.add_argument("-v", "--verbose", 
                        action="store_true", dest="verbose", default=sets.verbose,
                        help="print verbose output to log")

    parser.add_argument("-d", "--debug", 
                        action="store_true", dest="debug", default=sets.debug,
                        help="print highly verbose output to log")

    parser.add_argument("-s", "--sources", 
                        dest="SRC_FILE", default=sets.file_src,
                        help="source file (json).")

    return parser

# } getParser()


def getArgs(parser, sets):
    """
    Modify the ``Settings`` object to the command line arguments, return arguments.
    """

    ## Parse and Store Arguments
    #  -------------------------
    args = parser.parse_args()

    sets.verbose = args.verbose
    sets.debug = args.debug
    sets.file_src = args.SRC_FILE

    return args, sets

# } getArgs()

