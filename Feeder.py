"""

"""


import Sources
import rss


def main():
    sources = Sources.sources
    names, feeds = loadSources(sources)

    for nn,ff in zip(names, feeds):
        titles = rss.stringTitles(ff, True)
        print nn
        for tt in titles:
            print "\t",tt

        print ""
    
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
