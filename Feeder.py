"""

"""


from datetime import datetime
import numpy as np

import Settings, Sources, rss, MyLogger


__version__ = 0.1
_LOG_FILENAME = "Feeder.log"


def main():
    """

    """
    
    beg = datetime.now()

    ## Initialization
    #  --------------
    sets = Settings.Settings()
    log = MyLogger.defaultLogger(_LOG_FILENAME, sets=sets)
    log.info("Feeder.py")
    log.debug("main()")
    log.debug("version = '%s'" % str(__version__))
    log.debug("Settings version = '%s'" % (str(sets.version)))

    # Command-Line Arguments
    log.debug("Getting command line arguments")
    parser = Settings.getParser(sets)
    args, sets = Settings.getArgs(parser, sets)

    # Load Sources
    log.info("Initializing Sources")
    sources = Sources.Sources(log=log, sets=sets)
    log.info("Loading Sources")
    names, feeds = loadSources(sources, log)

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
    log.info("Done After %s\n" % (str(end-beg)))

    return

# } main()


def loadSources(sources, log):
    """
    """
    log.debug("loadSources()")

    names = []
    feeds  = []
    log.debug(" - Loading feeds for %d sources" % (sources.count))
    for src in sources.sources:
        names.append(str(src))
        feeds.append(rss.entries(src.url))

    return names, feeds

# } loadSources()


if( __name__ == "__main__"): main()
