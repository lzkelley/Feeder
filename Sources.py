"""

Objects
-------
    SOURCELIST_KEYS
    Source
    SourceList
    

Functions
---------
    main         : Run interactive mode where the user passes options via CLI.
    _inter_add   : Interactively add a new ``SourceList`` entry.
    _inter_del   : Interactively delete a ``SourceList`` entry.
    _inter_find  : 
    _inter_save  : Save current ``SourceList`` to file.


"""

# import json, pandas
import os, shutil
from configobj import ConfigObj
import MyLogger, Settings
from enum import Enum
from datetime import datetime
import numpy as np

import zcode.InOut as zio

__version__ = 0.1

_LOG_FILENAME = 'sources.log'


class SOURCELIST_KEYS(object):
    VERS = 'version'
    SAVE_LIST = 'savefile_list'
    SOURCES_URL = 'sources_url'
    SOURCES_TITLE = 'sources_title'
    SOURCES_SUBTITLE = 'sources_subtitle'


class Source(object):

    def __init__(self, url, title, subtitle):
        self.url = url.lower()
        self.title = title
        self.subtitle = subtitle
        self.name = self.title + " " + self.subtitle

    def __str__(self):
        return self.name





class SourceList(object):
    """

    Functions
    ---------
        new  : Initialize a new (or clear existing) state.
        load : Load sources list from the given filename.
        save : Save ``SourceList`` state to file.
        add  : Add one or multiple entries to sources.
        delete : Remove one or multiple entries from sources.
        _get : Retrieve one or multiple sources from list (default: return all).
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
        self._log = MyLogger.defaultLogger(_LOG_FILENAME, log, sets)
        # Set default filename
        if( fname is None ): fname = sets.file_sourcelist

        loaded = False

        # Load data from save file
        if( os.path.exists(fname) ):
            self._log.debug("Loading from '%s'" % (fname))
            retval = self.load(fname)
            if( retval ):
                self._log.debug(" - Loaded  v%s" % (str(self.version)))
                self._log.debug(" - Sources: %d" % (self.count))
                loaded = True
            else:
                errStr = "Load Failed!"
                self._log.error(errStr)
                raise RuntimeError(errStr)
        else:
            self._log.warning("File '%s' does not exist!" % (fname))


        # Create new
        if( not loaded ):

            # initialize values
            self._log.warning("Initializing new SourceList")
            self.new()
            # save
            self._log.info("Saving")
            retval = self.save(fname=fname)
            if( not retval ): self._log.error("Error, not saved!!")

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
        self._log.debug("new()")

        if( inter ):
            confirm = self._confirm_unsaved()
            if( not confirm ): return False

        # Metadata
        self.version = __version__
        self._savefile_list = []
        self.savefile = None
        self._saved = True
        self.count = 0

        # SourceList data
        self._sources_url = []
        self._sources_title = []
        self._sources_subtitle = []
        self.sources = []


        return True




    def load(self, fname, inter=True):
        """
        Load sources list from the given filename.

        Arguments
        ---------
            fname <str>  : filename to load from.
            inter <bool> : interactive, if so, prompt if unsaved changes.
        """

        self._log.debug("load()")

        ## Load raw Data
        #  -------------

        # Confirm lose unsaved changes
        if( inter ):
            confirm = self._confirm_unsaved()
            if( not confirm ): return False

        # Try to load file and extract elements
        try:
            self._log.debug("Loading from '%s'" % (fname))
            config = ConfigObj(fname)
            self.version = config[SOURCELIST_KEYS.VERS]
            self._savefile_list = config[SOURCELIST_KEYS.SAVE_LIST]
            self._sources_url = config[SOURCELIST_KEYS.SOURCES_URL]
            self._sources_title = config[SOURCELIST_KEYS.SOURCES_TITLE]
            self._sources_subtitle = config[SOURCELIST_KEYS.SOURCES_SUBTITLE]

            self.sources = []
            data = zip(self._sources_url, self._sources_title, self._sources_subtitle)
            for ii, (url, tit, sub) in enumerate(data):
                self.sources.append(Source(url, tit, sub))

        except:
            import sys
            self._log.error("Could not load!! {0:s} : {1:s}".format(*sys.exc_info()))
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
        Save ``SourceList`` state to file.

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

        self._log.debug("save()")

        retval = False

        # Use preset save filename if it exists
        if( fname is None ):
            if( self.savefile is not None ): fname = self.savefile
            else:
                self._log.error("``savefile`` is not set, ``fname`` must be provided!")
                return retval


        # Setup data using ``ConfigObj``
        self._log.debug("Creating ``ConfigObj``")
        config = ConfigObj()
        config.filename = fname
        config[SOURCELIST_KEYS.VERS] = self.version
        config[SOURCELIST_KEYS.SAVE_LIST] = self._savefile_list
        config[SOURCELIST_KEYS.SOURCES_URL] = self._sources_url
        config[SOURCELIST_KEYS.SOURCES_TITLE] = self._sources_title
        config[SOURCELIST_KEYS.SOURCES_SUBTITLE] = self._sources_subtitle


        # Make sure path exists, confirm overwrite in interactive mode
        zio.checkPath(fname)
        if( os.path.exists(fname) and inter ):
            conf = zio.promptYesNo("\tDestination '%s' already exists, overwrite?" % (fname))
            if( not conf ): return False

            # Create backup filename
            oldPath, oldName = os.path.split(fname)
            backname = os.path.join(oldPath, ".backup_" + oldName)
            # If backup already exists, delete
            if( os.path.exists(backname) ):
                self._log.info("Backup '%s' already exists.  Deleting." % (backname))
                os.remove(backname)

            # Move old file to backup
            self._log.info("Moving '%s' ==> '%s'" % (fname, backname))
            shutil.move(fname, backname)
            # Look for problems
            if( os.path.exists(fname) ):
                self._log.error("Old file '%s' still exists!" % (fname))
                return False

            if( not os.path.exists(backname) ):
                self._log.error("Backup '%s' does not exist!" % (backname))
                self._log.error("Lets hope the save works...")


        # Save data
        self._log.debug("Writing ``ConfigObj``")
        config.write()

        # Make sure its saved
        if( os.path.exists(fname) ):
            retval = True
            self._recount()
            self._log.info("Saved %d sources to '%s'" % (self.count, fname))
            self.savefile = fname
            self._saved = True
            if( not fname in self._savefile_list ):
                self._savefile_list.append(fname)

        else:
            self._log.error("Save to '%s' failed!" % (fname))
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
        self._log.debug("add()")

        # Make sure url(s) is(are) iterable
        if( isinstance(url, str) ): url = [ url ]
        # If no title/subtitle are provided, set to empty strings
        if( title is None ): title = ['']*np.size(url)
        if( subtitle is None ): subtitle = ['']*np.size(url)

        # Make sure all arrays are the same length
        if( not self._same_size(url, title, subtitle) ):
            self._log.error("values to add are not the same length!")
            return False

        # Iterate over and add all new entries
        retval = True
        for uu, tt, ss in zip(url, title, subtitle):
            # Check that url exists, skip if not
            if( check and not zio.checkURL(uu) ):
                self._log.warning("URL '%s' does not exist, skipping!" % (uu))
                retval = False
                continue

            self._sources_url.append(uu)
            self._sources_title.append(tt)
            self._sources_subtitle.append(ss)
            self.sources.append( Source(uu, tt, ss) )
            

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
        self._log.debug("delete()")

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
        del_src = []
        for id in reversed(index):
            del_url.append(self._sources_url.pop(id))
            del_tit.append(self._sources_title.pop(id))
            del_sub.append(self._sources_subtitle.pop(id))
            del_src.append(self.sources.pop(id))

        self._log.info("Deleted URLs:")
        for url in del_url:
            self._log.info(" - '%s'" % (url))

        self._recount()
        self._saved = False

        return True


    def _get(self, index=None):
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
        self._log.debug("_get()")

        ## Convert index to a slicing object
        import numbers
        # Single integer number
        if( isinstance(index, numbers.Integral) ): 
            ids = np.arange(index, index+1)
        # List of numbers
        elif( np.iterable(index) ): 
            ids = np.array(index)
        # Otherwise, return all sources
        else:
            if( index is not None ):
                self._log.error("Unrecognized `index` = '%s'!" % (str(index)))
                self._log.warning("Returning all entries")

            ids = np.arange(len(self._sources_url))


        ## Select target elements and return
        srcs = [ self.sources[ii] for ii in ids ]

        return ids, srcs



    def list(self, index=None):
        """
        List some or all sources to stdout.

        Arguments
        ---------
            index <obj> : int, list of ints, or `None` for all entries.

        """
        self._log.debug("list()")

        # Get entries and ID numbers
        ids, srcs = self._get(index=index)
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

        url = src.url
        tit = src.title
        sub = src.subtitle

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

        self._log.debug("_recount()")
        uselists = [ self._sources_url, self._sources_title, self._sources_subtitle, self.sources ]

        count = np.size(self._sources_url)
        if( self._same_size(*uselists) ): self._log.debug("All lists have length %d" % (count))
        else:
            self._log.error("Sources list lengths do not match!")
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




def main():
    """
    Run interactive mode where the user passes options via CLI to interact with ``SourceList``.

    Interactive options:
        [q]uit   : exit interactive mode
        [a]dd    : add a new sources entry
        [d]elete : delete an existing sources entry
        [l]ist   : list all current sources
        [f]ind   : find/search for a particular source
        [s]ave   : save the current sources to file
        [h]elp   : This help information

    """

    ## Initialization
    #  --------------
    sets = Settings.Settings()
    log = MyLogger.defaultLogger(_LOG_FILENAME, sets=sets)
    log.info("main()")
    log.debug("version = '%s'" % str(__version__))
    log.debug("Settings version = '%s'" % (str(sets.version)))

    # Command-Line Arguments
    log.debug("Getting command line arguments")
    parser = Settings.getParser(sets)
    args, sets = Settings.getArgs(parser, sets)

    # Load SourceList
    log.info("Loading SourceList")
    sourceList = SourceList(log=log, sets=sets)


    ## Interactive Routine
    #  -------------------
    prompt = "\n\tAction?  [q]uit, [a]dd, [d]elete, [l]ist, [f]ind, [s]ave, [h]elp : "
    while( True ):
        arg = raw_input(prompt)
        arg = arg.strip().lower()
        log.debug("arg = '%s'" % (arg))
        if(   arg.startswith('q') ):
            log.debug("Quitting interactive")
            break
        elif( arg.startswith('a') ):
            _inter_add(sourceList, log)
        elif( arg.startswith('d') ):
            _inter_del(sourceList, log)
        elif( arg.startswith('l') ):
            sourceList.list()
        elif( arg.startswith('f') ):
            _inter_find(sourceList, log)
        elif( arg.startswith('s') ):
            _inter_save(sourceList, sets, log)
        elif( arg.startswith('h') ):
            print '\n', main.__doc__
        else:
            log.warning("Argument '%s' not understood!" % (arg))
            continue


    log.debug("Done.\n")

    return

# } main()



def _inter_add(sourceList, log):
    """
    Interactively add a new ``SourceList`` entry.

    Prompts user for {url, title, subtitle}.

    Arguments
    ---------
        sourceList <obj> : ``SourceList`` object instance
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
    retval = sourceList.add(url, title=titl, subtitle=subt, check=True)
    if( retval ): log.info("Added entry for '%s'" % (url))
    else: log.error("Could not add entry for '%s'!" % (url))

    return

# } _inter_add()


def _inter_del(sourceList, log):
    """
    Interactively delete a ``SourceList`` entry.
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

    retval = sourceList.delete(index, inter=True)
    if( retval ): log.info("Deleted entry '%d'" % (index))
    else: log.error("Could not delete entry '%d'!" % (index))

    return

# } _inter_del()


def _inter_find(sourceList, log):
    log.debug("_inter_find()")

    return

# } _inter_find()


def _inter_save(sourceList, sets, log):
    """
    Save current sources list to file.
    """
    log.debug("_inter_save()")

    log.info("Settings filename: '%s'" % (sets.file_sourcelist))
    log.info("``sourceList.savefile``: '%s'" % (sourceList.savefile))

    # Set default save filename
    savename = sourceList.savefile
    if( savename is None ): savename = sets.file_sourcelist

    # Prompt for filename
    args = raw_input("\tEnter save filename [default '%s'] : " % (savename)).strip()
    if( len(args) > 0 ): savename = args

    retval = sourceList.save(fname=savename, inter=True)
    if( retval ): log.info("Saved to '%s'" % (savename))
    else: log.error("Could not save to '%s'!" % (savename))

    return

# } _inter_save()



if( __name__ == "__main__" ): main()
