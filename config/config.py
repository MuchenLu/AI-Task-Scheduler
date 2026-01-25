'''
./config/config.py
程式用途：
1. 使用 env 設置環境變數
2. 設置應用程式固定參數（如路徑等）
3. 設定驗證函式
'''
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from utils.logger import logger
from datetime import datetime

load_dotenv()

# * 路徑設定
ROOT_DIR = Path(__file__).parent.parent.resolve()
ASSETS_DIR = ROOT_DIR / "assets"
IMAGE_DIR = ASSETS_DIR / "images"
CONFIG_DIR = ROOT_DIR / "config"
SETTINGS_DIR = ROOT_DIR / "settings"
DATA_DIR = ROOT_DIR / "data"
HISTORY_DIR = DATA_DIR / "history"
LOG_DIR = ROOT_DIR / "logs"

# * 檔案設定
ICON_PNG = IMAGE_DIR / "icon.png"
ICON_ICO = IMAGE_DIR / "icon.ico"
RECORD_GIF = IMAGE_DIR / "record.gif"
CREDENTIALS_JSON = CONFIG_DIR / "credentials.json"
TOKEN_JSON = CONFIG_DIR / "token.json"
USER_CONFIG = SETTINGS_DIR / "user_config.json"
USER_PROMPT = SETTINGS_DIR / "user_prompt.py"
CURRENT_JSON = DATA_DIR / "current.json"
HISTORY_JSON = HISTORY_DIR / f"{datetime.now().strftime('%Y-%m')}.json"
LOG_FILE = LOG_DIR / "app.log"

# * 環境變數設定
API_KEY = os.getenv("API_KEY", None)

# * 驗證函式
def validate() :
    if not os.path.exists(DATA_DIR) :
        os.makedirs(DATA_DIR)
        logger.info(f"未發現 {DATA_DIR}，建立資料夾：{DATA_DIR}")
    if not os.path.exists(SETTINGS_DIR) :
        os.makedirs(SETTINGS_DIR)
        logger.info(f"未發現 {SETTINGS_DIR}，建立資料夾：{SETTINGS_DIR}")
    if not os.path.exists(USER_PROMPT) :
        os.makedirs(USER_PROMPT)
        logger.info(f"未發現 {USER_PROMPT}，建立檔案：{USER_PROMPT}")
    if not os.path.exists(ICON_PNG) :
        logger.warning(f"未發現圖示檔案：{ICON_PNG}，請確認是否存在")
    if not os.path.exists(ICON_ICO) :
        logger.warning(f"未發現圖示檔案：{ICON_ICO}，請確認是否存在")
    if not os.path.exists(RECORD_GIF) :
        logger.warning(f"未發現錄音動畫檔案：{RECORD_GIF}，請確認是否存在")
    if not os.path.exists(CREDENTIALS_JSON) :
        logger.warning(f"未發現憑證檔案：{CREDENTIALS_JSON}，請確認是否存在")
    if not os.path.exists(CURRENT_JSON) :
        with open(CURRENT_JSON, "w", encoding="utf-8") as f :
            f.write("{}")
        logger.info(f"未發現 {CURRENT_JSON}，建立空白檔案：{CURRENT_JSON}")
    if not os.path.exists(HISTORY_DIR) :
        os.makedirs(HISTORY_DIR)
        logger.info(f"未發現 {HISTORY_DIR}，建立資料夾：{HISTORY_DIR}")
    if not os.path.exists(HISTORY_JSON) :
        with open(HISTORY_JSON, "w", encoding="utf-8") as f :
            f.write("{}")
        logger.info(f"未發現今日歷史檔案：{HISTORY_JSON}，建立空白檔案：{HISTORY_JSON}")
    if API_KEY is None :
        logger.critical("未設置 API_KEY，請確認環境變數是否正確設定")
        sys.exit(1)