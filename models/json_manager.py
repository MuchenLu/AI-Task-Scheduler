import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Literal
from utils.logger import logger
from config.config import HISTORY_DIR, HISTORY_JSON, CURRENT_JSON

class JsonManager() :
    def __init__(self):
        now = datetime.now()
        self.history_files = [HISTORY_JSON]
        for i in range(1, 3) :
            date = now - relativedelta(months = i)
            year = date.year
            month = date.month
            self.history_files.insert(0, HISTORY_DIR / f"{year}-{month}.json")
        self.CURRENT_JSON = CURRENT_JSON
    
    def _read_json(self, file: str) -> list :
        """用於讀取 json 檔案

        Args:
            file (str): 檔案路徑

        Returns:
            list: 檔案內容
        """
        try :
            with open(file, "r", encoding="utf-8") as f :
                data = json.load(f)
                return data
        except json.JSONDecodeError :
            logger.warning(f"{file} 檔案讀取錯誤，檔案可能為空")
            return []
    
    def _write_json(self, mode: Literal["w", "a"], file: str, data: list) :
        """寫入 json 檔

        Args:
            mode ("w" | "a"): 選擇寫入或追加模式
            file (str): 檔案路徑
            data (list): 寫入內容
        """
        try :
            match mode :
                case "w" :
                    with open(file, "w", encoding="utf-8") as f :
                        json.dump(data, f, ensure_ascii=False, indent=4)
                case "a" :
                    data = self._read_json(file).extend(data)
                    with open(file, "w", encoding="utf-8") as f :
                        json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e :
            logger.error(f"寫入檔案 {file} 時遇到錯誤: {e}")
    
    def get_history(self) -> list :
        """取得歷史資料

        Returns:
            list: 歷史資料
        """
        history = []
        for file in self.history_files :
            if Path(file).exists() :
                history.extend(self._read_json(file))
        return history

    def get_current(self) -> list :
        """取得進行中任務

        Returns:
            list: 進行中任務
        """
        return self._read_json(self.CURRENT_JSON)
    
    def write_history(self, data: dict) :
        """寫入完成任務

        Args:
            data (dict): 完成的任務資料
        """
        self._write_json("a", HISTORY_JSON, [data])
    
    def write_current(self, data: list) :
        """寫入進行中任務

        Args:
            data (list): 完整更新的任務狀態
        """
        self._write_json("w", CURRENT_JSON, data)

manager = JsonManager()