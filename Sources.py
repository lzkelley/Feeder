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

# import json, pandas
import os
from configobj import ConfigObj
import MyLogger, Settings, Utils
from enum import Enum
from datetime import datetime
import numpy as np

import zcode.InOut as zio

__version__ = 0.1

'''
class SRC(object):
    """
    Column keys for Sources `DataFrame`.
    """
    URL = 'url'
    TIT = 'title'
    SUB = 'subtitle'
# } class SRC_COL
'''

'''
class KEYS_SAVE(object):
    DATA = 'data'
    VERS = 'version'
    DTCR = 'datetime_created'
    DTSV = 'datetime_saved'
    SVLS = 'savefile_list'

# } class KEYS_SAVE

SOURCES_COLUMNS = [ SRC.URL, SRC.TIT, SRC.SUB ]
'''

class SOURCES_KEYS(object):
    VERS = 'version'
    SAVE_LIST = 'savefile_list'
    SOURCES_URL = 'sources_url'
    SOURCES_TITLE = 'sources_title'
    SOURCES_SUBTITLE = 'sources_subtitle'



class Source(object):

    def __init__(self, url, title, subtitle=""):
        self.url = url
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
        clean :
        add  :
        delete :
        _del_url :

    """

    def __init__(self, fname=None, log=None, sets=None):
        """

        """
        # Load settings (singleton)
        if( sets is None ): sets = Settings.Settings()
        self.log = _getLogger(log, sets)
        # Set default filename
        if( fname is None ): fname = sets.file_sources

        loaded = False

        # Load data from save file
        if( os.path.exists(fname) ):
            self.log.debug("Loading from '%s'" % (fname))
            retval = self.load(fname)
            if( retval ):
                self.log.debug(" - Loaded  v%s" % (str(self.version)))
                loaded = True
            else:
                errStr = "Load Failed!"
                self.log.error(errStr)
                raise RuntimeError(errStr)
        else:
            self.log.warning("File '%s' does not exist!" % (fname))


        # Create new
        if( not loaded ):

            # initialize values
            self.log.warning("Initializing new Sources")
            self.new()
            # save
            self.log.info("Saving")
            retval = self.save(fname=fname)
            if( not retval ): self.log.error("Error, not saved!!")

        return

    # } __init__()


    def new(self, inter=True):
        """
        """
        self.log.debug("new()")

        if( inter ):
            confirm = self._confirm_unsaved()
            if( not confirm ): return False

        self.version = __version__
        self.savefile_list = []
        self.savefile = None

        self.sources_url = []
        self.sources_title = []
        self.sources_subtitle = []

        self.saved = True
        self.count = 0

        return True

    # } new()


    def load(self, fname, inter=True):
        """
        """

        self.log.debug("load()")

        if( inter ):
            confirm = self._confirm_unsaved()
            if( not confirm ): return False

        ## Try to load file and convert to DataFrame
        #  -----------------------------------------
        try:
            self.log.debug("Loading from '%s'" % (fname))
            config = ConfigObj(fname)
            self.version = config[SOURCES_KEYS.VERS]
            self.savefile_list = config[SOURCES_KEYS.SAVE_LIST]
            self.sources_url = config[SOURCES_KEYS.SOURCES_URL]
            self.sources_title = config[SOURCES_KEYS.SOURCES_TITLE]
            self.sources_subtitle = config[SOURCES_KEYS.SOURCES_SUBTITLE]
        except:
            import sys
            self.log.error("Could not load!! {0:s} : {1:s}".format(*sys.exc_info()))
            retval = False
        else:
            retval = True
            self.savefile = fname
            self.saved = True
            self._recount()

        return retval

    # } load()


    def save(self, fname=None):
        """
        """
        self.log.debug("save()")

        retval = False

        if( fname is None ):
            if( self.savefile is not None ): fname = self.savefile
            else:
                self.log.error("``savefile`` is not set, ``fname`` must be provided!")
                return retval


        zio.checkPath(fname)


        self.log.debug("Creating ``ConfigObj``")
        config = ConfigObj()
        config.filename = fname
        config[SOURCES_KEYS.VERS] = self.version
        config[SOURCES_KEYS.SAVE_LIST] = self.savefile_list
        config[SOURCES_KEYS.SOURCES_URL] = self.sources_url
        config[SOURCES_KEYS.SOURCES_TITLE] = self.sources_title
        config[SOURCES_KEYS.SOURCES_SUBTITLE] = self.sources_subtitle

        self.log.debug("Writing ``ConfigObj``")
        config.write()


        if( os.path.exists(fname) ):
            retval = True

            self.log.info("Saved to '%s'" % (fname))
            self.savefile = fname
            self.saved = True
            if( not fname in self.savefile_list ):
                self.savefile_list.append(fname)


        return retval

    # } save()


    '''
    def clean(self, log):
        """
        Perform cleaning operations on DataFrame.
        """
        log.debug("clean()")
        # must convert to integer before reindexing! (not sure why...)
        self.data.index = self.data.index.astype(int)
        self.data = self.data.reindex(index=np.arange(len(self.data)))
        return

    # } clean()
    '''

    def add(self, url, title='', subtitle='', check=True):
        """
        Add an entry to sources.
        """
        self.log.debug("add()")

        if( check and not zio.checkURL(url) ):
            self.log.warning("URL '%s' does not exist!" % (url))
            return False

        self.sources_url.append(url)
        self.sources_title.append(title)
        self.sources_subtitle.append(subtitle)

        if( not self._recount() ):
            self.sources_url.pop()
            self.sources_title.pop()
            self.sources_subtitle.pop()
            return False


        self.saved = False
        return True

    # } add()


    def delete(self, index, inter=True):
        """
        Remove an entry from sources.
        """
        self.log.debug("delete()")

        if( inter ):

            conf = zio.promptYesNo('Are you sure ')

        return

    # } delete()


    '''
    def _del_url(self, url):
        """
        Remove an entry from the sources DataFrame using the url address.
        """
        self.data = self.data[self.data.xs(SRC.URL,axis=1) != url]
        return
    # } _del_url()
    '''

    def src(self, index=None):
        import numbers
        if( isinstance(index, numbers.Integral) ): 
            cut = slice(index, index+1)
            ids = np.arange(index, index+1)
        elif( np.iterable(index) ): 
            cut = index
            ids = index
        else:
            if( index is not None ):
                self.log.error("Unrecognized `index` = '%s'!" % (str(index)))
                self.log.warning("Returning all entries")

            cut = slice(None)
            ids = np.arange(len(self.sources_url))

        urls = np.array(self.sources_url)
        tits = np.array(self.sources_title)
        subs = np.array(self.sources_subtitle)

        return ids, zip(urls[cut], tits[cut], subs[cut])
    # } src()


    def list(self, index=None):
        """
        List all sources in DataFrame.
        """
        self.log.debug("list()")

        ids, srcs = self.src(index=index)
        for id,src in zip(ids, srcs):
            print "\t",self._str_src(id, src)

        return
    # } list()

    def _str_src(self, id, src):
        """
        """

        url,tit,sub = src

        tstr = tit
        if( len(sub) > 0 ): tstr += " - " + sub

        pstr = "{0:>4d} : {1:{twid}.{twid}}   {2:{uwid}.{uwid}s}"
        pstr = pstr.format(id, tstr, url, twid=40, uwid=60)

        return pstr

    # } _str_row()




    def _confirm_unsaved(self):
        if( hasattr(self, 'saved') ):
            if( not self.saved ):
                return zio.promptYesNo('This will overwrite unsaved data, are you sure?')

        return True


    def _recount(self):

        self.log.debug("_recount()")
        uselists = [ self.sources_url, self.sources_title, self.sources_subtitle ]
        counts = [ len(onelist) for onelist in uselists ]

        if( len(set(counts)) == 1 ): self.log.debug("All lists have length %d" % (counts[0]))
        else:
            self.log.error("Sources list lengths do not match '%s'!" % (str(counts)))
            return False

        self.count = counts[0]
        return True

    # } _recount()


    def addAll(self):
        srclist = [
            ["http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
             "NewYork Times",
             "HomePage"],
            ["http://www.npr.org/rss/rss.php?id=1001",
             "NPR",
             "News"],
            ["http://feeds.washingtonpost.com/rss/world",
             "Washingtong Post",
             "World"],
            ["http://rss.cnn.com/rss/cnn_topstories.rss",
             "CNN",
             "Top Stories"],
            ["http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305",
             "Associated Press",
             "Top Headlines"],
            ["http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
             "USA Today",
             "News Top Stories"],
            ["http://feeds.reuters.com/reuters/topNews",
             "Reuters",
             "Top News"],
            ["http://feeds.bbci.co.uk/news/rss.xml",
             "BBC News",
             "Top News"],
            ["http://feeds.foxnews.com/foxnews/latest",
             "Fox News",
             "Latest News"],
            ["http://www.forbes.com/real-time/feed2/",
             "Forbes",
             "Latest Headlines"],
            ["http://feeds.foxnews.com/foxnews/latest",
             "Fox News",
             "Latest News"],
            ["http://www.ft.com/rss/home/us",
             "Financial Times",
             "US Home"],
            ["http://feeds.abcnews.com/abcnews/topstories",
             "ABC News",
             "Top Stores"],
            ["http://www.theguardian.com/uk/rss",
             "The Guardian",
             "UK Home"]
            ]

        for src in srclist:
            print "Adding ", src[0]
            self.add( src[0], src[1], src[2], check=False )

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

    prompt = "\tAction?  [q]uit, [a]dd, [d]elete, [l]ist, [f]ind, [s]ave, [h]elp : "
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
        elif( arg.startswith('f') ):
            _inter_find(sources, log)
        elif( arg.startswith('s') ):
            _inter_save(sources, log)
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

    # URL
    example = 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
    while( True ):
        url = raw_input("\tURL (e.g. '%s') : " % (example))
        url = url.strip().lower()
        # Catch 'q'uit request
        if( url == 'q' ):
            log.debug("Break '%s'" % (url))
            return

        # Make sure URL exists
        else:
            if( Utils.checkURL(url) ):
                log.debug("Valid URL '%s'" % (url))
                break
            else:
                log.warning("URL does not exist!  '%s'" % (url))
                if( not url.startswith('http://') ):
                    log.warning(" - Maybe something starting with 'http://'??")


    # Title
    titl = raw_input("\tTitle (e.g. 'NewYork Times'): ")
    titl = titl.strip()

    # Subtitle
    subt = raw_input("\tSubtitle : (e.g. 'HomePage') : ")
    subt = subt.strip()

    # Add New Source
    sources.add(url, title=titl, subtitle=subt)

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


def _inter_find(sources, log):
    log.debug("_inter_find()")

    return

# } _inter_find()


def _inter_save(sources, log):
    """
    """
    log.debug("_inter_save()")

    FILE_TYPE = '.json'

    saveName = None
    if( sources.savefile is not None ):
        arg = raw_input("\tSave to loaded filename '%s' ? y/[n] : " % (sources.savefile))
        arg = arg.strip().lower()
        if( arg.startswith('q') ):
            log.debug("arg '%s', canceling save" % (arg))
            return
        elif( arg.startswith('y') ):
            saveName = sources.savefile


    while( saveName is None ):
        saveName = raw_input("\tEnter (json) save filename : ").strip()
        if( saveName.lower() == 'q' ):
            log.debug("saveName '%s', canceling save" % (saveName))
            return
        elif( not saveName.lower().endswith(FILE_TYPE) ):
            saveName += FILE_TYPE

        if( os.path.exists(saveName) ):
            arg = raw_input("\tFile '%s' already exists, overwrite? y/[n] : ")
            arg = arg.strip().lower()
            if( arg.startswith('q') ):
                log.debug("arg '%s', canceling save" % (arg))
                return
            elif( arg.startswith('y') ):
                break
            else:
                saveName = None


    print "SAVENAME = ", saveName


    return

# } _inter_save()



def _inter_help(sources, log):
    log.debug("_inter_help()")

    return

# } _inter_help()




def _getLogger(log=None, sets=None):
    """
    Get a standard ``logging.Logger`` object for ``Sources.py``.
    """
    if( sets is None ): sets = Settings.Settings()

    useDir = sets.dir_log
    verbose = sets.verbose
    debug = sets.debug

    filename = useDir + "Sources.log"
    log = MyLogger.defaultLogger(log, filename=filename, verbose=verbose, debug=debug)
    return log
# } _getLogger()


'''
def _convertKeys(fname, oldKeys, newKeys):
    """
    """

    import shutil, filecmp

    print "Attempting to convert keys in '%s'" % (fname)
    print "\tFrom: '%s'" % (str(oldKeys))
    print "\tTo  : '%s'" % (str(newKeys))

    # Create backup
    pth, oldName = os.path.split(fname)
    newName = ".back_" + oldName
    newName = os.path.join(pth, newName)
    print "Creating backup file:"
    print "\t'%s' ==> '%s'" % (fname, newName)

    shutil.copy2(fname, newName)
    if( not os.path.exists(newName) ): raise RuntimeError("File not Copied!")
    else: print "Backup created."
    if( not filecmp.cmp(fname, newName) ): raise RuntimeError("Files do not match!")
    else: print "Backup matches."

    # Convert file
    loadFile = open(fname, 'r')
    loadData = json.load(loadFile)

    print loadData.keys()

    saveData = { nkey : loadData[okey] for (nkey,okey) in zip(newKeys, oldKeys) }
    print "LOADED: "
    print loadData
    print "\n"
    print "SAVING: "
    print saveData
    print "\n"

    return

# } _convertKeys()
'''




if( __name__ == "__main__" ): main()
