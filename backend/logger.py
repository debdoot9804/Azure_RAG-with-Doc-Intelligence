# backend/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE = os.path.join("logs", "app.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def setup_logger(name="docrag_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
