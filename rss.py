"""

"""

import feedparser, time
from bs4 import BeautifulSoup
import numpy as np

import MyLogger, Settings

TITLE_WIDTH = 140




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



class Feed(object):
    
    def __init__(self, url):
        """
        """
        rssf = feedparser.parse(url)
        self._rssfeed = rssf
        self.status = rssf.status
        self.url = url
        self.valid = False
        self.articles = []
        self.count = 0

        if( self.status != 200 or not hasattr(rssf, 'feed') ): 
            print "\tBad status/feed!"
            return

        if( not hasattr(rssf.feed, 'title') ):
            print "\tBad title!"
            return

        self.title = rssf.feed.title

        self.time = self._hasGet(rssf, 'updated_parsed')
        if( self.time is None ): self.time = self._hasGet(rssf, 'published_parsed')

        if( hasattr(rssf, 'entries') ):
            for ent in rssf.entries:
                art = Article(ent)
                if( art.valid ): self.articles.append(art)

            self.count = len(self.articles)

        if( self.count == 0 ): return

        self.valid = True
        return


    def _hasGet(self, rssf, key):
        """
        Check for attribute ``key`` in given rssfeed or rssfeed.feed.  Return ``None`` if neither.
        """

        if( hasattr(rssf, key) ):
            return getattr(rssf, key)
        elif( hasattr(rssf.feed, key) ):
            return getattr(rssf.feed, key)

        return None
    



def getFeeds(sourceList, log):

    
    log.debug("getFeeds()")

    ids = []
    feeds = []
    for ii, src in enumerate(sourceList.sources):
        feed = Feed(src.url)
        print "%d, %s --- %d" % (ii, src.name, feed.count)
        if( feed.valid ): 
            ids.append(ii)
            feeds.append(feed)


    return ids, feeds
    




def entries(addy):
    feed = feedparser.parse(addy)
    return feed.entries


def _formatDatetime(parsed, date=True, time=True):

    if( not np.iterable ): parsed = [ parsed ]

    datetime = []

    for elem in parsed:

        temp = ""
        if( date ): 
            temp += "{:04d}/{:02d}/{:02d}".format(*elem[0:3])
            if( time ): temp += " - "

        if( time ): temp += "{:02d}:{:02d}:{:02d}".format(*elem[3:6])

        datetime.append(temp)

    # } for elem

    if( np.size(parsed) == 1 ): datetime = datetime[0]

    return datetime

# } _formatDatetime()
    


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
