import logging
import sys

formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

def setup_logger(name, log_file, stdout=False, level=logging.INFO):
    """To setup as many loggers as you want"""

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    if stdout is True:
        stream_handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    if stdout is True:
        logger.addHandler(stream_handler)

    return logger

def setupRootLogger(log_file, log_level = 'INFO'):
    # Stream handler for root logger
    root_sh = logging.StreamHandler(sys.stdout)
    root_sh.setLevel(logging.DEBUG)

    # formatter = logging.Formatter('[%(asctime)s] %(levelname)s @ line %(lineno)d: %(message)s')
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    root_sh.setFormatter(formatter)

    root_fh = logging.handlers.WatchedFileHandler(
        # os.environ.get("LOGFILE", config.LOGFILE)
        log_file, encoding='utf-8'
    )
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    root_fh.setFormatter(formatter)


    '''
        getLogger is a module-level function. 
        logging.getLogger(name=None)
        Return a logger with the specified name or, if name is None, return a logger which is the root logger of 
        the hierarchy. If specified, the name is typically a dot-separated hierarchical name like ‘a’, ‘a.b’ or 
        ‘a.b.c.d’. Choice of these names is entirely up to the developer who is using logging.

        All calls to this function with a given name return the same logger instance. This means that logger 
        instances never need to be passed between different parts of an application.
    '''
    root = logging.getLogger()

    # root.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))  # DEBUG will print boto3 debug messages
    # root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    root.setLevel(os.environ.get("LOGLEVEL", log_level))

    root.addHandler(root_sh)
    root.addHandler(root_fh)
    return root

def get_rotating_log_file(logger_name, log_file=None):
    """
    Can call like this from a derived class:
        self.failed_log = self.get_rotating_log_file(logger_name='failed', log_file='/Users/john/temp/hiii.log')
        self.failed_log = self.get_rotating_log_file(logger_name='failed')
    :param logger_name:
    :param log_file:
    :return:
    """
    if log_file is None:
        log_file = logger_name + '.log'
    log_handler = logging.handlers.WatchedFileHandler(log_file)
    formatter = logging.Formatter(
        '%(asctime)s: %(message)s',
        '%b %d %Y %H:%M:%S')
    log_handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    return logger;

def get_daily_rotating_log_file(logger_name, log_file=None):
    if log_file is None:
        log_file = logger_name + '.log'
    log_handler = logging.handlers.TimedRotatingFileHandler(log_file, when="midnight", interval=1)
    log_handler.suffix = "%Y%m%d"
    formatter = logging.Formatter(
        '%(asctime)s: %(message)s',
        '%b %d %Y %H:%M:%S')
    log_handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    # logs logged by this logger should only going to THIS file and not bubble up to console/main file
    # handlers for the main logger, hence propagate = False
    logger.propagate = False
    return logger;