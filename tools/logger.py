import logging

def get_logger(logger_name: str) -> logging.Logger:
    """
    Get logger with all logging levels

    :param logger_name: same as python filename
    :return: Logger object
    """
    logger = logging.getLogger(logger_name)
    FORMAT = '%(levelname)s | %(name)s:%(lineno)s | %(message)s'
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    #logger_name = logger_name.replace('.py', '.log')
    #handler = logging.FileHandler(filename=f'C:\\Bot\\Logs\\{logger_name}',
    #                              encoding='utf-8')
    handler.setFormatter(logging.Formatter(FORMAT))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
