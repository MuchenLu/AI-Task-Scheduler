import datetime
from PyQt6.QtCore import QObject, pyqtSignal
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
                        schedule_list = []
                        for key, value in recommendations.items():
                            new_schedule = value.copy()
                            new_schedule['type'] = 'suggest'
                            new_schedule['text'] = new_schedule.get('summary', '無摘要')
                            schedule_list.append(new_schedule)

                        # --- 關鍵修正：確保抓取範圍包含完整日期與台灣時區 ---
                        due_date = content.get("due_date")
                        fetch_start = None
                        fetch_end = None
                        
                        if due_date:
                            # 統一格式為 YYYY-MM-DD
                            base_date = due_date[:10]
                            # 抓取該日 00:00 到 23:59，並補上時區 +08:00
                            fetch_start = f"{base_date}T00:00:00+08:00"
                            fetch_end = f"{base_date}T23:59:59+08:00"
                        
                        # 抓取 Google 日曆事件（包含個人與學校等所有日曆）
                        events_tuple = calendar_service.get_calendar_events(
                            "all", 
                            start=fetch_start, 
                            end=fetch_end
                        )

                        # 處理抓回來的固定行程
                        for event_list in events_tuple:
                            if not event_list: continue
                            for event in event_list:
                                # 僅顯示具有具體時間的事件 (排除全天事件)
                                if 'dateTime' in event.get('start', {}): 
                                    schedule_list.append({
                                        'text': event.get('summary', '無標題'),
                                        'start': event['start'],
                                        'end': event['end'],
                                        'type': 'fixed'
                                    })
                        
                        logger.info(f"發送行程列表，共 {len(schedule_list)} 個事件")
                        self.task_info.emit(schedule_list)
                    elif response and response.get("reason"):
                        self.error_info.emit(response.get("reason"))
                    else:
                        self.error_info.emit("無法新增任務，請稍後再試")

                case "START_TASK":
                    response = db.get_current_task()
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
                    response = db.get_current_task()
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
                    response = db.get_current_task()
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
                    response = db.get_current_task()
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
                    subtasks = db.get_current_task()
                    self.user_msg.emit(str(subtasks))

task_state_manager = TaskStateManager()