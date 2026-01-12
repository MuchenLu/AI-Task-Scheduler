import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from dateutil.parser import parse
import pytz
from config import config
import uuid
from utils.logger import logger
from data.db_manager import db
from services.llm_client import llm_client
from services.calendar_sync import calendar_service

class TaskStateManager(QObject) :
    task_info = pyqtSignal(list) # task info
    show_calendar_signal = pyqtSignal() # 顯示日曆的訊號
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
        
        # 1. 抓取 Google 日曆事件
        all_events = calendar_service.get_calendar_events("all", start=fetch_start, end=fetch_end)
        
        # 2. 關鍵修正：只有在「非」新增建議行程的模式下 (例如一般查詢)，才合併本地資料庫的任務。
        # 當使用者要新增任務時 (suggestions is not None)，我們只顯示 Google 日曆上的既有行程，
        # 避免本地端尚未同步的任務造成畫面混亂，讓使用者能根據最準確的日曆來做決策。
        if suggestions is None:
            local_tasks = db.get_current_task() or []
            for task in local_tasks:
                if task.get("status") != "COMPLETED":
                    schedule_list.append({
                        'text': f"[待辦] {task.get('summary')}",
                        'start': {'dateTime': task.get('start_time', fetch_start)},
                        'end': {'dateTime': task.get('due_date', fetch_end)},
                        'type': 'fixed' # 既有的任務視為固定
                    })
        
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
                        # 發送訊號，通知 UI 顯示日曆視圖
                        self.show_calendar_signal.emit()

                    elif response and response.get("reason"):
                        self.error_info.emit(response.get("reason"))
                    else:
                        self.error_info.emit("無法新增任務，請稍後再試")

                case "START_TASK" | "PAUSE_TASK" | "RESUME_TASK":
                    logger.info(f"Processing state change intent: {intent.get('intent')}")
                    
                    # AI 狀態控制器會處理所有邏輯，包括從 Google Calendar 查找任務
                    new_task_list = llm_client.change_status(intent)

                    if new_task_list is not None:
                        db.save_current_task(new_task_list)
                        logger.info(f"Successfully updated task status. New list: {new_task_list}")
                        
                        task_summary = intent.get("content", {}).get("summary", "未知任務")
                        match intent.get("intent"):
                            case "START_TASK":
                                self.user_msg.emit(f"任務 '{task_summary}' 已開始。")
                            case "PAUSE_TASK":
                                self.user_msg.emit(f"任務 '{task_summary}' 已暫停。")
                            case "RESUME_TASK":
                                self.user_msg.emit(f"任務 '{task_summary}' 已繼續。")
                                self.resume.emit()
                    else:
                        self.error_info.emit("AI 狀態控制器處理失敗，無法變更任務狀態。")

                case "COMPLETE_TASK":
                    logger.info(f"Processing state change intent: {intent.get('intent')}")
                    
                    # AI 狀態控制器會將任務標記為已完成
                    new_task_list_from_ai = llm_client.change_status(intent)

                    if new_task_list_from_ai is not None:
                        task_to_archive = None
                        # 在 AI 回傳的新列表中找到剛剛被標記為完成的任務
                        for task in new_task_list_from_ai:
                            if task.get("status") == "COMPLETED":
                                task_to_archive = task
                                break
                        
                        if task_to_archive:
                            # 歸檔已完成的任務
                            db.archive_task(task_to_archive)
                            
                            # 建立最終的當前任務列表 (移除已歸檔的任務)
                            final_task_list = [t for t in new_task_list_from_ai if t.get("task_id") != task_to_archive.get("task_id")]
                            db.save_current_task(final_task_list)
                            
                            self.complete_info.emit(task_to_archive)
                            self.user_msg.emit(f"任務 '{task_to_archive.get('summary')}' 已完成。")
                            logger.info(f"Task '{task_to_archive.get('summary')}' completed and archived.")
                        else:
                            # 這種情況不應該發生，但作為防錯，我們仍然儲存 AI 的狀態
                            db.save_current_task(new_task_list_from_ai)
                            logger.warning("AI processed COMPLETE_TASK but no task was marked as COMPLETED in the response.")
                            self.error_info.emit("無法確認完成的任務，但狀態已更新。")
                    else:
                        self.error_info.emit("AI 狀態控制器處理失敗，無法完成任務。")

                case "QUERY_TASK":
                    # 修正：使用者查詢時，除了回話，也要更新日曆視圖
                    self.fetch_and_emit_calendar() 
                    subtasks = db.get_current_task() or []
                    self.user_msg.emit("正在為您查詢今天的行程...")

task_state_manager = TaskStateManager()