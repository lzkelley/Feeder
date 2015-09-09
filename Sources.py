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
    _interactive :
    _inter_add : Interactively add a new ``Sources`` entry.
    _inter_del : Interactively delete a ``Sources`` entry.
    _inter_list : List all ``Sources`` entries.
    _inter_find :
    _inter_save :
    _inter_help : 
    _getLogger :


"""

# import json, pandas
import os, shutil
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





class Sources(object):
    """

    Functions
    ---------
        new  : Initialize a new (or clear existing) state.
        load : Load sources list from the given filename.
        save : Save ``Sources`` state to file.
        add  : Add one or multiple entries to sources.
        delete : Remove one or multiple entries from sources.
        _src : Retrieve one or multiple sources from list (default: return all).
        list : List some or all sources to stdout.
        _str_src : Create a string representation of a single source.
        _confirm_unsaved : If there is unsaved data, Prompt user (via CLI) to confirm overwrite.
        _recount : Count the current number of sources and assure all lists match in length.
        _same_size : Check whether all of the given arrays or lists are the same size.

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
                self.log.debug(" - Sources: %d" % (self.count))
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




    def new(self, inter=True):
        """
        Initialize a new (or clear existing) state.

        Arguments
        ---------
            inter <bool> : interactive, if so prompt if unsaved changes exist.

        Returns
            retval <bool> : True if new state is created.

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

        self._saved = True
        self.count = 0

        return True




    def load(self, fname, inter=True):
        """
        Load sources list from the given filename.

        Arguments
        ---------
            fname <str>  : filename to load from.
            inter <bool> : interactive, if so, prompt if unsaved changes.
        """

        self.log.debug("load()")

        # Confirm lose unsaved changes
        if( inter ):
            confirm = self._confirm_unsaved()
            if( not confirm ): return False

        # Try to load file and extract elements
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
        # Add appropriate metadata on success
        else:
            retval = True
            self.savefile = fname
            self._saved = True
            self._recount()
            

        return retval



    def save(self, fname=None, inter=True):
        """
        Save ``Sources`` state to file.

        In interactive mode (``inter`` == 'True'), prompts user if overwriting existing savefile.
        If overwriting, backup file is created.
        
        Arguments
        ---------
            fname <str>  : filename to save to
            inter <bool> : interactive, if true, prompt for file overwrite

        Returns
        -------
            retval <bool> : `True` on successful save, otherwise `False`.

        """

        self.log.debug("save()")

        retval = False

        # Use preset save filename if it exists
        if( fname is None ):
            if( self.savefile is not None ): fname = self.savefile
            else:
                self.log.error("``savefile`` is not set, ``fname`` must be provided!")
                return retval


        # Setup data using ``ConfigObj``
        self.log.debug("Creating ``ConfigObj``")
        config = ConfigObj()
        config.filename = fname
        config[SOURCES_KEYS.VERS] = self.version
        config[SOURCES_KEYS.SAVE_LIST] = self.savefile_list
        config[SOURCES_KEYS.SOURCES_URL] = self.sources_url
        config[SOURCES_KEYS.SOURCES_TITLE] = self.sources_title
        config[SOURCES_KEYS.SOURCES_SUBTITLE] = self.sources_subtitle


        # Make sure path exists, confirm overwrite in interactive mode
        zio.checkPath(fname)
        if( os.path.exists(fname) and inter ):
            conf = zio.promptYesNo("Destination '%s' already exists, overwrite?" % (fname))
            if( not conf ): return False

            # Create backup filename
            oldPath, oldName = os.path.split(fname)
            backname = os.path.join(oldPath, ".backup_" + oldName)
            # If backup already exists, delete
            if( os.path.exists(backname) ):
                self.log.info("Backup '%s' already exists.  Deleting." % (backname))
                os.remove(backname)

            # Move old file to backup
            self.log.info("Moving '%s' ==> '%s'" % (fname, backname))
            shutil.move(fname, backname)
            # Look for problems
            if( os.path.exists(fname) ):
                self.log.error("Old file '%s' still exists!" % (fname))
                return False

            if( not os.path.exists(backname) ):
                self.log.error("Backup '%s' does not exist!" % (backname))
                self.log.error("Lets hope the save works...")


        # Save data
        self.log.debug("Writing ``ConfigObj``")
        config.write()

        # Make sure its saved
        if( os.path.exists(fname) ):
            retval = True
            self._recount()
            self.log.info("Saved %d sources to '%s'" % (self.count, fname))
            self.savefile = fname
            self._saved = True
            if( not fname in self.savefile_list ):
                self.savefile_list.append(fname)

        else:
            self.log.error("Save to '%s' failed!" % (fname))
            return False

        return retval



    def add(self, url, title=None, subtitle=None, check=True):
        """
        Add one or multiple entries to sources.

        If ``title`` and/or ``subtitle`` are provided, they must match length of ``url``.
        
        Arguments
        ---------
            url      <str>([N])  : URL of new entry/entries.
            title    <str>([N])  : Titles of new entries.
            subtitle <str>([N])  : Subtitles of new entries.
            check    <bool>      : Check each URL for existence before adding.

        Returns
        -------
            retval <bool> : success if all passed entries were added.

        """
        self.log.debug("add()")

        # Make sure url(s) is(are) iterable
        if( isinstance(url, str) ): url = [ url ]
        # If no title/subtitle are provided, set to empty strings
        if( title is None ): title = ['']*np.size(url)
        if( subtitle is None ): subtitle = ['']*np.size(url)

        # Make sure all arrays are the same length
        if( not self._same_size(url, title, subtitle) ):
            self.log.error("values to add are not the same length!")
            return False

        # Iterate over and add all new entries
        retval = True
        for uu, tt, ss in zip(url, title, subtitle):
            # Check that url exists, skip if not
            if( check and not zio.checkURL(uu) ):
                self.log.warning("URL '%s' does not exist, skipping!" % (uu))
                retval = False
                continue

            self.sources_url.append(uu)
            self.sources_title.append(tt)
            self.sources_subtitle.append(ss)


        # update metadata
        self._recount()
        self._saved = False

        return retval



    def delete(self, index, inter=True):
        """
        Remove one or multiple entries from sources.
        
        Arguments
        ---------
            index <int>([N]) : index or indices to delete.
            inter <bool>     : interactive, if so, confirm delete.

        Returns
        -------
            retval <bool> : ``True`` on successful deletion

        """
        self.log.debug("delete()")

        if( inter ):
            print "Delete the following sources: "
            self.list(index)
            conf = zio.promptYesNo('Are you sure?')
            if( not conf ): return False

        if( not np.iterable(index) ): index = [index]

        # Iterate over IDs and delete
        #     MUST REVERSE ITERATE so that index numbers are preserved for subsequent entries.
        del_url = []
        del_tit = []
        del_sub = []
        for id in reversed(index):
            del_url.append(self.sources_url.pop(id))
            del_tit.append(self.sources_title.pop(id))
            del_sub.append(self.sources_subtitle.pop(id))

        self.log.info("Deleted URLs:")
        for url in del_url:
            self.log.info(" - '%s'" % (url))

        self._recount()
        self._saved = False

        return True




    def _src(self, index=None):
        """
        Retrieve one or multiple sources from list (default: return all).

        Arguments
        ---------
            index <obj> : target index or indices to retrieve.

        Returns
        -------
            ids  <int>([N])   : returned index numbers.
            srcs <str>[(N),3] : sources, each is {url, title, subtitle}
        
        """
        self.log.debug("_src()")

        ## Convert index to a slicing object
        import numbers
        # Single integer number
        if( isinstance(index, numbers.Integral) ): 
            cut = slice(index, index+1)
            ids = np.arange(index, index+1)
        # List of numbers
        elif( np.iterable(index) ): 
            cut = index
            ids = index
        # Otherwise, return all sources
        else:
            if( index is not None ):
                self.log.error("Unrecognized `index` = '%s'!" % (str(index)))
                self.log.warning("Returning all entries")

            cut = slice(None)
            ids = np.arange(len(self.sources_url))

        ## Convert to np.array and slice
        urls = np.array(self.sources_url)
        tits = np.array(self.sources_title)
        subs = np.array(self.sources_subtitle)

        srcs = zip(urls[cut], tits[cut], subs[cut])

        return ids, srcs



    def list(self, index=None):
        """
        List some or all sources to stdout.

        Arguments
        ---------
            index <obj> : int, list of ints, or `None` for all entries.

        """
        self.log.debug("list()")

        # Get entries and ID numbers
        ids, srcs = self._src(index=index)
        # Print each source
        for id,src in zip(ids, srcs):
            print "\t",self._str_src(id, src)

        return



    def _str_src(self, id, src):
        """
        Create a string representation of a single source.

        Arguments
        ---------
            id <int>     : index number
            src <str>[3] : source {url, title, subtitle}

        Returns
        -------
            pstr <str> : formatted string representing source.

        """

        url,tit,sub = src

        tstr = tit
        if( len(sub) > 0 ): tstr += " - " + sub

        pstr = "{0:>4d} : {1:{twid}.{twid}}   {2:{uwid}.{uwid}s}"
        pstr = pstr.format(id, tstr, url, twid=40, uwid=60)

        return pstr


    def _confirm_unsaved(self):
        """
        If there is unsaved data, Prompt user (via CLI) to confirm overwrite.
        
        Returns
        -------
            retval <bool> : `True` on positive confirmation.

        """
        if( hasattr(self, '_saved') ):
            if( not self._saved ):
                return zio.promptYesNo('This will overwrite unsaved data, are you sure?')

        return True



    def _recount(self):
        """
        Count the current number of sources and assure all lists match in length.

        Updated count is stored to `self.count`.

        Returns
        -------
            retval <bool> : `True` if all lengths match.

        """

        self.log.debug("_recount()")
        uselists = [ self.sources_url, self.sources_title, self.sources_subtitle ]

        count = np.size(self.sources_url)
        if( self._same_size(*uselists) ): self.log.debug("All lists have length %d" % (count))
        else:
            self.log.error("Sources list lengths do not match!")
            return False

        self.count = count
        return True


    def _same_size(self, *arrs):
        """
        Check whether all of the given arrays or lists are the same size.

        Arguments
        ---------
            arrs <obj> : any number of comparison arrays.

        Returns
        -------
            retval <bool> : `True` if all are same length

        """
        counts = [ np.size(ar) for ar in arrs ]
        if( len(set(counts)) == 1 ): return True
        return False



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







def main(sets=None, log=None):
    """

    """

    ## Initialization
    #  --------------
    if( sets is None ): sets = Settings.Settings()
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

    prompt = "\n\tAction?  [q]uit, [a]dd, [d]elete, [l]ist, [f]ind, [s]ave, [h]elp : "
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
    Interactively add a new ``Sources`` entry.

    Prompts user for {url, title, subtitle}.

    Arguments
    ---------
        sources <obj> : ``Sources`` object instance
        log     <obj> : ``logging.Logger`` instance

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

    # Title
    titl = raw_input("\tTitle (e.g. 'NewYork Times'): ")
    titl = titl.strip()

    # Subtitle
    subt = raw_input("\tSubtitle : (e.g. 'HomePage') : ")
    subt = subt.strip()

    # Add New Source
    retval = sources.add(url, title=titl, subtitle=subt, check=True)
    if( retval ): log.info("Added entry for '%s'" % (url))
    else: log.error("Could not add entry for '%s'!" % (url))

    return

# } _inter_add()


def _inter_del(sources, log):
    """
    Interactively delete a ``Sources`` entry.
    """
    import numbers
    log.debug("_inter_del()")

    index = raw_input("\tIndex number: ").strip().lower()
    if( index.startswith('q') ):
        log.debug("Break")
        return

    try:
        index = np.int(index)
    except:
        log.error("Could not convert '%s' to integer" % (index))
        return

    retval = sources.delete(index, inter=True)
    if( retval ): log.info("Deleted entry '%d'" % (index))
    else: log.error("Could not delete entry '%d'!" % (index))

    return

# } _inter_del()


def _inter_list(sources, log):
    """
    List all ``Sources`` entries.
    """
    log.debug("_inter_list()")
    sources.list()
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





if( __name__ == "__main__" ): main()
