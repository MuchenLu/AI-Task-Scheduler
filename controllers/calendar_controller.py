'''
./controllers/calendar_sync.py
模組功能：
1. 整理資料格式
'''
from models.calendar_sync import calendar
from utils.logger import logger

class CalendarController :
    def __init__(self) :
        self.calendar = calendar
    
    def add_task(self, task_content: dict) :
        """新增 Google Calendar 事件，並添上私人屬性

        Args:
            task_content (dict): 包含 summary, start 以及 end 的任務內容
        """
        event = {}
        event["summary"] = task_content["summary"]
        event["start"] = task_content["start"]
        event["end"] = task_content["end"]
        event["extendProperties"] = {"private": {"sign": "SCHEDAI"}}
        self.calendar.add_calendar_event(event)
        logger.info("新增事件成功")

calendar_controller = CalendarController()