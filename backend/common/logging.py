import os
import logging


def get_logger(name):
    logger = logging.getLogger(name)
    level = os.getenv('LOGGING_LEVEL_APP', "INFO")
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger


def init_logging():
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
