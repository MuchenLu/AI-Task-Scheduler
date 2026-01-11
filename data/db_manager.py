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
        self.history_dir.mkdir(parents=True, exist_ok=True)
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
                with open(filepath, "w", encoding = "utf-8") as f :
                    json.dump(data, f, ensure_ascii = False, indent = 4)
            except Exception as e :
                logger.error(f"Write json file error: {e}")
    
    def get_subtask(self, task_id: str) :
        # 修正：先檢查 data 是否為 None，避免 AttributeError
        data = self._load_json(self.subtask_json)
        if data:
            return data.get(task_id, None)
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
        filepath = self.history_dir / f"{now.year}-{now.month}.json"
        
        # 核心修正：明確檢查檔案是否存在，如果不存在，則先建立一個包含空列表的檔案。
        # 這讓後續的讀取-修改-寫入流程更加穩健，並直接回應了使用者的需求。
        if not filepath.exists():
            self._save_json(filepath, [])

        history_list = self._load_json(filepath) or []
        history_list.append(data)
        self._save_json(filepath, history_list)
    
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
            filepath = self.history_dir / f"{target_date.year}-{target_date.month}.json"
            # 修正：使用正確的 filepath 物件來讀取檔案，而不是僅用檔名字串。
            # 同時只加入成功讀取的歷史資料，並使用 extend 將多個月份的任務合併成一個扁平列表。
            loaded_data = self._load_json(filepath)
            if loaded_data:
                data.extend(loaded_data)
        
        if data :
            return data
        else :
            return None

db = DBManager()