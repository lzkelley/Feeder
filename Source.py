"""

Objects
-------
    Article
    Source


Methods
-------
    ent_to_dict : 
    dict_to_ent : 


"""

from __future__ import unicode_literals

import feedparser, time, json, os
from bs4 import BeautifulSoup
import numpy as np

import MyLogger, Settings


class Article(object):
    
    def __init__(self, ent):
        self._ent = ent
        self.valid = False

        self.time = None
        self.time_updated = None
        self.time_published = None
        self.time_updated_str = ''
        self.time_published_str = ''
        self.time_str = ''

        try:
            self.title = ent['title']
            self.link = ent['link']
            self.summary = BeautifulSoup(ent['summary']).text

            if( ent.has_key('updated_parsed') ): self.time_updated = ent['updated_parsed']
            if( ent.has_key('published_parsed') ): self.time_published = ent['published_parsed']

        except:
            self.title = None
            self.link = None
            self.summary = None
            return


        if( self.time_updated is not None ): 
            self.time_updated_str = time.asctime(self.time_updated)

        if( self.time_published is not None ): 
            self.time_published_str = time.asctime(self.time_published)

        if( self.time_updated is not None ): self.time = self.time_updated
        elif( self.time_published is not None ): self.time = self.time_published

        if( self.time is not None ): self.time_str = time.asctime(self.time)

        self.valid = True
        return


    def str(self):
        """
        Note: DO NOT OVERRIDE `__str__` returning unicode!
        """
        myStr = u"{0:{w0}.{w0}} - {1:{w1}.{w1}}"
        myStr = myStr.format(self.title, self.time_str, 
                             w0=Settings.STR_TITLE_LEN, w1=Settings.STR_TIME_LEN)
        return myStr


    def _hasGet(self, ent, key):
        if( hasattr(ent, key) ): return getattr(ent, key)
        else: return None




class Source(object):
    """
    Store data for individual feed source, and manage loading and storing feed articles.

    Methods
    -------
        str          : Construct a string description of this object using its title and time.
        getFeed      : Load the RSS feed from stored url.
        _strTimes    : Store string representations of different time attributes.
        _mostRecent  : Find time of the most recent article.
        _hasGet      : Check for attribute, retrieve if possible (otherwise ``None``).
        _getFilename : Construct a viable filename for this ``Source``.

    """


    def __init__(self, url, name='', subname='', filename='', filetime=None):
        ## Parameters Loaded from SourceList files
        self.url = url
        self.name = name
        self.subname = subname

        ## Set filename, construct if needed
        if( len(filename) > 0 ): self._filename = filename
        else:                    self._filename = self._getFilename()
        self.file_time = filetime

        self.valid = False
        self.articles = []
        self.count = 0
        self.status = -1
        self.title = u''

        self.time = None
        self.feed_time = None
        self.article_time = None
        self.time_str = ''
        self.feed_time_str = ''
        self.article_time_str = ''
        self.file_time_str = ''

        return
      

    
    def str(self):
        """
        Construct a string description of this object using its title and time.

        Note: DO NOT OVERRIDE `__str__` returning unicode!
        """
        myStr = u"{0} - {1}"
        myStr = myStr.format(self.title, self.time_str)
        return myStr


    def getFeed(self):
        """
        Load the RSS feed from this ``Source``'s stored url.

        Uses ``feedparser`` to parse the RSS feed, converting a list of 'entries' into a list of
        ``Article`` objects stored to the ``.articles`` variable.  Time information is updated
        based on the metadata given in the RSS feed, and the timestamps of the articles themselves.

        Returns
        -------
            retval <bool> : `True` on success, `False` otherwise

        """
        
        # Get Parsed Feed
        feed = feedparser.parse(self.url)
        self._feed = feed
        self.status = feed.status

        # Check if source feed seems valid
        self.valid = False # Make sure this is False by default
        if( self.status != 200 or not hasattr(feed, 'feed') or not hasattr(feed.feed, 'title') ): 
            return False

        # Set basic parameters (if available)
        self.title = feed.feed.title
        #     Look for something describing time this feed was updated
        self.feed_time = self._hasGet(feed, 'updated_parsed')
        if( self.feed_time is None ): self.feed_time = self._hasGet(feed, 'published_parsed')

        # Look for 'entries', use them to create ``Articles``
        if( hasattr(feed, 'entries') ):
            for ent in feed.entries:
                art = Article(ent)
                if( art.valid ): self.articles.append(art)

            self.count = len(self.articles)

        # If no valid articls found, return False
        if( self.count == 0 ): return False

        # Find most recent time from articles
        self.article_time = self._mostRecent()

        # Set ``.time`` as the most reliable measure of updated time
        if( self.feed_time is not None ): self.time = self.feed_time
        else:                             self.time = self.article_time

        # Update string times
        self._strTimes()

        self.valid = True
        return True



    def loadArticles(self, fname=None):
        """
        """

        print "\nLOAD"

        if( fname is None ): fname = self._filename

        if( not os.path.exists(fname) ): 
            estr = "ERROR: file '%s' does not exist!" % (fname)
            print estr
            return []

        try:
            data = json.load( open(fname, 'r') )
            print "Loaded data from '%s'" % (fname)
        except:
            estr = "ERROR: could not load json from '%s'" % (fname)
            print estr
            return []

        ents = [ dict_to_ent(dic) for dic in data ]
        arts = [ Article(ee) for ee in ents ]
        print "Loaded %d articles" % (len(arts))

        return arts



    def saveArticles(self, fname=None):
        """
        """

        print "\nSAVE"

        if( fname is None ): fname = self._filename

        print "Filename = ", fname
        
        if( len(fname) == 0 ):
            estr = "Error: invalid filename '%s'" % (fname)
            print estr
            return False

        
        arts = []
        if( os.path.exists(fname) ):
            print "Path '%s' exists" % (fname)
            arts += self.loadArticles(fname)
            print "\tLoaded %d articles" % (len(arts))

        else:
            print "Path '%s' does not exist" % (fname)
        

        titles = [ aa.title for aa in arts ]
        newArts = 0
        for aa in self.articles:
            if( aa.title not in titles ): 
                arts.append(aa)
                newArts += 1

        print "Adding %d new articles" % (newArts)

        ## Convert articles to string dictionaries
        print "Converting entries to dictionaries"
        data = [ ent_to_dict(aa._ent) for aa in arts ]
        
        print "Saving to '%s'" % (fname)
        json.dump(data, open(fname, 'w'))

        if( not os.path.exists(fname) ):
            estr = "ERROR: did not save to '%s'" % (fname)
            print estr
            return False


        print "Saved"
        self.saved = True

        return True


    
    def _strTimes(self):
        """
        Store string representations of different time attributes.
        """
        self.time_str = time.asctime(self.time)
        if( self.feed_time is not None ): self.feed_time_str = time.asctime(self.feed_time)
        if( self.article_time is not None ): self.article_time_str = time.asctime(self.article_time)
        if( self.file_time is not None ): self.file_time_str = time.asctime(self.file_time)
        return


    def _mostRecent(self):
        """
        Find time of the most recent article.
        """
        times = [ art.time for art in self.articles if art.time is not None ]
        if( len(times) == 0 ):
            print "WARNING: NO TIMES!  %s" % (self.url)
        elif( len(times) == 1 ):
            return times[0]
        else:

            recent = times[0]
            for tt in times[1:]:
                if( tt > recent ): recent = tt

        return recent


    def _hasGet(self, feed, key):
        """
        Check for attribute ``key`` in given feed or feed.feed.  Return ``None`` if neither.
        """

        if( hasattr(feed, key) ):
            return getattr(feed, key)
        elif( hasattr(feed.feed, key) ):
            return getattr(feed.feed, key)

        return None
    

    def _getFilename(self):
        """
        Construct a viable filename for this ``Source``.

        Notes:
            `name`_`subname`[__`url`]
            If the combination of ``name`` and ``subname`` are not long enough (compared to 
            ``Settings.FILENAME_MIN_LEN``), then a trimmed version of the URL is appended.
            The only preserved characters are alpha-numeric and underscore ('_').

        Returns
        -------
            retval <str> : filename

        """

        # Construct candidate filename from ``name`` and ``subname``
        fname = self.name.strip() + '_' + self.subname.strip()
        # If candidate is not long enough, append cleaned-``url`` string
        if( len(fname) <= Settings.FILENAME_MIN_LEN ): 
            urlStr = self.url.strip().replace('http://','').replace('www.','').split('/')[0]
            fname += '__' + urlStr

        # Remove everything but underscore ('_') and alphanumeric characters
        fname = ''.join(ch for ch in fname if (ch.isalnum() or ch == '_') )

        fname = Settings.Settings().dir_data + fname + Settings.SOURCE_FILE_TYPE

        return fname



def ent_to_dict(ent):
    """
    """

    # Copy data to new dictionary
    dic = dict(ent)

    # Convert ``struct_time`` objects to strings
    for key in dic.keys():
        if( key.endswith('_parsed') ):
            struct_time = dic[key]
            strTime = "{:.3f}".format(time.mktime( dic[key] ))
            dic[key] = strTime

    
    return dic



def dict_to_ent(dic):
    """
    """

    # Copy data to new dictionary
    ent = dict(dic)

    # String times to ``struct_time``
    for key in ent.keys():
        if( key.endswith('_parsed') ):
            fltTime = np.float(ent[key])
            struct_time = time.localtime(fltTime)
            ent[key] = struct_time

    return ent
    
