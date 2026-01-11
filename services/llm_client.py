import json
import ast
import os
import datetime
from dateutil.relativedelta import relativedelta
import pytz
import google.generativeai as genai
from config import config
from utils.logger import logger
from utils.prompts import SCHEDULER_PROMPT, SLICE_TASK_PROMPT, USER_INTENT_PROMPT, STATE_CONTROLLER_PROMPT
from services.calendar_sync import calendar_service
from data.db_manager import db

class LLMClient :
    def __init__(self):
        try :
            genai.configure(api_key = config.API_KEY)
            self.model = genai.GenerativeModel("gemini-2.5-pro")
            logger.info("LLMClient initialized")
        except Exception as e :
            logger.critical(f"Error initializing LLMClient: {e}")
            self.model = None
        
    def _clean_response(self, text: str) -> dict :
        """use to clean AI's response and turn into dict

        Args:
            text (str): AI's response.

        Returns:
            dict: AI's response as dict.
        """
        try :
            text = text.replace("```json", "").replace("```", "").strip()
            text = ast.literal_eval(text)
            return text
        except Exception as e :
            logger.error(f"Error cleaning response: {e}")
            return None

    def sugget_schedule(self, command: dict) -> dict :
        """use AI to suggest user three recommand schedule

        Args:
            command (dict): Command has been AI format.
        """
        if command is None:
            logger.warning("command is None.")
            return None
        
        now = datetime.datetime.now(pytz.timezone('Asia/Taipei')).isoformat(timespec = "seconds")

        # 修正：確保 end 時間符合 RFC 3339 格式，避免 Google API 400 錯誤
        due_date = command.get("due_date")
        fetch_end = None
        if due_date:
            # 關鍵修正：只取 due_date 的日期部分 (前10個字元)，以建立一個格式正確的 RFC3339 時間字串。
            # 這可以防止當 due_date 包含時間 (如 "2026-01-16 23:59:59") 時，產生格式錯誤的字串。
            base_date_str = due_date[:10]
            fetch_end = f"{base_date_str}T23:59:59+08:00"

        calendar_events = calendar_service.get_calendar_events("all", end=fetch_end)
        active_tasks_db = db.get_current_task() or []
        historical_logs = db.get_history(3)
        
        prompt = SCHEDULER_PROMPT.format(current_time = now,
                                         command = command,
                                         calendar_events = calendar_events,
                                         active_tasks_db = active_tasks_db,
                                         historical_logs = historical_logs)
        result = self._clean_response(self.model.generate_content(prompt).text)
        
        if result :
            logger.info(f"AI clean response: {result}")
            return result
        else :
            logger.error(f"Clean AI response failed or ai response wrong.")
            return None
    
    def slice_task(self, command: dict) -> dict :
        if command is None :
            logger.warning("Command is None.")
        
        historical_data = db.get_history()
        
        prompt = SLICE_TASK_PROMPT.format(task_context = command, historical_data = historical_data)
        result = self.model.generate_content(prompt)
        
        if result :
            return result
        else :
            return None
    
    def analyze_intent(self, command: str) -> dict :
        """Analyze user's intent.

        Args:
            command (str): command from user

        Returns:
            dict: AI's response in dict.
        """
        current_time = datetime.datetime.now(pytz.timezone('Asia/Taipei')).isoformat(timespec = "seconds")
        file = config.DATA_DIR / "current_task.json"
        existing_tasks_db = db.get_current_task() or []
        calendar_events = calendar_service.get_calendar_events('all')
        
        prompt = USER_INTENT_PROMPT.format(current_time = current_time,
                                           calendar_events = calendar_events,
                                           existing_tasks_db = existing_tasks_db,
                                           command = command)
        result = self._clean_response(self.model.generate_content(prompt).text)
        
        if result :
            logger.info(f"AI clean response: {result}")
            return result
        else :
            logger.error("Clean AI response failed or ai response wrong.")
            return None
    
    def change_status(self, incoming_action: dict) -> int :
        """Change doing task's status

        Args:
            incoming_action (dict): Intent response dict.

        Returns:
            int: status code
        """
        if incoming_action is None :
            logger.warning("command is None.")
        
        current_active_tasks_json = db.get_current_task() or []
        
        calendar_tasks = calendar_service.get_calendar_events("task")
        
        prompt = STATE_CONTROLLER_PROMPT.format(current_active_tasks_json = current_active_tasks_json,
                                                 calendar_tasks = calendar_tasks,
                                                 incoming_action = incoming_action)
        result = self._clean_response(self.model.generate_content(prompt).text)
        
        if result :
            logger.info(f"Has changed specific task status.")
            return 200
        else :
            logger.error("Change status failed.")
            return 500

llm_client = LLMClient()