import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from dateutil.parser import parse
import pytz
from config import config
from utils.logger import logger
from data.db_manager import db
from services.llm_client import llm_client
from services.calendar_sync import calendar_service

class TaskStateManager(QObject) :
    task_info = pyqtSignal(list) # task info
    pause_reason = pyqtSignal(str) # pause reason
    resume = pyqtSignal() # resume signal
    complete_info = pyqtSignal(dict) # complete info
    error_info = pyqtSignal(str) # error info
    user_msg = pyqtSignal(str) # user message
    calendar_temp = pyqtSignal(list)
    
    def __init__(self) :
        super().__init__()

    def fetch_and_emit_calendar(self, suggestions=None, target_date_str=None):
        """
        新增一個統一抓取並發送日曆資料的方法。
        它會抓取指定日期的既有行程，並可選擇性地合併傳入的建議行程。
        """
        schedule_list = suggestions if suggestions is not None else []
        
        # --- 核心修正：動態計算涵蓋所有相關日期的時間範圍 ---
        # 之前的邏輯只抓取單一目標日期的事件，導致其他日期的既有事件遺失。
        # 新邏輯會找出所有建議行程和目標日期，並抓取這個完整區間的所有事件。
        all_relevant_dates = []
        
        # 1. 從建議行程中提取日期
        for s in schedule_list:
            if s.get('type') == 'suggest' and 'dateTime' in s.get('start', {}):
                try:
                    dt = parse(s['start']['dateTime'])
                    all_relevant_dates.append(dt.date())
                except (ValueError, TypeError):
                    logger.warning(f"無法從建議行程中解析日期: {s}")
        
        # 2. 從目標日期字串中提取日期
        if target_date_str:
            try:
                target_date = parse(target_date_str).date()
                all_relevant_dates.append(target_date)
            except (ValueError, TypeError):
                logger.warning(f"無法解析目標日期字串: {target_date_str}")

        # 3. 決定抓取範圍
        if all_relevant_dates:
            min_date = min(all_relevant_dates)
            max_date = max(all_relevant_dates)
            fetch_start = datetime.datetime.combine(min_date, datetime.time.min).isoformat() + "+08:00"
            fetch_end = datetime.datetime.combine(max_date, datetime.time.max).isoformat() + "+08:00"
        else:
            # 如果沒有任何有效日期，則備援為抓取今天
            today = datetime.datetime.now(pytz.timezone('Asia/Taipei')).date()
            fetch_start = datetime.datetime.combine(today, datetime.time.min).isoformat() + "+08:00"
            fetch_end = datetime.datetime.combine(today, datetime.time.max).isoformat() + "+08:00"
        
        # 使用動態計算出的、更可靠的範圍來抓取 Google 日曆事件
        all_events = calendar_service.get_calendar_events("all", start=fetch_start, end=fetch_end)
        
        # A. 處理 Google 日曆事件 (相容全天事件)
        if all_events:
            for event in all_events:
                start_data = event.get('start', {})
                end_data = event.get('end', {})
                
                start_time = start_data.get('dateTime')
                end_time = end_data.get('dateTime')

                # 如果是全天事件，手動設定開始與結束時間
                if not start_time and 'date' in start_data:
                    start_date = start_data['date']
                    start_time = f"{start_date}T00:00:00+08:00"
                    end_time = f"{start_date}T23:59:59+08:00"

                if start_time and end_time:
                    schedule_list.append({
                        'text': event.get('summary', '無標題'),
                        'start': {'dateTime': start_time},
                        'end': {'dateTime': end_time},
                        'type': 'fixed'
                    })
        
        logger.info(f"發送行程列表，共 {len(schedule_list)} 個事件")
        self.task_info.emit(schedule_list)

    def process_voice(self, text: str):
        """處理使用者的語音或文字指令"""
        intents = llm_client.analyze_intent(text)

        if not intents:
            logger.error("Failed to analyze user intent or intent is empty.")
            self.error_info.emit("抱歉，我無法理解您的指令。")
            return

        for intent in intents:
            match intent.get("intent"):
                case "ADD_TASK":
                    content = intent.get("content")
                    response = llm_client.sugget_schedule(content)
                    if response and response.get("status") == "success":
                        # 獲取 AI 建議行程
                        recommendations = response.get("recommendations", {})
                        suggestions_list = []
                        for key, value in recommendations.items():
                            new_schedule = value.copy()
                            new_schedule['type'] = 'suggest'
                            new_schedule['text'] = new_schedule.get('summary', '無摘要')
                            suggestions_list.append(new_schedule)
                        
                        # 呼叫統一的方法，傳入建議行程與目標日期
                        self.fetch_and_emit_calendar(suggestions_list, content.get("due_date"))
                    elif response and response.get("reason"):
                        self.error_info.emit(response.get("reason"))
                    else:
                        self.error_info.emit("無法新增任務，請稍後再試")

                case "START_TASK":
                    response = db.get_current_task() or []
                    for task in response:
                        if task.get("status") == "IN_PROGRESS":
                            self.error_info.emit(f"目前已有 {task.get('task_name')} 進行中，無法開始新任務")
                            return
                    found = False
                    for task in response:
                        if intent.get("content").get("task_name") == task.get("task_name"):
                            task["status"] = "IN_PROGRESS"
                            found = True
                            break
                    if found:
                        self.user_msg.emit(f"{task['task_name']} 已開始")
                    else:
                        self.user_msg.emit("未找到任務")
                    db.save_current_task(response)

                case "PAUSE_TASK":
                    response = db.get_current_task() or []
                    found = False
                    for task in response:
                        if intent.get("content").get("task_name") == task.get("task_name"):
                            task["status"] = "PAUSED"
                            found = True
                            break
                    if found:
                        self.user_msg.emit(f"{task['task_name']} 已暫停")
                    else:
                        self.user_msg.emit("未找到任務")
                    db.save_current_task(response)

                case "RESUME_TASK":
                    response = db.get_current_task() or []
                    for task in response:
                        if task.get("status") == "IN_PROGRESS":
                            self.error_info.emit(f"目前已有 {task.get('task_name')} 進行中，無法恢復任務")
                            return
                    found = False
                    for task in response:
                        if intent.get("content").get("task_name") == task.get("task_name"):
                            task["status"] = "IN_PROGRESS"
                            found = True
                            break
                    if found:
                        self.user_msg.emit(f"{task['task_name']} 已恢復")
                        db.save_current_task(response)
                        self.resume.emit()
                    else:
                        self.user_msg.emit("未找到任務")

                case "COMPLETE_TASK":
                    response = db.get_current_task() or []
                    for task in response:
                        if intent.get("content").get("task_name") == task.get("task_name"):
                            task["status"] = "COMPLETED"
                            task["end_time"] = datetime.datetime.now().isoformat()
                            db.archive_task()
                            response.remove(task)
                            db.save_current_task(response)
                            self.complete_info.emit(task)
                            self.user_msg.emit(f"任務完成：{task['task_name']}")
                            break

                case "QUERY_TASK":
                    # 修正：使用者查詢時，除了回話，也要更新日曆視圖
                    self.fetch_and_emit_calendar() 
                    subtasks = db.get_current_task() or []
                    self.user_msg.emit("正在為您查詢今天的行程...")

task_state_manager = TaskStateManager()