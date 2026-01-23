import json
from pathlib import Path
from utils.logger import logger
from config.config import USER_CONFIG

def load_user_config() :
    try :
        with open(USER_CONFIG, "r", encoding="utf-8") as f :
            data = json.load(f)
            if ["USER_NAME", "CAREER", "AVAILABLE_TIME", "HIGH_EFFICIENCY_TIME", "REST_BUFFER_TIME", "DAILY_TASK_LIMIT", "TASK_DECOMPOSITION", "DEFAULT_TASK_DURATION", "GOOGLE_CALENDAR_ID"] not in data.keys() :
                logger.error(f"使用者設定檔缺少必要欄位：{USER_CONFIG}，將啟動 setup 程式以重新建立。")
                return False
            return True
    except FileNotFoundError :
        logger.warning(f"未發現使用者設定檔：{USER_CONFIG}，將啟動 setup 程式。")
        return False
    except json.JSONDecodeError :
        logger.error(f"使用者設定檔格式錯誤：{USER_CONFIG}，將啟動 setup 程式以重新建立。")
        return False