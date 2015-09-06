"""

"""


import Sources
import rss
from datetime import datetime
import numpy as np


def main():
    
    beg = datetime.now()

    sources = Sources.sources
    names, feeds = loadSources(sources)

    numFeeds = 0
    numStories = 0

    for nn,ff in zip(names, feeds):
        titles = rss.stringTitles(ff, True)
        if( np.size(titles) > 0 ):
            numFeeds += 1
            numStories += np.size(titles)

        print nn
        for tt in titles:
            print "\t",tt

        print ""


    
        
    print "Feeds: %d" % (numFeeds)
    print "Stores: %d" % (numStories)

    end = datetime.now()
    print "After %s" % (str(end-beg))

    
    return

# } main()


def loadSources(sources):
    names = []
    feeds  = []
    for src in sources:
        names.append(str(src))
        feeds.append(rss.entries(src.html))

    return names, feeds

# } loadSources()


if( __name__ == "__main__"): main()
