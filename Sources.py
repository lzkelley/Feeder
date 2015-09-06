"""

"""

class Source(object):
    
    def __init__(self, html, title, subtitle=""):
        self.html = html
        self.title = title
        self.subtitle = subtitle
        self.name = self.title + " " + self.subtitle

    def __str__(self):
        return self.name


# } class Source



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


