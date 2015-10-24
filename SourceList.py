"""

Notes
-----
    - Updating / Changing SourceList save files
      - - - - - - - - - - - - - - - - - - - - -
        + Make class of old `KEYS` (e.g. ``_KEYS__V0_1``)
        + Create method to convert to newest version (e.g. ``_V0_1__to__V0_2``)
        + Update ``SourceList``'s ``load``, ``save``, and ``new`` methods for changes.
            - Note that ``load`` might have to makeup some differences...
        + Update ``__version__`` number.

Objects
-------
    SOURCELIST_KEYS
    SourceList

Functions
---------
    main         : Run interactive mode where the user passes options via CLI.
    _inter_add   : Interactively add a new ``SourceList`` entry.
    _inter_del   : Interactively delete a ``SourceList`` entry.
    _inter_find  :
    _inter_save  : Save current ``SourceList`` to file.

To-Do
-----
    1) Add ``info`` interactive option (and associated function) to print summary info,
       including version, number of sources, etc.
    2) Create save files for Source data.
    3) Remove redundancy in ``SourceList`` data --- i.e. the '_src_*' arrays.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
from configobj import ConfigObj
import numpy as np

import zcode.inout as zio

import MyLogger
import Settings
import Source

_LOG_FILENAME = 'sources.log'


class SOURCELIST_KEYS(object):
    VERS = 'version'
    SAVE_LIST = 'savefile_list'
    URLS = 'sources_urls'
    NAMES = 'sources_names'
    SUBNAMES = 'sources_subnames'
    FILENAMES = 'sources_filenames'
    UPDATED = 'sources_updated'


class SourceList(object):
    """

    Notes
    -----


    Functions
    ---------
        new      : Initialize a new (or clear existing) state.
        load     : Load sources list from the given filename.
        save     : Save ``SourceList`` state to file.
        add      : Add one or multiple entries to sources.
        delete   : Remove one or multiple entries from sources.
        list     : List some or all sources to stdout.
        getFeeds : Tell earch ``Source`` object to get its RSS feed.

        _get             : Retrieve one or multiple sources from list (default: return all).
        _checkVersion    : Make sure the loaded version is up-to-date.  Prompt to update.
        _backupFile      : Create a backup of the given file.
        _str_src         : Create a string representation of a single source.
        _confirm_unsaved : If there is unsaved data, Prompt user (via CLI) to confirm overwrite.
        _recount         : Count the current number of sources and assure all lists match in length.
        _same_size       : Check whether all of the given arrays or lists are the same size.
        _clearSourceList : Reset source lists to empty.
        _updateSave      : Based on the version of old save data, delegate conversion to new style.
        _V0_1__to__V0_2  : Convert from save data v0.1 to v0.2.

    """

    def __init__(self, fname=None, log=None, sets=None):
        """

        """
        # Load settings (singleton)
        if(sets is None): sets = Settings.Settings()
        self._log = MyLogger.defaultLogger(_LOG_FILENAME, log, sets)
        # Set default filename
        if(fname is None): fname = sets.file_sourcelist

        loaded = False

        # Load data from save file
        if(os.path.exists(fname)):
            self._log.debug("Loading from '%s'" % (fname))
            retval = self.load(fname)
            if(retval):
                self._log.debug(" - Loaded  v%s" % (str(self.version)))
                self._log.debug(" - Sources: %d" % (self.count))
                loaded = True
            else:
                self._log.error("Load Failed!")

        else:
            self._log.warning("File '%s' does not exist!" % (fname))

        # Create new
        if(not loaded):

            # initialize values
            self._log.warning("Initializing new SourceList")
            self.new()
            # save
            self._log.info("Saving")
            retval = self.save(fname=fname)
            if(not retval): self._log.error("Error, not saved!!")

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

        if(inter):
            confirm = self._confirm_unsaved()
            if(not confirm): return False

        # Metadata
        self.version = Settings.__version__
        self._savefile_list = []
        self.savefile = None
        self._saved = True
        self.count = 0

        # SourceList data
        self._clearSourceLists()
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

        # Load raw Data
        # -------------

        # Confirm lose unsaved changes
        if(inter):
            # Checks if there are unsaved changes, if so, prompts user
            confirm = self._confirm_unsaved()
            if(not confirm): return False

        # Load file as ``ConfigObj``
        self._log.info("Loading ``SourceList`` from '%s'" % (fname))
        config = ConfigObj(fname)

        # Check version, update if needed
        config = self._checkVersion(config, fname, inter)
        if(config is None):
            self._log.error("Version check on '%s' failed!" % (fname))
            return False

        # Load Raw Data from save file
        self.version = config[SOURCELIST_KEYS.VERS]
        self._savefile_list = config[SOURCELIST_KEYS.SAVE_LIST]
        self._src_urls = config[SOURCELIST_KEYS.URLS]
        self._src_names = config[SOURCELIST_KEYS.NAMES]
        self._src_subnames = config[SOURCELIST_KEYS.SUBNAMES]

        numSrcs = len(self._src_urls)
        filenames = config[SOURCELIST_KEYS.FILENAMES]
        if(len(filenames) == numSrcs): self._src_filenames = filenames
        else:                          self._src_filenames = ['']*numSrcs
        updated = config[SOURCELIST_KEYS.UPDATED]
        if(len(updated) == numSrcs): self._src_updated = updated
        else:                        self._src_updated = [None]*numSrcs

        # Construct list of ``Source``s from raw data
        self.sources = []
        for ii in range(numSrcs):
            url = self._src_urls[ii]
            nam = self._src_names[ii]
            sub = self._src_subnames[ii]
            fil = self._src_filenames[ii]
            upd = self._src_updated[ii]

            src = Source.Source(url, nam, sub, fil, upd)
            self.sources.append(src)

        # Set metadata
        self.savefile = fname
        self._recount()
        self._saved = True

        return True

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
        if(fname is None):
            if(self.savefile is not None): fname = self.savefile
            else:
                self._log.error("``savefile`` is not set, ``fname`` must be provided!")
                return retval

        # Update internal parameters based on list of sources
        self._clearSourceLists()
        for src in self.sources:
            self._src_urls.append(src.url)
            self._src_names.append(src.name)
            self._src_subnames.append(src.subname)
            self._src_filenames.append(src.filename)
            self._src_updated.append(src.updated)

        # Setup data using ``ConfigObj``
        self._log.debug("Creating ``ConfigObj``")
        config = ConfigObj()
        config.filename = fname
        config[SOURCELIST_KEYS.VERS] = self.version
        config[SOURCELIST_KEYS.SAVE_LIST] = self._savefile_list
        config[SOURCELIST_KEYS.URLS] = self._src_urls
        config[SOURCELIST_KEYS.NAMES] = self._src_names
        config[SOURCELIST_KEYS.SUBNAMES] = self._src_subnames
        config[SOURCELIST_KEYS.FILENAMES] = self._src_filenames
        config[SOURCELIST_KEYS.UPDATED] = self._src_updated

        # Make sure path exists, confirm overwrite in interactive mode
        zio.checkPath(fname)
        if(os.path.exists(fname) and inter):
            conf = zio.promptYesNo("\tDestination '%s' already exists, overwrite?" % (fname))
            if(not conf): return False

            # Create backup
            backname = self._backupFile(fname)
            if(backname is None):
                self._log.error("Backup of '%s' failed!" % (fname))
                return False

        # Save data
        self._log.debug("Writing ``ConfigObj``")
        config.write()

        # Make sure its saved
        if(os.path.exists(fname)):
            retval = True
            self._recount()
            self._log.info("Saved %d sources to '%s'" % (self.count, fname))
            self.savefile = fname
            self._saved = True
            if(fname not in self._savefile_list):
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
        if(isinstance(url, str)): url = [url]
        # If no title/subtitle are provided, set to empty strings
        if(title is None): title = ['']*np.size(url)
        if(subtitle is None): subtitle = ['']*np.size(url)

        # Make sure all arrays are the same length
        if(not self._same_size(url, title, subtitle)):
            self._log.error("values to add are not the same length!")
            return False

        # Iterate over and add all new entries
        retval = True
        for uu, tt, ss in zip(url, title, subtitle):
            # Check that url exists, skip if not
            if(check and not zio.checkURL(uu)):
                self._log.warning("URL '%s' does not exist, skipping!" % (uu))
                retval = False
                continue

            self.sources.append(Source(uu, tt, ss))

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

        # If interactive, show sources and confirm deletion
        if(inter):
            print("Delete the following sources: ")
            self.list(index)
            conf = zio.promptYesNo('Are you sure?')
            if(not conf): return False

        # Make sure indices are iterable
        if(not np.iterable(index)): index = [index]

        # Iterate over IDs and delete
        #     MUST REVERSE ITERATE so that index numbers are preserved for subsequent entries.
        del_src = []
        for id in reversed(index):
            del_src.append(self.sources.pop(id))

        # Report deleted urls
        self._log.info("Deleted URLs:")
        for src in del_src:
            self._log.info(" - '%s'" % (src.url))

        # Update metadata
        self._recount()
        self._saved = False

        return True

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
        for id, src in zip(ids, srcs):
            print("\t", self._str_src(id, src))

        return

    def getFeeds(self):
        """
        Tell earch ``Source`` object to get its RSS feed.
        """
        self._log.debug("getFeeds()")
        numValid = 0
        for src in self.sources:
            if(src.getFeed()): numValid += 1

        return

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

        # Convert index to a slicing object
        import numbers
        # Single integer number
        if(isinstance(index, numbers.Integral)):
            ids = np.arange(index, index+1)
        # List of numbers
        elif(np.iterable(index)):
            ids = np.array(index)
        # Otherwise, return all sources
        else:
            if(index is not None):
                self._log.error("Unrecognized `index` = '%s'!" % (str(index)))
                self._log.warning("Returning all entries")

            ids = np.arange(len(self._src_urls))

        # Select target elements and return
        srcs = [self.sources[ii] for ii in ids]

        return ids, srcs

    def _checkVersion(self, config, fname, inter):
        """
        Make sure the loaded version is up-to-date.  If not, prompt to update, or return ``None``.

        If the file is not up-to-date, it is updated.  A backup file is created by appending the
        old version number to the previous filename (``fname``; e.g. './data/sources_v0.1.conf').

        Arguments
        ---------
            config <obj>  : config data dictionary loaded from save file
            fname  <str>  : filename from which data was loaded
            inter  <bool> : interactive session, if so prompts to update out of date data.

        Returns
        -------
            retval <obj> : ``config`` dictionary on success, ``None`` on failure

        """

        self._log.debug("_checkVersion()")

        vers = config[SOURCELIST_KEYS.VERS]
        # If version is up-to-date, return config object
        if(vers == Settings.__version__):
            self._log.debug("Version is uptodate at v'%s'" % (Settings.__version__))
            return config

        # Prompt to update file
        msg = "File '{}' version is v'{}' not current v'{}'"
        msg = msg.format(fname, vers, Settings.__version__)
        estr = msg + ", cannot load!"
        # If not interactive, return ``None``
        if(not inter):
            self._log.warning(msg)
            self._log.warning("Updating to new version!")
        # If interactive, prompt user to update file
        else:
            msg += "; update to load?"
            conf = zio.promptYesNo("\t" + msg, default='y')
            if(not conf):
                self._log.error(estr)
                return None

        # Update file
        #  -----------

        # Create a backup of the file, and delete original
        self._log.debug("Creating backup")
        backname = self._backupFile(fname, True, prepend='', append='_v%s' % (vers))
        if(backname is None):
            self._log.debug("Backup failed!")
            return None
        else:
            self._log.debug("Backed up to '%s'" % (backname))

        # Convert old, loaded dictionary to new, updated one
        self._log.debug("Updating save data")
        config = self._updateSave(config)

        # Save new version
        vers = config[SOURCELIST_KEYS.VERS]
        self._log.info("Saving new version v'%s' to '%s'" % (vers, fname))
        config.write()
        if(not os.path.exists(fname)):
            self._log.error("Filename '%s' does not exist!  Save failed!!" % (fname))
            return None

        return config

    def _backupFile(self, fname, delold, append='', prepend='.back_'):
        """
        Create a backup of the given file.

        Arguments
        ---------
            fname <str>   : filename to backup
            delold <bool> : delete the original file after backup

        Returns
        -------
            retval <obj> : backup filename ``backname`` on success, ``None`` on failure.

        """

        self._log.debug("_backupFile()")

        # Create backup filename
        backname = zio.modifyFilename(fname, append=append, prepend=prepend)

        # If backup already exists, delete
        if(os.path.exists(backname)):
            self._log.info("Backup '%s' already exists.  Deleting." % (backname))
            os.remove(backname)

        # Move old file to backup
        self._log.info("Copying '%s' ==> '%s'" % (fname, backname))
        shutil.copy2(fname, backname)

        # Make sure backup created
        if(not os.path.exists(backname)):
            self._log.error("Backup '%s' does not exist!" % (backname))
            return None

        # Delete old file if desired
        if(delold):
            self._log.info("Deleting '%s'" % (fname))
            os.remove(fname)

        return backname

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
        tit = src.name
        sub = src.subname

        tstr = tit
        if(len(sub) > 0): tstr += " - " + sub

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
        if(hasattr(self, '_saved')):
            if(not self._saved):
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
        uselists = [self._src_urls, self._src_names, self._src_subnames, self.sources]

        count = np.size(self._src_urls)
        if(self._same_size(*uselists)): self._log.debug("All lists have length %d" % (count))
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
        counts = [np.size(ar) for ar in arrs]
        if(len(set(counts)) == 1): return True
        return False

    def _clearSourceLists(self):
        """
        Reset source lists to empty.
        """
        self._src_urls = []
        self._src_names = []
        self._src_subnames = []
        self._src_filenames = []
        self._src_updated = []
        return

    def _updateSave(self, old):
        """
        Based on the version of old dictionary save data, delegate conversion to new style.
        """
        self._log.debug("_updateSave()")
        vers = old[SOURCELIST_KEYS.VERS]

        if(vers.startswith('0.1')):
            new = self._V0_1__to__V0_2(old)

        else:
            estr = "Unknown version v'%s'!" % (vers)
            self._log.error(estr)
            return None

        return new

    def _V0_1__to__V0_2(self, old):
        """
        Convert from save data v0.1 to v0.2.
        """
        self._log.debug("_V0_1__to__V0_2()")
        new = ConfigObj()
        new.filename = old.filename
        new[SOURCELIST_KEYS.VERS] = '0.1.1'
        new[SOURCELIST_KEYS.URLS] = old[_KEYS__V0_1.SOURCES_URL]
        new[SOURCELIST_KEYS.NAMES] = old[_KEYS__V0_1.SOURCES_TITLE]
        new[SOURCELIST_KEYS.SUBNAMES] = old[_KEYS__V0_1.SOURCES_SUBTITLE]
        new[SOURCELIST_KEYS.SAVE_LIST] = old[_KEYS__V0_1.SAVE_LIST]
        new[SOURCELIST_KEYS.FILENAMES] = []
        new[SOURCELIST_KEYS.UPDATED] = []

        return new


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

    # Initialization
    # --------------
    sets = Settings.Settings()
    log = MyLogger.defaultLogger(_LOG_FILENAME, sets=sets)
    log.info("main()")
    log.debug("version = '%s'" % str(Settings.__version__))

    # Command-Line Arguments
    log.debug("Getting command line arguments")
    parser = Settings.getParser(sets)
    args, sets = Settings.getArgs(parser, sets)

    # Load SourceList
    log.info("Loading SourceList")
    sourceList = SourceList(log=log, sets=sets)

    # Interactive Routine
    # -------------------
    prompt = "\n\tAction?  [q]uit, [a]dd, [d]elete, [l]ist, [f]ind, [s]ave, [h]elp : "
    while(True):
        arg = input(prompt)
        arg = arg.strip().lower()
        print("")
        log.debug("arg = '%s'" % (arg))
        if(arg.startswith('q')):
            log.debug("Quitting interactive")
            break
        elif(arg.startswith('a')):
            _inter_add(sourceList, log)
        elif(arg.startswith('d')):
            _inter_del(sourceList, log)
        elif(arg.startswith('l')):
            sourceList.list()
        elif(arg.startswith('f')):
            _inter_find(sourceList, log)
        elif(arg.startswith('s')):
            _inter_save(sourceList, sets, log)
        elif(arg.startswith('h')):
            print('\n', main.__doc__)
        else:
            log.warning("Argument '%s' not understood!" % (arg))
            continue

    log.debug("Done.\n")

    return


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
    while(True):
        url = input("\tURL (e.g. '%s') : " % (example))
        url = url.strip()
        # Catch 'q'uit request
        if(url == 'q'):
            log.debug("Break '%s'" % (url))
            return

    # Title
    titl = input("\tTitle (e.g. 'NewYork Times'): ")
    titl = titl.strip()

    # Subtitle
    subt = input("\tSubtitle : (e.g. 'HomePage') : ")
    subt = subt.strip()

    # Add New Source
    retval = sourceList.add(url, title=titl, subtitle=subt, check=True)
    if(retval): log.info("Added entry for '%s'" % (url))
    else: log.error("Could not add entry for '%s'!" % (url))

    return


def _inter_del(sourceList, log):
    """
    Interactively delete a ``SourceList`` entry.
    """
    log.debug("_inter_del()")

    index = input("\tIndex number: ").strip().lower()
    if(index.startswith('q')):
        log.debug("Break")
        return

    try:
        index = np.int(index)
    except:
        log.error("Could not convert '%s' to integer" % (index))
        return

    retval = sourceList.delete(index, inter=True)
    if(retval): log.info("Deleted entry '%d'" % (index))
    else: log.error("Could not delete entry '%d'!" % (index))

    return


def _inter_find(sourceList, log):
    log.debug("_inter_find()")

    return


def _inter_save(sourceList, sets, log):
    """
    Save current sources list to file.
    """
    log.debug("_inter_save()")

    log.info("Settings filename: '%s'" % (sets.file_sourcelist))
    log.info("``sourceList.savefile``: '%s'" % (sourceList.savefile))

    # Set default save filename
    savename = sourceList.savefile
    if(savename is None): savename = sets.file_sourcelist

    # Prompt for filename
    args = input("\tEnter save filename [default '%s'] : " % (savename)).strip()
    if(len(args) > 0): savename = args

    retval = sourceList.save(fname=savename, inter=True)
    if(retval): log.info("Saved to '%s'" % (savename))
    else: log.error("Could not save to '%s'!" % (savename))

    return


class _KEYS__V0_1(object):
    VERS = 'version'
    SAVE_LIST = 'savefile_list'
    SOURCES_URL = 'sources_url'
    SOURCES_TITLE = 'sources_title'
    SOURCES_SUBTITLE = 'sources_subtitle'


if(__name__ == "__main__"): main()
