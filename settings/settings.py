import json
import os
from pathlib import Path
from utils.logger import logger
from config.config import USER_CONFIG

def load_user_config() :
    try :
        with open(USER_CONFIG, "r", encoding="utf-8") as f :
            data = json.load(f)
            if not all(key in data for key in ("USER_NAME", "CAREER", "AVAILABLE_TIME", "HIGH_EFFICIENCY_TIME", "REST_BUFFER_TIME", "DAILY_TASK_LIMIT", "TASK_DECOMPOSITION", "DEFAULT_TASK_DURATION", "GOOGLE_CALENDAR_ID")) :
                logger.error(f"使用者設定檔缺少必要欄位：{USER_CONFIG}，將啟動 setup 程式以重新建立。")
                return False
            os.environ["USER_NAME"] = data["USER_NAME"]
            os.environ["CAREER"] = data["CAREER"]
            os.environ["AVAILABLE_TIME"] = data["AVAILABLE_TIME"]
            os.environ["HIGH_EFFICIENCY_TIME"] = data["HIGH_EFFICIENCY_TIME"]
            os.environ["REST_BUFFER_TIME"] = data["REST_BUFFER_TIME"]
            os.environ["DAILY_TASK_LIMIT"] = str(data["DAILY_TASK_LIMIT"])
            os.environ["TASK_DECOMPOSITION"] = data["TASK_DECOMPOSITION"]
            os.environ["DEFAULT_TASK_DURATION"] = data["DEFAULT_TASK_DURATION"]
            calendars = data["GOOGLE_CALENDAR_ID"]
            os.environ["GOOGLE_CALENDAR_ID"] = str([item["id"] for item in data["GOOGLE_CALENDAR_ID"]])
            print(os.environ["GOOGLE_CALENDAR_ID"])
            for calendar in calendars :
                if calendar.get("choose", False) :
                    os.environ["TASK_CALENDAR"] = calendar["id"]
                    break
            return True
    except FileNotFoundError :
        logger.warning(f"未發現使用者設定檔：{USER_CONFIG}，將啟動 setup 程式。")
        return False
    except json.JSONDecodeError :
        logger.error(f"使用者設定檔格式錯誤：{USER_CONFIG}，將啟動 setup 程式以重新建立。")
        return False