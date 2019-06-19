import logging
import logging.handlers
import os

LOGGER_NAME = "pyGoPro"
LOGGER_FMT  = '%(levelname)s: %(message)s'
LOGGER_FMT_CHILD = '%(levelname)s[%(name)s]: %(message)s'


lh = logging.StreamHandler()
sh = None
fh = None
logger = logging.getLogger(LOGGER_NAME)

def setupLogger(quiet:bool = False, verbose:bool = False, syslog:bool = False, directory:str = None):
    lh.setFormatter(LogFormatter())

    lvl = logging.ERROR if quiet else (logging.DEBUG if verbose else logging.INFO)
    logging.basicConfig(level=lvl, format=LOGGER_FMT)

    logger.propagate = False
    logger.addHandler(lh)

    if syslog:
        sh = logging.handlers.SysLogHandler(address='/dev/log')
        sh.setFormatter(logging.Formatter('GoPro:'+LOGGER_FMT_CHILD))
        logger.addHandler(sh)

    if directory and os.path.isdir(directory):
        # log to files by day and only warning and above
        fh = logging.handlers.TimedRotatingFileHandler(os.path.join(directory, LOGGER_NAME+'.log'), 'D', backupCount=5)
        fh.setLevel(logging.WARNING)
        fh.setFormatter(LogFormatter(True))
        fh.addFilter(DuplicateFilter(logging.WARNING))
        logger.addHandler(fh)

def __addHandler(l:logging.Logger, h:logging.Handler):
    # check before adding handler
    if h not in l.handlers:
        l.addHandler(h)

def getLogger(name):
    l = logger.getChild(name)
    return l

class LogFormatter(logging.Formatter):

    def __init__(self, include_date:bool=False):
        super().__init__()
        self.include_date = include_date

    def format(self, record):
        prefix = self.formatTime(record) + ' ' if self.include_date else ''
        if record.name != LOGGER_NAME:
            self._style._fmt = prefix + LOGGER_FMT_CHILD
        else:
            self._style._fmt = prefix + LOGGER_FMT

        return logging.Formatter.format(self, record)  # super(LogFormatter, self).format(format)


class DuplicateFilter(logging.Filter):
    def __init__(self, lvl):
        super().__init__()
        self.last_log = None
        self.last_cnt = 0

    def filter(self, record:logging.LogRecord):
        # make sure my own messages gets logged without interfering with other messages
        if os.path.splitext(os.path.basename(__file__))[0] == record.module:
            return True
        # the current log record
        current_log = (record.module, record.levelno, record.msg)
        current_cnt = self.last_cnt
        # did the record change in comparison to the last?
        if current_log != self.last_log:
            # reset count before logging the 'informational' message
            self.last_cnt = 0
            # if the last message was logged multiple times, log that info
            if current_cnt != 0:
                logger.log(self.last_log[1], "The last message occurred %d times", current_cnt)
            # set the new message
            self.last_log = current_log
            return True
        # update same message counter
        self.last_cnt += 1
        return False

# make methods public
error = logger.error
warning = logger.warning
info = logger.info
debug = logger.debug
log = logger.log