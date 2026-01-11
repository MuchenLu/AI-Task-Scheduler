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
        if command is None :
            logger.warning("command is None.")
        
        now = datetime.datetime.now(pytz.timezone('Asia/Taipei')).isoformat(timespec = "seconds")
        calendar_events = calendar_service.get_calendar_events("all", end = command.get("due_date"))
        historical_logs = db.get_history(3)
        
        prompt = SCHEDULER_PROMPT.format(current_time = now,
                                         command = command,
                                         calendar_events = calendar_events,
                                         historical_logs = historical_logs)
        result = self._clean_response(self.model.generate_content(prompt).text)
        
        if result :
            logger.info(f"AI clean response: {result}")
        if result:
            # 如果 AI 回應中包含建議排程，則將原始指令中的 calendar_id 注入，
            # 以確保它能被傳遞到 UI 層進行選擇。
            if 'schedules' in result and 'calendar_id' in command:
                for schedule in result['schedules']:
                    schedule['calendar_id'] = command['calendar_id']
                logger.info(f"AI response with injected calendar_id: {result}")
            else:
                logger.info(f"AI clean response: {result}")
            return result
        else :
        else:
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
        existing_tasks_db = db.get_current_task()
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
        
        current_active_tasks_json = db.get_current_task()
        
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