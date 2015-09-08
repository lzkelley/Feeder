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
    URL = 'url'
    TIT = 'title'
    SUB = 'subtitle'
# } class SRC_COL


class KEYS_SAVE(object):
    DATA = 'data'
    VERS = 'version'
    DTCR = 'datetime_created'
    DTSV = 'datetime_saved'
    SVLS = 'savefile_list'

# } class KEYS_SAVE


SOURCES_COLUMNS = [ SRC.URL, SRC.TIT, SRC.SUB ]

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
        log = _getLogger(log, sets)

        if( fname is None and sets is not None ):
            fname = sets.file_src

        ## Load data from save file
        #  ------------------------
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

        ## Initialize empty
        #  ----------------
        else:
            log.debug("Initializing new Sources DataFrame")
            self.data = pandas.DataFrame(columns=SOURCES_COLUMNS)
            self.version = __version__
            self.datetime_created = str(datetime.now())
            self.datetime_saved = None
            self.savefile_list = []
            self.savefile = None
            log.debug("Created")

        return

    # } __init__()


    def load(self, fname, log):
        """
        """

        log.debug("load()")

        ## Try to load file and convert to DataFrame
        #  -----------------------------------------
        try:
            log.debug("Loading from '%s'" % (fname))
            loadFile = open(fname, 'r')
            loadData = json.load(loadFile)
            self.data = pandas.DataFrame.from_dict(loadData[KEYS_SAVE.DATA])
        except:
            import sys
            log.warning("Could not load!! {0:s} : {1:s}".format(*sys.exc_info()))
            retval = False

        ## Store Data on Success
        #  ---------------------
        else:
            # Reindex converting to integer type
            self.clean(log)
            self.version = loadData[KEYS_SAVE.VERS]
            self.datetime_created = loadData[KEYS_SAVE.DTCR]
            self.datetime_saved = loadData[KEYS_SAVE.DTSV]
            self.savefile_list = loadData[KEYS_SAVE.SVLS]
            self.savefile = fname
            retval = True


        return retval

    # } load()


    def save(self, log, fname=None):
        """
        """

        retval = False

        if( fname is None ):
            if( self.savefile is not None ): fname = self.savefile
            else:
                log.error("``savefile`` is not set, ``fname`` must be provided!")
                return retval


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

        if( os.path.exists(fname) ):
            retval = True

            log.info("Saved to '%s'" % (fname))
            if( not fname in self.savefile_list ):
                self.savefile_list.append(fname)

        return retval

    # } save()


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


    def add(self, url, title='', subtitle=''):
        """
        Add an entry to the sources DataFrame.
        """
        temp = pandas.DataFrame({SRC.URL:[url],
                                 SRC.TIT:[title],
                                 SRC.SUB:[subtitle]})
        self.data = self.data.append(temp, ignore_index=True)
        return
    # } add()


    def delete(self, index, interactive=False):
        """
        Remove an entry from the sources DataFrame.
        """

        if( interactive ):

            resp = raw_input

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


    def list(self, log):
        """
        List all sources in DataFrame.
        """
        log.debug("list()")

        for id,src in self.data.sort().iterrows():
            print self._str_row(id, src=src)

        return
    # } list()

    def _str_row(self, index, src=None):
        """
        """
        if( src is None ):
            if( index is not None ):
                src = self.data.xs(index)
            else:
                raise RuntimeError("Either ``index`` or ``src`` must be provided!")

        tstr = src[SRC.TIT]
        if( isinstance(src[SRC.SUB], str) ):
            if( len(src[SRC.SUB]) > 0 ): tstr += " - " + src[SRC.SUB]

        pstr = "{0:>4d} : {1:{twid}.{twid}}   {2:{uwid}.{uwid}s}"
        pstr = pstr.format(index, tstr, src[SRC.URL], twid=40, uwid=60)

        return pstr

    # } _str_row()


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
