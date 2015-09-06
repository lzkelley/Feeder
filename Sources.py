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


import MyLogger, Settings

__version__ = 0.1



class Source(object):
    
    def __init__(self, html, title, subtitle=""):
        self.html = html
        self.title = title
        self.subtitle = subtitle
        self.name = self.title + " " + self.subtitle
        self.version = __version__

    def __str__(self):
        return self.name


# } class Source

'''
class Sources(object):

    import json

    def __init__(self):
        

# } class Sources
'''





def main(sets=None, log=None):
    """

    """

    sets = Settings.getSettings(sets)
    log = _getLogger(log, sets)
    log.info("main()")
    log.debug("version = '%s'" % str(__version__))
    log.debug("Settings version = '%s'" % (str(sets.version)))

    log.debug("Getting command line arguments")
    parser = Settings.getParser(sets)
    args, sets = Settings.getArgs(parser, sets)

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
    filename = sets.dir_log + "Sources.log"
    log = MyLogger.defaultLogger(log, filename=filename, verbose=sets.verbose, debug=sets.debug)
    return log
# } _getLogger()




if( __name__ == "__main__" ): main()
