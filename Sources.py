"""

Objects
-------
    SRC
    KEYS_SAVE
    Source
    Sources


Functions
---------
    main :
    _getLogger :


"""

import json, pandas, os
import MyLogger, Settings, Utils
from enum import Enum
from datetime import datetime
import numpy as np

__version__ = 0.1


class SRC(object):
    """
    Column keys for Sources `DataFrame`.
    """
    HTML = 'html'
    TITL = 'title'
    SUBT = 'subtitle'
# } class SRC_COL


class KEYS_SAVE(object):
    DATA = 'data'
    VERS = 'version'
    DTCR = 'datetime_created'
    DTSV = 'datetime_saved'

# } class KEYS_SAVE


SOURCES_COLUMNS = [ SRC.HTML, SRC.TITL, SRC.SUBT ]

class Source(object):

    def __init__(self, html, title, subtitle=""):
        self.html = html
        self.title = title
        self.subtitle = subtitle
        self.name = self.title + " " + self.subtitle

    def __str__(self):
        return self.name


# } class Source



class Sources(object):
    """

    Objects
    -------
        SCOL :

    Functions
    ---------
        load :
        save :
        add  :
        delete :

    """

    def __init__(self, fname=None, log=None, sets=None):
        """

        """
        log = _getLogger(log, sets)

        if( fname is None and sets is not None ):
            fname = sets.file_src

        # Load data from save file
        if( fname is not None ):
            log.debug("Loading")
            retval = self.load(fname, log)
            if( retval ):
                log.debug(" - Loaded  v%s" % (str(self.version)))
                log.debug(" - Created %s" % (self.datetime_created))
                log.debug(" - Saved   %s" % (self.datetime_saved))
            else:
                errStr = "Load Failed!"
                log.error(errStr)
                raise RuntimeError(errStr)

        # Initialize empty DataFrame
        else:
            log.debug("Initializing new Sources DataFrame")
            self.data = pandas.DataFrame(columns=SOURCES_COLUMNS)
            self.version = __version__
            self.datetime_created = str(datetime.now())
            self.datetime_saved = None
            log.debug("Created")

        return

    # } __init__()


    def load(self, fname, log):
        """
        """

        log.debug("load()")

        try:
            log.debug("Loading from '%s'" % (fname))
            loadFile = open(fname, 'r')
            loadData = json.load(loadFile)
            print loadData[KEYS_SAVE.DATA]
            self.data = pandas.DataFrame.from_dict(loadData[KEYS_SAVE.DATA])
        except:
            import sys
            log.warning("Could not load!! {0:s} : {1:s}".format(*sys.exc_info()))
            retval = False
        else:
            # Convert indices to integer type
            # self.data.index = self.data.index.astype(int)
            self.data = self.data.reindex(index=np.arange(len(self.data)))
            self.version = loadData[KEYS_SAVE.VERS]
            self.datetime_created = loadData[KEYS_SAVE.DTCR]
            self.datetime_saved = loadData[KEYS_SAVE.DTSV]
            retval = True


        return retval

    # } load()


    def save(self, fname, log):
        """
        """

        log.debug("save()")
        Utils.checkPath(fname)
        self.datetime_saved = str(datetime.now())

        saveDict = {}
        saveDict[KEYS_SAVE.DATA] = self.data.to_dict()
        saveDict[KEYS_SAVE.VERS] = self.version
        saveDict[KEYS_SAVE.DTCR] = self.datetime_created
        saveDict[KEYS_SAVE.DTSV] = self.datetime_saved

        with open(fname, 'w') as saveFile:
            json.dump(saveDict, saveFile)

        log.info("Saved to '%s'" % (fname))

        return

    # } save()


    def add(self, html, title='', subtitle=''):
        """
        Add an entry to the sources DataFrame.
        """
        temp = pandas.DataFrame({SRC.HTML:[html],
                                 SRC.TITL:[title],
                                 SRC.SUBT:[subtitle]})
        self.data = self.data.append(temp, ignore_index=True)
        return
    # } add()


    def delete(self, html):
        """
        Remove an entry from the sources DataFrame.
        """
        self.data = self.data[self.data.xs(SRC.HTML,axis=1) != html]
        return
    # } delete()

    def list(self, log):
        """
        List all sources in DataFrame.
        """
        log.debug("list()")

        for id,src in self.data.sort().iterrows():
            tstr = src[SRC.TITL]
            if( len(src[SRC.SUBT]) > 0 ): tstr += " - " + src[SRC.SUBT]
            pstr = "{0:>4d} : {1:{twid}.{twid}}   {2:{uwid}.{uwid}s}"
            pstr = pstr.format(id, tstr, src[SRC.HTML], twid=40, uwid=60)
            print pstr

        return
    # } list()



# } class Sources






def main(sets=None, log=None):
    """

    """

    ## Initialization
    #  --------------
    sets = Settings.getSettings(sets)
    log = _getLogger(log, sets)
    log.info("main()")
    log.debug("version = '%s'" % str(__version__))
    log.debug("Settings version = '%s'" % (str(sets.version)))

    # Command-Line Arguments
    log.debug("Getting command line arguments")
    parser = Settings.getParser(sets)
    args, sets = Settings.getArgs(parser, sets)

    # Load Sources
    log.info("Loading Sources")
    sources = Sources(log=log, sets=sets)


    ## Interactive Routine
    #  -------------------
    _interactive(sources, log, sets)


    log.info("Done.")

    return

# } main()


def _interactive(sources, log, sets):
    """

    """
    log.info("_interactive()")

    prompt = "\tAction?  [q]uit, [a]dd, [d]elete, [l]ist, [s]earch, [h]elp : "
    while( True ):
        arg = raw_input(prompt)
        arg = arg.strip().lower()
        log.debug("arg = '%s'" % (arg))
        if(   arg.startswith('q') ):
            log.debug("Quitting interactive")
            break
        elif( arg.startswith('a') ):
            _inter_add(sources, log)
        elif( arg.startswith('d') ):
            _inter_del(sources, log)
        elif( arg.startswith('l') ):
            _inter_list(sources, log)
        elif( arg.startswith('s') ):
            _inter_search(sources, log)
        elif( arg.startswith('h') ):
            _inter_help(sources, log)
        else:
            log.warning("Argument '%s' not understood!" % (arg))
            continue


    return sources, sets

# } _interactive()



def _inter_add(sources, log):
    """
    Add a new ``Sources`` entry.
    """

    log.debug("_inter_add()")

    # HTML
    example = 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
    while( True ):
        html = raw_input("\tHTML (e.g. '%s') : " % (example))
        html = html.strip().lower()
        # Catch 'q'uit request
        if( html == 'q' ):
            log.debug("Break '%s'" % (html))
            return

        # Make sure URL exists
        else:
            if( Utils.checkURL(html) ):
                log.debug("Valid URL '%s'" % (html))
                break
            else:
                log.warning("URL does not exist!  '%s'" % (html))
                if( not html.startswith('http://') ):
                    log.warning(" - Maybe something starting with 'http://'??")


    # Title
    titl = raw_input("\tTitle (e.g. 'NewYork Times'): ")
    titl = titl.strip()

    # Subtitle
    subt = raw_input("\tSubtitle : (e.g. 'HomePage') : ")
    subt = subt.strip()

    # Add New Source
    sources.add(html, title=titl, subtitle=subt)

    return

# } _inter_add()


def _inter_del(sources, log):
    log.debug("_inter_del()")

    return

# } _inter_del()


def _inter_list(sources, log):
    log.debug("_inter_list()")
    sources.list(log)

    return

# } _inter_list()


def _inter_search(sources, log):
    log.debug("_inter_search()")

    return

# } _inter_search()


def _inter_help(sources, log):
    log.debug("_inter_help()")

    return

# } _inter_help()




def _getLogger(log, sets):
    """
    Get a standard ``logging.Logger`` object for ``Sources.py``.
    """
    if( sets is not None ):
        useDir = sets.dir_log
        verbose = sets.verbose
        debug = sets.debug

    else:
        useDir = "./"
        verbose = True
        debug = False

    filename = useDir + "Sources.log"
    log = MyLogger.defaultLogger(log, filename=filename, verbose=verbose, debug=debug)
    return log
# } _getLogger()




if( __name__ == "__main__" ): main()
