import os
import datetime
import pytz
from typing import Literal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from utils.logger import logger
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
    
    def valiadate_calendar(self, calendar_id) -> int :
        try :
            calendar_meta = self.service.calendars().get(calendarId = calendar_id).execute()
            return 200
        except HttpError as e :
            return e.resp.status
        
calendar = CalendarService()