

import Feeder, Settings, Sources, rss, MyLogger, feedparser
reload(Feeder); reload(Settings); reload(Sources)
sets = Settings.Settings(); log = MyLogger.defaultLogger('temp.log', sets); sourceList = Sources.SourceList(sets=sets, log=log)

