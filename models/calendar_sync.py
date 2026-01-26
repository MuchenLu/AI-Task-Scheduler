'''
./models/calendar.sync.py
模組功能：
1. 驗證 Google Calendar ID
2. 取得 calendar events
3. 新增 calendar events
4. 更新 calendar events
5. 刪除 calendar events
'''
import os
import datetime
import pytz
from ast import literal_eval
from typing import Literal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from utils.logger import logger
from utils.date_helpper import *
from config.config import TOKEN_JSON, CREDENTIALS_JSON

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService :
    def __init__(self):
        creds = None
        try:
            if os.path.exists(TOKEN_JSON):
                creds = Credentials.from_authorized_user_file(str(TOKEN_JSON), SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Reload token...")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_JSON):
                        logger.critical(f"未找到驗證憑證")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_JSON), SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                with open(TOKEN_JSON, "w") as token:
                    token.write(creds.to_json())

            self.service = build("calendar", "v3", credentials=creds)
            logger.info("Google Calendar 服務啟動成功")
        except Exception as e :
            logger.critical(f"Google Calendar 初始化失敗: {e}")
            self.service = None
    
    def valiadate_calendar(self, calendar_id: str) -> int :
        """用於驗證 calendar id 是否存在且可取得

        Args:
            calendar_id (str): 傳入的 calendar id

        Returns:
            int: 狀態碼
        """
        try :
            calendar_meta = self.service.calendars().get(calendarId = calendar_id).execute()
            return 200
        except HttpError as e :
            return e.resp.status
    
    def get_calendar_events(self, start_time: str = datetime_before_week(datetime.datetime.now(), "str"), end_time: str = datetime_after_week(datetime.datetime.now(), "str")) -> list :
        """用於取得指定時間的所有 calendar events

        Args:
            start_time (str, optional): 設定起始日期時間. 預設為一星期前的 00:00:00
            end_time (str, optional): 設定截止日期時間. 預設為一星期後的 23:59:00

        Returns:
            list: 期間內完整的 calendar events
        """
        total_events = []
        try :
            for calendar_id in literal_eval(os.getenv("GOOGLE_CALENDAR_ID")) :
                events = self.service.events().list(calendarId = calendar_id, timeMin = start_time, timeMax = end_time, singleEvents = True, eventTypes = ["default"], orderBy = "startTime").execute().get("items", [])
                total_events.extend(events)
            total_events.sort(key = lambda x : x["start"]["dateTime"])
            return total_events
        except Exception as e :
            raise Exception(f"取得 calendar events 出錯: {e}")
    
    def add_calendar_event(self, task_content: dict) :
        """新增 Google Calendar 事件，並添上私人屬性

        Args:
            task_content (dict): 包含 summary, start 以及 end 的任務內容
        """
        # NOTE: 確認內容正確度
        if not all(key in task_content for key in ["summary", "start", "end", "extendProperties"]) :
            raise Exception(f"新增事件格式錯誤: {task_content}")
        
        task_content["reminders"] = {"useDefault": False, "overrides": [{"method": "popup", "minutes": 0}]}
        try :
            self.service.events().insert(calendarId = os.getenv("TASK_CALENDAR"), body = task_content).execute()
            logger.info("新增事件成功")
        except Exception as e :
            raise Exception(f"新增事件失敗: {e}")
    
calendar = CalendarService()