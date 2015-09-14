

import Feeder, SourceList, Settings, Source, MyLogger, feedparser
reload(Feeder); reload(Settings); reload(Source); reload(SourceList)
sets = Settings.Settings(); log = MyLogger.defaultLogger('temp.log', sets); sourceList = SourceList.SourceList(sets=sets, log=log)

