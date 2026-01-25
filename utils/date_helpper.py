from dateutil import relativedelta, parser
import datetime
import pytz
from typing import Literal

def to_ISO8601(date_time: str | datetime.datetime, return_type: Literal["str", "datetime"]) -> str | datetime.datetime :
    """將任意格式日期時間轉換為 ISO8601 格式

    Args:
        date_time (str | datetime): 欲轉換的日期時間，可接受字串或 datetime 物件
        return_type ("str" | "datetime"): 選擇回傳型態

    Raises:
        Exception: 日期時間格式混亂錯誤

    Returns:
        str | datetime: 轉換完成的日期時間
    """
    if isinstance(date_time, datetime.datetime) :
        date_time = str(date_time)
    try :
        dt = parser.parse(date_time, fuzzy = True)
        if dt.tzinfo is None :
            dt = dt.astimezone()
        if return_type == "datetime" :
            return dt
        else :
            return dt.isoformat(timespec = "seconds")
    except (ValueError, TypeError) :
        raise Exception(f"日期時間格式過於混亂或錯誤，無法自動解析: {date_time}")

def set_to_start(now: str | datetime.datetime, return_type: Literal["str", "datetime"]) -> str | datetime.datetime :
    """將時間設置為 00:00:00

    Args:
        now (str | datetime): 現在日期時間，可接受字串或 datetime 物件
        return_type ("str" | "datetime"): 選擇回傳型態

    Returns:
        str | datetime: 設定完成的日期時間
    """
    if isinstance(now, str) :
        now = datetime.datetime.fromisoformat(to_ISO8601(now, "str"))
    
    start = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    start = to_ISO8601(start, "datetime")
    if return_type == "datetime" :
        return start
    else :
        return start.isoformat(timespec = "seconds")

def set_to_end(now: str | datetime.datetime, return_type: Literal["str", "datetime"]) -> str | datetime.datetime :
    """將時間設置為 23:59:59

    Args:
        now (str | datetime): 欲轉換的日期時間，可接受字串或 datetime 物件
        return_type ("str", "datetime"): 選擇回傳型態

    Returns:
        str | datetime.datetime: 設定完成的日期時間
    """
    if isinstance(now, str) :
        now = datetime.datetime.fromisoformat(to_ISO8601(now, "str"))
    
    end = now.replace(hour = 23, minute = 59, second = 59, microsecond = 0)
    end = to_ISO8601(end, "datetime")
    if return_type == "datetime" :
        return end
    else :
        return end.isoformat(timespec = "seconds")

def datetime_before_week(now: str | datetime.datetime, return_type: Literal["str", "datetime"]) -> str | datetime.datetime :
    """將日期時間設定為一星期前的 00:00:00

    Args:
        now (str | datetime): 欲轉換的時間日期，可接受字串或 datetime 物件
        return_type ("str" | "datetime"): 選擇回傳型態

    Returns:
        str | datetime: 設定完成的日期時間
    """
    if isinstance(now, str) :
        now = datetime.datetime.fromisoformat(to_ISO8601(now, "str"))
    
    before = now - relativedelta.relativedelta(weeks = 1)
    before = set_to_start(before, "datetime")
    if return_type == "datetime" :
        return before
    else :
        return before.isoformat(timespec = "seconds")

def datetime_after_week(now: str | datetime.datetime, return_type: Literal["str", "datetime"]) -> str | datetime.datetime :
    """將日期時間設定為一星期後的 23:59:00

    Args:
        now (str | datetime.datetime): 欲轉換的時間日期，可接受字串或 datetime 物件
        return_type ("str" | "datetime"): 選擇回傳型態

    Returns:
        str | datetime: 設定完成的日期時間
    """
    if isinstance(now, str) :
        now = datetime.datetime.fromisoformat(to_ISO8601(now, "str"))
    
    after = now + relativedelta.relativedelta(weeks = 1)
    after = set_to_end(after, "datetime")
    if return_type == "datetime" :
        return after
    else :
        return after.isoformat(timespec = "seconds")