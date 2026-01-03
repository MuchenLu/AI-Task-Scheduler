import os
import datetime
import pytz
from typing import Literal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
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
    
    def get_calendar_events(self, calendar_id: Literal["all", "personal", "school", "task"], start: str = datetime.datetime.now(pytz.timezone('Asia/Taipei')).replace(hour=0, minute=0, second=0).isoformat(timespec = "seconds"), end: str = (datetime.datetime.now(pytz.timezone('Asia/Taipei')) + datetime.timedelta(days=7)).replace(hour=23, minute=59, second=59).isoformat(timespec = "seconds")) -> tuple :
        """Get specific time spec events.

        Args:
            calendar_id (str): Choose which calendar to get events.
            start (str, optional): Set the start time to get calendar events. Defaults to today.
            end (str, optional): Set when to stop getting calendar events. Defaults to 7 days later.
        Returns:
            tuple: return events like (personal events, school events, task events)
        """
        try :
            datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        except :
            logger.warning(f"Start time format wrong: {start}")
        
        try :
            datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
        except :
            logger.warning(f"End time format wrong: {end}")
        
        personal_events = []
        school_events = []
        task_events = []
        match calendar_id :
            case "all" :
                calendar_ids = (True, True, True)
            case "personal" :
                calendar_ids = (True, False, False)
            case "school" :
                calendar_ids = (False, True, False)
            case "task" :
                calendar_ids = (False, False, True)
        
        if calendar_ids[0] :
            try :
                personal_events = self.service.events().list(calendarId = config.PERSONAL_CALENDAR,
                                                            timeMin = start,
                                                            timeMax = end,
                                                            singleEvents = True,
                                                            orderBy = "startTime").execute().get("items", [])
            except :
                logger.warning("Get personal events failed.")
        if calendar_ids[1] :
            try :
                school_events = self.service.events().list(calendarId = config.SCHOOL_CALENDAR,
                                                            timeMin = start,
                                                            timeMax = end,
                                                            singleEvents = True,
                                                            orderBy = "startTime").execute().get("items", [])
            except :
                logger.warning("Get school events failed.")
        if calendar_ids[2] :
            try :
                task_events = self.service.events().list(calendarId = config.TASK_CALENDAR,
                                                        timeMin = start,
                                                        timeMax = end,
                                                        singleEvents = True,
                                                        orderBy = "startTime").execute().get("items", [])
            except :
                logger.warning("Get task events failed.")
        
        return (personal_events, school_events, task_events)
    
    def add_event(self, calendar_id: Literal["personal", "school", "task"], event: dict) -> int :
        """Add events to assign calendar.

        Args:
            calendar_id (str): Choose which calendar too ad event.
            event (dict): Event data.

        Returns:
            int: Status code.
        """
        event["reminders"] = {"useDefault": False, "overrides": [{"method": "popup", "minutes": 0}]}
        match calendar_id :
            case "personal" :
                calendar_id = config.PERSONAL_CALENDAR
            case "school" :
                calendar_id = config.SCHOOL_CALENDAR
            case "task" :
                calendar_id = config.TASK_CALENDAR
        
        try :
            self.service.events().insert(calendarId = calendar_id, body = event).execute()
            logger.info("Add event success.")
            return 200
        except Exception as e :
            logger.error(f"Add event failed: {e}")
            return 500
        
calendar_service = CalendarService()