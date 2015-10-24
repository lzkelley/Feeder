"""

"""
from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
import numpy as np

import Settings, SourceList, MyLogger


_LOG_FILENAME = "feeder.log"


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
    log.debug("version = '%s'" % str(Settings.__version__))

    # Command-Line Arguments
    log.debug("Getting command line arguments")
    parser = Settings.getParser(sets)
    args, sets = Settings.getArgs(parser, sets)

    # Load Sources
    log.info("Initializing SourceList")
    sourceList = SourceList.SourceList(log=log, sets=sets)
    log.info("Loading Feeds")
    #sourceList.getFeeds()


    # Print New Articles
    for ii, src in enumerate(sourceList.sources):
        src.getFeed()
        print("{0:3d} : {1}".format(ii, src.str()))

        if(src.valid):
            for jj,art in enumerate(src.articles):
                print("\t{0:3d} : {1}".format(jj, art.str()))

        else:
            print("\tINVALID")


    end = datetime.now()
    log.info("Done After %s\n" % (str(end-beg)))

    return

# } main()


def loadSources(sourceList, log):
    """
    """
    log.debug("loadSources()")

    names = []
    feeds  = []
    log.debug(" - Loading feeds for %d sources" % (sourceList.count))
    for src in sourceList.sources:
        names.append(str(src))
        feeds.append(rss.entries(src.url))

    return names, feeds

# } loadSources()


if(__name__ == "__main__"): main()
