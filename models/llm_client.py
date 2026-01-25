'''
./models/llm_client.py
模組功能：
1. 分析使用者意圖
2. 拆解任務
3. 推薦使用者任務時間
4. 更改任務狀態
'''
from ast import literal_eval
import os
import sys
from datetime import datetime
import google.generativeai as genai
from models.calendar_sync import calendar
from models.json_manager import manager
from utils.date_helpper import to_ISO8601
from utils.prompts import SCHEDULER_PROMPT, USER_INTENT_PROMPT, STATE_CONTROLLER_PROMPT, GENERATE_DECOMPOSITION_PROMPT
from utils.logger import logger
from config.config import USER_CONFIG, USER_PROMPT, API_KEY
try :
    from settings.user_prompt import DECOMPOSITION_PROMPT
    new_prompt = False
except ImportError :
    logger.warning("任務拆解 prompt 不存在，將自動建立")
    new_prompt = True

class SafeDict(dict) :
    def __missing__(self, key) :
        return "{" + key + "}"

class LLMClient() :
    def __init__(self):
        try :
            genai.configure(api_key = API_KEY)
            self.model = genai.GenerativeModel("gemini-2.5-pro")
            logger.info("LLM 設定完成")
        except Exception as e :
            logger.critical(f"LLM 設定出錯: {e}")
            sys.exit(1)
        self.SCHEDULER_PROMPT = SCHEDULER_PROMPT
        self.USER_INTENT_PROMPT = USER_INTENT_PROMPT
        self.STATE_CONTROLLER_PROMPT = STATE_CONTROLLER_PROMPT
        self.GENERATE_DECOMPOSITION_PROMPT = GENERATE_DECOMPOSITION_PROMPT
        
        self.SCHEDULER_PROMPT = self._combine_user_settings(self.SCHEDULER_PROMPT, {"rest_buffer_time": os.getenv("REST_BUFFER_TIME"),
                                                                            "available_time": os.getenv("AVAILABLE_TIME"),
                                                                            "daily_task_limit": os.getenv("DAILY_TASK_LIMIT"),
                                                                            "high_efficiency_time": os.getenv("HIGH_EFFICIENCY_TIME")})
        if new_prompt :
            self.GENERATE_DECOMPOSITION_PROMPT = self._combine_user_settings(self.GENERATE_DECOMPOSITION_PROMPT, {"task_decomposition": os.getenv("TASK_DECOMPOSITION")})
            self.DECOMPOSITIPON_PROMPT = self.model.generate_content(self.GENERATE_DECOMPOSITION_PROMPT).text.replace("````", "").replace("{{{{", "{{").replace("}}}}", "}}").replace("{{task_context}}", "{task_context}").replace("{{historical_data}}", "{historical_data}")
            logger.debug(self.DECOMPOSITIPON_PROMPT)
            with open(USER_PROMPT, "w", encoding="utf-8") as f :
                f.write(f'DECOMPOSITION_PROMPT = """\n{self.DECOMPOSITIPON_PROMPT}\n"""')
            logger.debug(self.DECOMPOSITIPON_PROMPT)
        else :
            self.DECOMPOSITIPON_PROMPT = DECOMPOSITION_PROMPT
    
    def _combine_user_settings(self, prompt: str, user_settings: dict) -> str :
        """將 prompt 模板結合使用者設定

        Args:
            prompt (str): 須結合的 prompt 模板
            user_settings (dict): 欲結合的使用者設定

        Returns:
            str: 結合後的 prompt
        """
        prompt.format_map(SafeDict(user_settings))
        return prompt
    
    def _format_prompt(self, prompt: str, content: dict) -> str :
        """將 prompt 中的變數替換成真實內容

        Args:
            prompt (str): 代替換的 prompt
            content (dict): 欲替換的內容

        Returns:
            str: 替換完成後的 prompt
        """
        prompt.format_map(content)
        return prompt

    def analyze_intent(self, calendar_events: list, existing_tasks_db: list, command: str) -> list :
        """分析使用者意圖（支援多意圖）

        Args:
            calendar_events (list): 行事曆事件
            existing_tasks_db (list): 進行中任務
            command (str): 使用者原指令

        Returns:
            list: 使用者意圖列表
        """
        current_time = to_ISO8601(datetime.now(), "str")
        prompt = self._format_prompt(self.USER_INTENT_PROMPT, {"current_time": current_time,
                                                               "calendar_events": calendar_events,
                                                               "existing_tasks_db": existing_tasks_db,
                                                               "command": command})
        result = self.model.generate_content(prompt).text.replace("```json", "").replace("```", "")
        try :
            result = literal_eval(result)
            return result
        except SyntaxError :
            raise SyntaxError(f"AI 分析意圖回覆格式錯誤或無效: {result}")
    
    def decomposition_task(self, task_context: dict, historical_data: list) -> dict :
        """判斷使用者的任務是否需要拆解

        Args:
            task_context (dict): 任務內容
            historical_data (list): 歷史紀錄

        Returns:
            dict: 是否需要拆解及如何拆解
        """
        prompt = self._format_prompt(self.DECOMPOSITIPON_PROMPT, {"task_context": task_context,
                                                                  "historical_data": historical_data})
        result = self.model.generate_content(prompt).text.replace("```json", "").replace("```", "")
        try :
            result = literal_eval(result)
            return result
        except SyntaxError :
            raise SyntaxError(f"AI 拆解回覆格式錯誤或無效: {result}")

    def scheduler_prompt(self, task_content: dict) -> list :
        """用於推薦使用者任務時間

        Args:
            task_content (dict): 任務資訊

        Returns:
            list: 任務推薦時間清單
        """
        calendar_events = calendar.get_calendar_events(to_ISO8601(datetime.now(), "str"), to_ISO8601(task_content["end"]["dateTime"]))
        historical_logs = manager.get_history()
        prompt = self._format_prompt(self.SCHEDULER_PROMPT, {"calendar_events": calendar_events,
                                                             "historical_logs": historical_logs,
                                                             "task_content": task_content})
        result = self.model.generate_content(prompt).text.replace("```json", "").replace("```", "")
        try :
            result = literal_eval(result)
            return result
        except SyntaxError :
            raise SyntaxError(f"AI 時間推薦回覆格式錯誤或無效: {result}")
    
    def change_state_prompt(self, actions: dict) -> list :
        """用於更新任務狀態

        Args:
            actions (dict): 要動作的任務及動作

        Returns:
            list: 更新後的完整任務狀態
        """
        current_time = to_ISO8601(datetime.now(), "str")
        current_active_tasks_json = manager.get_current()
        calendar_tasks = calendar.get_calendar_events(to_ISO8601(datetime.now(), "str"))
        prompt = self._format_prompt(self.STATE_CONTROLLER_PROMPT, {"current_time": current_time,
                                                                    "current_active_tasks_json": current_active_tasks_json,
                                                                    "calendar_tasks": calendar_tasks,
                                                                    "actions": actions})
        try :
            result = literal_eval(result)
            return result
        except SyntaxError :
            raise SyntaxError(f"AI 更新任務狀態回覆格式錯誤或無效: {result}")

llm = LLMClient()