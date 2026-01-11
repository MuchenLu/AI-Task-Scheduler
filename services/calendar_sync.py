import os
import datetime
import pytz
from typing import Literal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import config, ROOT_DIR
from utils.logger import logger

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = ROOT_DIR / "token.json"
CREDENTIALS_PATH = ROOT_DIR / "credentials.json"

class CalendarService :
    def __init__(self):
        creds = None
        try:
            if os.path.exists(TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Reload token...")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_PATH):
                        logger.critical(f"Credentials file not found.")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_PATH), SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                with open(TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())

            self.service = build("calendar", "v3", credentials=creds)
            logger.info("Google Calendar build success.")
        except Exception as e :
            logger.critical(f"Google Calendar build failed.")
            return False
    
    def get_calendar_events(self, calendar_id: Literal["all", "personal", "school", "task"], start: str = datetime.datetime.now(pytz.timezone('Asia/Taipei')).replace(hour=0, minute=0, second=0).isoformat(timespec = "seconds"), end: str = (datetime.datetime.now(pytz.timezone('Asia/Taipei')) + datetime.timedelta(days=7)).replace(hour=23, minute=59, second=59).isoformat(timespec = "seconds")) -> list :
        """Get specific time spec events.

        Args:
            calendar_id (str): Choose which calendar to get events.
            start (str, optional): Set the start time to get calendar events. Defaults to today.
            end (str, optional): Set when to stop getting calendar events. Defaults to 7 days later.
        Returns:
            list: return a single list of all events from the specified calendars.
        """
        # 防錯增強：確保 start/end 包含時區，否則 Google API 會回傳 400 Bad Request。
        # 之前的 strptime 檢查不正確，因為它無法處理時區，所以移除。
        if start and isinstance(start, str) and "+" not in start and "Z" not in start:
            logger.warning(f"Start time '{start}' is missing timezone. Appending +08:00.")
            start += "+08:00"
        if end and isinstance(end, str) and "+" not in end and "Z" not in end:
            logger.warning(f"End time '{end}' is missing timezone. Appending +08:00.")
            end += "+08:00"

        all_events = []
        calendar_ids_to_fetch = (False, False, False) # (personal, school, task)
        match calendar_id:
            case "all":
                calendar_ids_to_fetch = (True, True, True)
            case "personal":
                calendar_ids_to_fetch = (True, False, False)
            case "school":
                calendar_ids_to_fetch = (False, True, False)
            case "task":
                calendar_ids_to_fetch = (False, False, True)

        if calendar_ids_to_fetch[0]:
            try:
                personal_events = self.service.events().list(calendarId=config.PERSONAL_CALENDAR, timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime", eventTypes=["default"]).execute().get("items", [])
                for event in personal_events: event['type'] = 'personal'
                all_events.extend(personal_events)
                logger.info(f"Successfully fetched {len(personal_events)} events from 'personal' calendar.")
            except HttpError as e:
                logger.error(f"An HTTP error occurred when fetching 'personal' calendar: {e}")
            except Exception as e:
                logger.error(f"A general error occurred when fetching 'personal' calendar: {e}")

        if calendar_ids_to_fetch[1]:
            try:
                school_events = self.service.events().list(calendarId=config.SCHOOL_CALENDAR, timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime", eventTypes=["default"]).execute().get("items", [])
                for event in school_events: event['type'] = 'school'
                all_events.extend(school_events)
                logger.info(f"Successfully fetched {len(school_events)} events from 'school' calendar.")
            except HttpError as e:
                logger.error(f"An HTTP error occurred when fetching 'school' calendar: {e}")
            except Exception as e:
                logger.error(f"A general error occurred when fetching 'school' calendar: {e}")

        if calendar_ids_to_fetch[2]:
            try:
                task_events = self.service.events().list(calendarId=config.TASK_CALENDAR, timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime", eventTypes=["default"]).execute().get("items", [])
                for event in task_events: event['type'] = 'task'
                all_events.extend(task_events)
                logger.info(f"Successfully fetched {len(task_events)} events from 'task' calendar.")
            except HttpError as e:
                logger.error(f"An HTTP error occurred when fetching 'task' calendar: {e}")
            except Exception as e:
                logger.error(f"A general error occurred when fetching 'task' calendar: {e}")
        
        return all_events
    
    def add_event(self, calendar_id: Literal["personal", "school", "task"], event: dict) -> int :
        """Add events to assign calendar.

        Args:
            calendar_id (str): Choose which calendar too ad event.
            event (dict): Event data.

        Returns:
            int: Status code.
        """
        event["reminders"] = {"useDefault": False, "overrides": [{"method": "popup", "minutes": 0}]}
        
        target_calendar_id = None
        match calendar_id:
            case "personal":
                target_calendar_id = config.PERSONAL_CALENDAR
            case "school":
                target_calendar_id = config.SCHOOL_CALENDAR
            case "task":
                target_calendar_id = config.TASK_CALENDAR
        
        try :
            self.service.events().insert(calendarId=target_calendar_id, body=event).execute()
            logger.info("Add event success.")
            return 200
        except Exception as e :
            logger.error(f"Add event failed: {e}")
            return 500
        
calendar_service = CalendarService()