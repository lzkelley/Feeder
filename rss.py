"""

"""

import feedparser
import numpy as np

TITLE_WIDTH = 140


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
