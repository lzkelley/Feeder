

import SourceList

sourceList = SourceList.SourceList()

src = sourceList.sources[0]
src.getFeed()

print "SAVING"
src.saveArticles()


print "LOADING"
arts = src.loadArticles()
for aa in arts:
    print aa.str()

