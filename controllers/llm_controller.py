'''
./controllers/llm_controller.py
模組功能：
1. 串接前端輸入及 AI 處理
'''

from PyQt6.QtCore import QObject, pyqtSignal
from models.llm_client import llm
from utils.logger import logger

class Signal(QObject) :
    proccesing = pyqtSignal(bool, str) # NOTE: 處理是否成功 / 處理階段
    schedule = pyqtSignal(list, list) # NOTE AI 排程完畢之推薦時間、原有日程內容
    backup = pyqtSignal(str)

# TODO: 結合 loading 發信號
class LLMController() :
    def __init__(self) :
        self.signal = Signal()
        self.llm = llm
    
    def start_processing(self, user_input: str) :
        logger.debug(f"AI 開始處理指令: {user_input}")
        try :
            user_intents = self.llm.analyze_intent(user_input)
            logger.debug(str(user_intents))
        except Exception as e :
            logger.error(f"AI 分析出錯: {e}")
            self.signal.proccesing.emit(False, "AI 分析意圖錯誤")
            self.signal.backup.emit(user_input)
            return
        self.signal.proccesing.emit(True, "AI 意圖分析完成")
        add_task_content = []
        change_task_content = []
        for intent in user_intents :
            if intent["intent"] == "ADD_TASK" :
                add_task_content.append(intent)
            elif intent["intent"] == "CHANGE_TASK_STATUS" :
                change_task_content.append(intent)
            elif intent["intent"] == "START_TASK" :
                change_task_content.append(intent)
        if add_task_content :
            try :
                decomposition_result = self.llm.decomposition_task(add_task_content)
                logger.debug(str(decomposition_result))
            except Exception as e :
                logger.error(f"AI 拆解出錯: {e}")
                self.signal.proccesing.emit(False, "AI 拆解錯誤")
                self.signal.backup.emit(user_input)
                return
            self.signal.proccesing.emit(True, "AI 拆解完成")
            try :
                suggets_schedule, fixed_event = self.llm.suggest_schedule(decomposition_result)
                logger.debug(str(suggets_schedule))
            except Exception as e :
                logger.error(f"AI 時間推薦出錯: {e}")
                self.signal.proccesing.emit(False, "AI 推薦時間失敗")
                self.signal.backup.emit(user_input)
                return
            self.signal.proccesing.emit(True, "AI 推薦時間完成")
            self.signal.schedule.emit(suggets_schedule["recommendations"], fixed_event)
            # TODO: on 行事曆
        if change_task_content :
            try :
                self.llm.change_state(change_task_content)
                logger.debug(str(change_task_content))
            except Exception as e :
                logger.error(f"AI 更新狀態出錯: {e}")
                self.signal.proccesing.emit(False, "AI 更新狀態失敗")
                self.signal.backup.emit(user_input)
                return
            self.signal.proccesing.emit(True, "AI 更新狀態完成")

llm_controller = LLMController()