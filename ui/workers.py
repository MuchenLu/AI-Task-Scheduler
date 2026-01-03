import time
from PyQt6.QtCore import QThread, pyqtSignal

from services.audio_manager import audio_manager
from core.state_machine import task_state_manager
from utils.logger import logger
from typing import Literal

class RecorderWorker(QThread) :
    recorded = pyqtSignal(str) # return file path
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
    
    def run(self) :
        self.is_recording = True
        audio_manager.start_recording()
        
        while self.is_recording :
            audio_manager.process_stream()
    
    def stop(self) :
        self.is_recording = False
        self.wait()
        
        file_path = audio_manager.stop_recording()
        if file_path :
            self.recorded.emit(file_path)
            logger.info(f"Record complete. File path: {file_path}")
        else :
            logger.warning("Record failed.")

class AIProcessorWorker(QThread) :
    finished = pyqtSignal() # complete signal
    
    def __init__(self) :
        super().__init__()
    
    def set_var(self, var_type: Literal["audio", "text"], var: str) :
        if var_type == "audio" :
            self.audio_path = var
        elif var_type == "text" :
            self.text = var
        
    
    def run(self) :
        logger.debug("start AI processor.")
        if self.audio_path :
            self.text = audio_manager.transcribe(self.audio_path)
        
        if self.text :
            task_state_manager.process_voice(self.text)
        else :
            task_state_manager.error_info.emit("Please repeat again.")
        
        self.audio_path = None
        self.text = None
        self.finished.emit()