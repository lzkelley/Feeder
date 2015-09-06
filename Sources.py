"""

Objects
-------
    Source


Functions
---------
    main :
    _getLogger :
    _getArgs :

    

"""

import json, pandas, os
import MyLogger, Settings, Utils
from enum import Enum
from datetime import datetime

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
        remove :

    """

    def __init__(self, fname=None, log=None, sets=None):
        """

        """
        log = _getLogger(log, sets)

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
            self.data = pandas.DataFrame.from_dict(loadData[KEYS_SAVE.DATA])
            self.version = loadData[KEYS_SAVE.VERS]
            self.datetime_created = loadData[KEYS_SAVE.DTCR]
            self.datetime_saved = loadData[KEYS_SAVE.DTSV]
            retval = True

        except:
            import sys
            log.warning("Could not load!! {0:s} : {1:s}".format(*sys.exc_info()))
            retval = False

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


    def remove(self, html):
        """
        Remove an entry from the sources DataFrame.
        """
        self.data = self.data[self.data.xs(SRC.HTML,axis=1) != html]
        return
    # } remove() 


    def addAll(self):
        for src in sources:
            self.add(src.html, src.title, src.subtitle)

        return
        

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
    sources = Sources(sets)

    log.info("done.")

    return

# } main()


sources = [ 
    Source("http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", 
           "NewYork Times", 
           "HomePage"),
    Source("http://www.npr.org/rss/rss.php?id=1001", 
           "NPR", 
           "News"),
    Source("http://feeds.washingtonpost.com/rss/world",
           "Washingtong Post",
           "World"),
    Source("http://rss.cnn.com/rss/cnn_topstories.rss",
           "CNN",
           "Top Stories"),
    Source("http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305",
           "Associated Press",
           "Top Headlines"),
    Source("http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
           "USA Today",
           "News Top Stories"),
    Source("http://feeds.reuters.com/reuters/topNews",
           "Reuters",
           "Top News"),
    Source("http://feeds.bbci.co.uk/news/rss.xml",
           "BBC News",
           "Top News"),
    Source("http://feeds.foxnews.com/foxnews/latest",
           "Fox News",
           "Latest News"),
    Source("http://www.forbes.com/real-time/feed2/",
           "Forbes",
           "Latest Headlines"),
    Source("http://feeds.foxnews.com/foxnews/latest",
           "Fox News",
           "Latest News"),
    Source("http://www.ft.com/rss/home/us",
           "Financial Times",
           "US Home"),
    Source("http://feeds.abcnews.com/abcnews/topstories",
           "ABC News",
           "Top Stores"),
    Source("http://www.theguardian.com/uk/rss",
           "The Guardian",
           "UK Home")
    ]



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
