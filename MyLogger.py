"""Logging objects and routines.

Objects
-------
    IndentFormatter : Custom ``logging`` Formatter to add indentation based on stack level.

Functions
---------
    _getLogger    : Create a standard logger object which logs to file and or stdout stream.
    defaultLogger : Create a basic ``logging.Logger`` object, logging to stream and file.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import inspect
import numpy as np

import zcode.inout as zio

import Settings


class IndentFormatter(logging.Formatter):
    """Custom ``logging`` Formatter to add indentation based on stack level.
    """

    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.baseline = None

    def format(self, rec):
        stack = inspect.stack()
        if(self.baseline is None): self.baseline = len(stack)
        indent = (len(stack)-self.baseline)
        addSpace = ((indent > 0) & (not rec.msg.startswith(" -")))
        rec.indent = ' -'*indent + ' '*addSpace
        out = logging.Formatter.format(self, rec)
        del rec.indent
        return out


def _getLogger(name, strFmt=None, fileFmt=None, dateFmt=None, strLevel=None, fileLevel=None,
               tofile=None, tostr=True):
    """Create a standard logger object which logs to file and or stdout stream ('str')

    Arguments
    ---------
        name    <str> : handle for this logger, must be distinct for a distinct logger

        strFmt  <str>  : format of log messages to stream (stdout)
        fileFmt <str>  : format of log messages to file
        dateFmt <str>  : format of time stamps to stream and/or file
        strLevel  <int>  : logging level for stream
        fileLevel <int>  : logging level for file
        tofile  <str>  : filename to log to (turned off if `None`)
        tostr   <bool> : log to stdout stream

    Returns
    -------
        logger  <obj>  : ``logging`` logger object

    """

    if(tofile is None and not tostr): raise RuntimeError("Must log to something")

    logger = logging.getLogger(name)
    # Make sure handlers don't get duplicated (ipython issue)
    while len(logger.handlers) > 0: logger.handlers.pop()
    # Prevents duplication or something something...
    logger.propagate = 0

    # Determine and Set Logging Level
    if(fileLevel is None): fileLevel = logging.DEBUG
    if(strLevel is None): strLevel  = logging.WARNING
    # Logger object must be at minimum level; only accepts `int`
    useLevel = int(np.min([fileLevel, strLevel]))
    logger.setLevel(useLevel)

    if(dateFmt is None): dateFmt = '%Y/%m/%d %H:%M:%S'

    # Log to file
    # -----------
    if(tofile is not None):
        zio.checkPath(tofile)

        # Create default formatting for file output
        if(fileFmt is None):
            fileFmt  = "%(asctime)s %(levelname)8.8s [%(filename)20.20s:"
            fileFmt += "%(funcName)-20.20s]%(indent)s%(message)s"

        fileFormatter = IndentFormatter(fileFmt, datefmt=dateFmt)
        fileHandler = logging.FileHandler(tofile, 'w')
        fileHandler.setFormatter(fileFormatter)
        fileHandler.setLevel(fileLevel)
        logger.addHandler(fileHandler)

    # Log To stdout
    #  -------------
    if(tostr):
        # Create default formatting for stream output
        if(strFmt is None):
            strFmt = "%(indent)s%(message)s"

        strFormatter = IndentFormatter(strFmt, datefmt=dateFmt)
        strHandler = logging.StreamHandler()
        strHandler.setFormatter(strFormatter)
        strHandler.setLevel(strLevel)
        logger.addHandler(strHandler)

    return logger


def defaultLogger(fname, log=None, sets=None):
    """Create a basic ``logging.Logger`` object, logging to stream and file.

    Arguments
    ---------
        log  <obj>  : a ``logging`` level (integer), or `None` for default
        verbose <bool> : True to set 'verbose' output (`logging.INFO`)
        debug   <bool> : True to set 'debug'   output (`logging.DEBUG`), overrides ``verbose``

    Returns
    -------
        log  <obj>  : ``logging.Logger`` object.

    """

    if(isinstance(log, logging.Logger)): return log
    if(sets is None): sets = Settings.Settings()

    filename = sets.dir_log + fname

    if(sets.debug): level = logging.DEBUG
    elif(sets.verbose): level = logging.INFO
    else:                 level = logging.WARNING

    log = _getLogger(None, tostr=True, tofile=filename, strLevel=level, fileLevel=logging.DEBUG)

    return log
