import datetime
from utils.date_helpper import *

def test_convert_time_str_mode() :
    test_input = "2020/08/20 12:00"
    test_output = to_ISO8601(test_input, "str")
    assert test_output == "2020-08-20T12:00:00+08:00" and type(test_output) == str

def test_convert_time_datetime_mode() :
    test_input = "2020/08/20 12:00"
    test_output = to_ISO8601(test_input, "datetime")
    assert test_output == datetime.datetime(2020, 8, 20, 12, 0, 0, tzinfo = datetime.timezone(datetime.timedelta(hours = 8))) and type(test_output) == datetime.datetime

def test_set_to_start_str_mode() :
    test_input = "2020/08/20 12:00"
    test_output = set_to_start(test_input, "str")
    assert test_output == "2020-08-20T00:00:00+08:00" and type(test_output) == str

def test_set_to_start_datetime_mode() :
    test_input = "2020/08/20 12:00"
    test_output = set_to_start(test_input, "datetime")
    assert test_output == datetime.datetime(2020, 8, 20, 0, 0, 0, tzinfo = datetime.timezone(datetime.timedelta(hours = 8))) and type(test_output) == datetime.datetime

def test_set_to_end_str_mode() :
    test_input = "2020/08/20 12:00"
    test_output = set_to_end(test_input, "str")
    assert test_output == "2020-08-20T23:59:59+08:00" and type(test_output) == str

def test_set_to_end_datetime_mode() :
    test_input = "2020/08/20 12:00"
    test_output = set_to_end(test_input, "datetime")
    assert test_output == datetime.datetime(2020, 8, 20, 23, 59, 59, tzinfo = datetime.timezone(datetime.timedelta(hours = 8))) and type(test_output) == datetime.datetime

def test_before_week_str_mode() :
    test_input = "2020/08/20 12:00"
    test_output = datetime_before_week(test_input, "str")
    assert test_output == "2020-08-13T00:00:00+08:00" and type(test_output) == str

def test_before_week_datetime_mode() :
    test_input = "2020/08/20 12:00"
    test_output = datetime_before_week(test_input, "datetime")
    assert test_output == datetime.datetime(2020, 8, 13, 0, 0, 0, tzinfo = datetime.timezone(datetime.timedelta(hours = 8))) and type(test_output) == datetime.datetime

def test_after_week_str_mode() :
    test_input = "2020/08/20 12:00"
    test_output = datetime_after_week(test_input, "str")
    assert test_output == "2020-08-27T23:59:59+08:00" and type(test_output) == str

def test_after_week_datetime_mode() :
    test_input = "2020/08/20 12:00"
    test_output = datetime_after_week(test_input, "datetime")
    assert test_output == datetime.datetime(2020, 8, 27, 23, 59, 59, tzinfo = datetime.timezone(datetime.timedelta(hours = 8))) and type(test_output) == datetime.datetime