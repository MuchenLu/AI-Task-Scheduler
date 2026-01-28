'''
./utils/logger.py
程式用途：
1. 設置應用程式 log 紀錄
2. 定義 log 格式與 level
3. 提供 log 寫入檔案與輸出終端機
'''
import logging
from logging.handlers import TimedRotatingFileHandler
import sys

logger = logging.getLogger("SCHEDAI")
logger.setLevel(logging.DEBUG)

if not logger.handlers :
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)-8s %(filename)s:%(lineno)d | %(message)s', datefmt = "%H:%M:%S")
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

def setup_logger(log_file: str) :
    """用於設置完整 logger

    Args:
        log_file (str): 傳入 log 檔案路徑
    """
    file_handler = TimedRotatingFileHandler(filename = log_file, when = "midnight", interval = 1, backupCount = 7, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)-8s %(filename)s:%(lineno)d | %(message)s', datefmt = "%H:%M:%S"))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    logger.info(f"Log 設定完成，寫入檔案：{log_file}")