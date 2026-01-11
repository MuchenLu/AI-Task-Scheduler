import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

logger = logging.getLogger("AI-Task-Manager")
logger.setLevel(logging.DEBUG)

def setup_logger(log_folder: Path) :
    """use to write log into file and print out.

    Args:
        log_folder (Path): where to save log file.
    """
    #* === File Handler ===
    if any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers) : # NOTE: avoid duplicate handlers
        return
    
    log_file_path = log_folder / "app.log"
    
    file_handler = TimedRotatingFileHandler(
        filename = log_file_path,
        when = "midnight",
        interval = 1,
        backupCount = 7,
        encoding = "utf-8",
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(fmt = "%(asctime)s - %(levelname)s | %(filename)s:%(lineno)d | - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    #* === Stream Handler ===
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers) : # NOTE: avoid duplicate handlers
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_formatter = logging.Formatter(fmt = "%(asctime)s - %(levelname)s | %(filename)s:%(lineno)d | %(message)s")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)
    
    logger.info(f"Logger is set up. Log file path: {log_file_path}")