import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger


def init_logging():
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
