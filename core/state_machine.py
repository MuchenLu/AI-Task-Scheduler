import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from config import config
from utils.logger import logger
from data.db_manager import db
from services.llm_client import llm_client
from services.calendar_sync import calendar_service

class TaskStateManager(QObject) :
    task_info = pyqtSignal(dict) # task info
    pause_reason = pyqtSignal(str) # pause reason
    resume = pyqtSignal() # resume signal
    complete_info = pyqtSignal(dict) # complete info
    error_info = pyqtSignal(str) # error info
    user_msg = pyqtSignal(str) # user message
    
    def __init__(self) :
        super().__init__()
    
    def process_voice(self, text: str) :
        """Use to process user's command

        Args:
            text (str): Transcribe result.
        """
        intents = llm_client.analyze_intent(text)
        
        for intent in intents :
            match intent.get("intent") :
                case "ADD_TASK" :
                    response = llm_client.sugget_schedule(intent.get("content"))
                    if response :
                        self.task_info.emit(response)
                    else :
                        self.error_info.emit("無法新增任務，請稍後再試")
                case "START_TASK" :
                    response = db.get_current_task()
                    for task in response :
                        if task.get("status") == "IN_PROGRESS" :
                            self.error_info.emit(f"目前已有 {task.get('task_name')} 進行中，無法開始新任務")
                            logger.warning(f"目前已有 {task.get('task_name')} 進行中，無法開始新任務")
                            return
                    found = False
                    for task in response :
                        if intent.get("content").get("task_name") == task.get("task_name") :
                            task["status"] = "IN_PROGRESS"
                            found = True
                            break
                    if found :
                        self.user_msg.emit(f"{task['task_name']} 已開始")
                        logger.info(f"{task['task_name']} 已開始")
                    else :
                        self.user_msg.emit("未找到任務")
                        logger.warning("未找到任務")
                    db.save_current_task(response)
                case "PAUSE_TASK" :
                    response = db.get_current_task()
                    found = False
                    for task in response :
                        if intent.get("content").get("task_name") == task.get("task_name") :
                            task["status"] = "PAUSED"
                            found = True
                            break
                    if found :
                        self.user_msg.emit(f"{task['task_name']} 已暫停")
                        logger.info(f"{task['task_name']} 已暫停")
                    else :
                        self.user_msg.emit("未找到任務")
                        logger.warning("未找到任務")
                    db.save_current_task(response)
                case "RESUME_TASK" :
                    response = db.get_current_task()
                    for task in response :
                        if task.get("status") == "IN_PROGRESS" :
                            self.error_info.emit(f"目前已有 {task.get('task_name')} 進行中，無法恢復任務")
                            return # 記得要 return
                    
                    found = False
                    for task in response:
                        if intent.get("content").get("task_name") == task.get("task_name"):
                            task["status"] = "IN_PROGRESS"
                            found = True
                            break
                    
                    if found:
                        self.user_msg.emit(f"{task['task_name']} 已恢復")
                        db.save_current_task(response)
                        self.resume.emit() # 通知 UI
                    else:
                        self.user_msg.emit(f"未找到任務：{task['task_name']}")
                case "COMPLETE_TASK" :
                    response = db.get_current_task()
                    found = None
                    
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
                case "QUERY_TASK" :
                    subtasks = db.get_current_task()
                    self.user_msg.emit(subtasks)

task_state_manager = TaskStateManager()