import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from utils.logger import setup_logger, logger

ROOT_DIR = Path(__file__).parent.absolute()
load_dotenv(ROOT_DIR / ".env")

class Config :
    APP_NAME = "AI-Task-Manager"
    
    DATA_DIR = ROOT_DIR / "data"
    LOG_DIR = ROOT_DIR / "log"
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    setup_logger(LOG_DIR)
    
    # TODO: change to read env variables with no stable amount
    PERSONAL_CALENDAR = os.getenv("PERSONAL_CALENDAR", None)
    SCHOOL_CALENDAR = os.getenv("SCHOOL_CALENDAR", None)
    TASK_CALENDAR = os.getenv("TASK_CALENDAR", None)
    
    API_KEY = os.getenv("API_KEY", None)
    
    @classmethod
    def validate(cls) :
        # TODO: change to read env variables with no stable amount
        missings = []
        if cls.PERSONAL_CALENDAR is None :
            missings.append("PERSONAL_CALENDAR")
        if cls.SCHOOL_CALENDAR is None :
            missings.append("SCHOOL_CALENDAR")
        if cls.TASK_CALENDAR is None :
            missings.append("TASK_CALENDAR")
        if cls.API_KEY is None :
            missings.append("API_KEY")
        
        if missings :
            logger.critical(f"Missing environment variables: {', '.join(missings)}")
            return False
        
        logger.info("All required environment variables are set.")
        return True

config = Config()