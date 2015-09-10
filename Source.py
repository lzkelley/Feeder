"""

"""

import feedparser, time
from bs4 import BeautifulSoup
import numpy as np

import MyLogger, Settings

#TITLE_WIDTH = 140



class Article(object):
    
    def __init__(self, ent):
        self._ent = ent
        self.valid = False

        try:
            self.published = ent.published_parsed
            self.title = ent.title
            self.link = ent.link
            self.updated = ent.updated_parsed
            self.summary = BeautifulSoup(ent.summary).text
        except:
            self.published = None
            self.title = None
            self.link = None
            self.updated = None
            self.summary = None
            return

        self.valid = True
        return

    def _hasGet(self, ent, key):
        if( hasattr(ent, key) ): return getattr(ent, key)
        else: return None




class Source(object):

    def __init__(self, url, name='', subname=''):
        self.url = url.lower()
        self.name = name
        self.subname = subname

        self.valid = False
        self.articles = []
        self.count = 0
        self.status = -1

        self.time = None
        self.feed_time = None
        self.article_time = None

        self.time_str = ''
        self.feed_time_str = ''
        self.article_time_str = ''

        return

    
    def __str__(self):
        return self.name + " " + self.subname


    def getFeed(self):
        """
        """
        
        feed = feedparser.parse(self.url)
        self._feed = feed
        self.status = feed.status

        if( self.status != 200 or not hasattr(feed, 'feed') ): 
            return self.valid

        if( not hasattr(feed.feed, 'title') ):
            return self.valid

        self.title = feed.feed.title

        self.feed_time = self._hasGet(feed, 'updated_parsed')
        if( self.feed_time is None ): self.feed_time = self._hasGet(feed, 'published_parsed')

        if( hasattr(feed, 'entries') ):
            for ent in feed.entries:
                art = Article(ent)
                if( art.valid ): self.articles.append(art)

            self.count = len(self.articles)

        if( self.count == 0 ): return self.valid

        self.article_time = self._mostRecent()

        if( self.feed_time is not None ):
            self.time = self.feed_time
        else:
            self.time = self.article_time


        self.time_str = time.asctime(self.time)
        if( self.feed_time is not None ): self.feed_time_str = time.asctime(self.feed_time)
        if( self.article_time is not None ): self.article_time_str = time.asctime(self.article_time)

        print "\n", str(self)
        print "Time         = ", self.time_str
        print "Feed Time    = ", self.feed_time_str
        print "Article Time = ", self.article_time_str

        self.valid = True
        return self.valid


    def _mostRecent(self):
        """
        Find time of most recent article.
        """
        times = [ art.updated for art in self.articles ]
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
    

    

'''
def stringTitles(entries, times=False, width=TITLE_WIDTH):
    titles = [ ent.title.encode('utf-8') for ent in entries ]
    titles = [ ent.title for ent in entries ]

    strings = []

    if( times ):
        times = [ ent.published_parsed for ent in entries ]
        times = _formatDatetime(times, date=True, time=True)
        for tit,tim in zip(titles,times):
            strings.append(u"{:<{wid}.{wid}s}   {:21.21s}".format(tit,tim,wid=width))

    else:
        
        for tit in titles:
            strings.append(u"{:>140.140s}".format(tit))


    return strings

# stringTitles()
'''
