import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("AI-Task-Manager")
logger.setLevel(logging.DEBUG)

def setup_logger(log_folder: Path):
    """將日誌寫入文件並輸出到終端機。"""
    
    #* === File Handler ===
    # 檢查是否已經有檔案處理器
    if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
        log_file_path = log_folder / "app.log"
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s | %(filename)s:%(lineno)d | - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    #* === Stream Handler ===
    # 關鍵修正：使用 type(h) is logging.StreamHandler 來排除 FileHandler 子類別
    if not any(type(h) is logging.StreamHandler for h in logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s | %(filename)s:%(lineno)d | %(message)s")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)
    
    logger.info("Logger 初始化完成。")