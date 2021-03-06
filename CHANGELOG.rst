Change Log
==========

-   Project
    +   Updated code for python3 compatibility with python2 backwards compatibility.
-   SourceList.py
    +   Added methods to update old versions of the save file to new versions.
    +   Added entries in the save file for `Source` filenames (for saving old articles), and times
        when those files are updated.  Not implemented yet.
-   Settings.py
    +   The `__version__` now corresponds to the global version of the project.
-   Source.py
    +   Added methods 'saveArticles()' and 'loadArticles()' to handle saving and loading 'Article'
        objects respectively.



## [0.1] : '2015-09-12'
#  --------------------
-   Feeder.py
    +   Main interactive script.  Loads `SourceList`, and prints the most recent RSS feeds.
-   SourceList.py
    +   Maintains a savefile including a list of information to construct `Source` objects.
    +   Creates and manages list of `Source` objects.
-   Source.py
    +   Includes the `Source` and `Article` classes.  `Source` loads a set of `Article` objects
        from an RSS feed.
-   Settings.py
    +   Includes global settings.
    +   Object is setup as a singleton.
-   MyLogger.py
    +   Creates custom `logging.Logger` objects for logging.
