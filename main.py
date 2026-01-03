import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from config import config
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon
from ui.workers import RecorderWorker, AIProcessorWorker
from core.state_machine import task_state_manager
from data.db_manager import db
from utils.logger import logger

class AITaskManagerApp :
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        if not config.validate() :
            logger.critical("Configuration validation failed. Exiting application.")
            sys.exit(1)
        
        self.window = MainWindow()
        self.tray = TrayIcon(self.window)
        
        self.recorder_worker = None
        self.ai_worker = None
        
        self._connect_signals()
        self.refresh_task_list()
        self.window.show()
        self.window.wake_up()
        self.tray.show()
        
    def _connect_signals(self) :
        self.window.signal_recording_start.connect(self.start_recording)
        self.window.signal_recording_stop.connect(self.stop_recording)
        self.window.signal_command_input.connect(self.handle_text_command)
        task_state_manager.user_msg.connect(self.on_ai_message)
        task_state_manager.resume.connect(self.refresh_task_list)
        task_state_manager.complete_info.connect(lambda x: self.refresh_task_list())
        task_state_manager.error_info.connect(self.on_ai_error)
    
    def start_recording(self):
        logger.info("Starting Recorder Worker...")
        self.recorder_worker = RecorderWorker()
        self.recorder_worker.recorded.connect(self.start_ai_processing)
        self.recorder_worker.start()
    
    def stop_recording(self):
        if self.recorder_worker:
            logger.info("Stopping Recorder Worker...")
            self.recorder_worker.stop()
    
    def start_ai_processing(self, audio_path):
        logger.info(f"Starting AI Processor with {audio_path}")
        self.window.set_status("thinking")
        self.ai_worker = AIProcessorWorker(audio_path)
        self.ai_worker.finished.connect(lambda: self.window.set_status("success"))
        self.ai_worker.finished.connect(self.refresh_task_list)
        self.ai_worker.start()
    
    def handle_text_command(self, text):
        logger.info(f"Processing text command: {text}")
        task_state_manager.process_voice(text)
        self.window.set_status("success")
        self.refresh_task_list()
    
    def refresh_task_list(self):
        tasks = db.get_current_task()
        if tasks is None:
            tasks = []
        logger.debug(f"Refreshing UI with {len(tasks)} tasks.")
        self.window.update_task_list(tasks)
    
    def on_ai_message(self, msg):
        logger.info(f"AI Message: {msg}")
        self.window.input_field.setPlaceholderText(str(msg))
        self.refresh_task_list()
    
    def on_ai_error(self, err_msg):
        logger.error(f"AI Error: {err_msg}")
        self.window.set_status("idle")
        self.window.input_field.setPlaceholderText(f"Error: {err_msg}")

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    task_app = AITaskManagerApp()
    task_app.run()