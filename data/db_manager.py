import json
import os
import shutil
import threading
import datetime
from pathlib import Path
from dateutil.relativedelta import relativedelta
from config import config
from utils.logger import logger

class DBManager :
    def __init__(self):
        self.history_dir = config.DATA_DIR / "history"
        self.current_task_file = config.DATA_DIR / "current_task.json"
        self.subtask_json = config.DATA_DIR / "subtask.json"
        self.lock = threading.Lock()
    
    def _load_json(self, filepath: Path) :
        with self.lock :
            try :
                with open(filepath, "r", encoding = "utf-8") as f :
                    return json.load(f)
            except Exception as e :
                logger.error(f"Read json file failed: {e}")
                return None
    
    def _save_json(self, filepath: Path, data: dict) :
        with self.lock :
            try :
                with open(filepath, "w", encoding = "utf-8") :
                    json.dump(data, ensure_ascii = False, indent = 4)
            except Exception as e :
                logger.error(f"Write json file error: {e}")
    
    def get_subtask(self, task_id: str) :
        data = self._load_json(self.subtask_json).get(task_id, None)
        if data :
            return data
        else :
            return None
    
    def save_subtask(self, data: dict) :
        self._save_json(self.subtask_json, data)
    
    def get_current_task(self) -> dict | None :
        data = self._load_json(self.current_task_file)
        if data :
            return data
        else :
            return None
    
    def save_current_task(self, data: dict) :
        self._save_json(self.current_task_file, data)
    
    def archive_task(self, data: dict) :
        now = datetime.datetime.now()
        filename = f"{now.year}-{now.month}.json"
        filename = config.DATA_DIR / filename
        
        history_list = self._load_json(filename)
        history_list.append(data)
        self._save_json(filename, history_list)
    
    def get_history(self, long: int) -> list | None :
        """Get task history

        Args:
            long (int): How many month history you want to get.

        Returns:
            list: Tasks list.
        """
        data = []
        for target in range(long) :
            target_date = datetime.datetime.now() - relativedelta(month = target)
            filename = f"{target_date.year}-{target_date.month}.json"
            data.append(self._load_json(filename))
        
        if data :
            return data
        else :
            return None

db = DBManager()