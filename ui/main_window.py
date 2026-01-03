from ui.components.text_input import TextInput
from ui.components.voice_button import VoiceButton
from ui.styles import Colors
from ui.views.task_view import TaskView
from ui.views.calendar_view import CalendarView
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal # 記得引入 pyqtSignal
from ui.workers import RecorderWorker, AIProcessorWorker
import keyboard
from core.state_machine import task_state_manager
from data.db_manager import db

class MainWindow(QMainWindow):
    sig_hotkey_voice = pyqtSignal()
    sig_hotkey_text = pyqtSignal()
    sig_hotkey_task = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sched AI")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool) # 加上 Tool 可以避免在工作列佔位(看需求)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)
        self.setStyleSheet(Colors.BACKGROUND)
        
        self.size_set = {"record": (200, 200), "text": (350, 90), "task": (300, 600), "calendar": (600, 700)}
        
        self.setFixedSize(self.size_set["task"][0], self.size_set["task"][1])
        
        self.screen = QApplication.primaryScreen().availableGeometry()
        
        self.auto_fade_timer = QTimer(self)
        self.auto_fade_timer.setInterval(5000)
        self.auto_fade_timer.timeout.connect(self.fade_out)
        
        self.text_input = TextInput(self)
        self.voice_button = VoiceButton(self)
        self.task_view = TaskView(self)
        self.calendar_view = CalendarView(self)
        
        self.text_input.hide()
        self.voice_button.hide()
        self.task_view.show()
        
        self.recorder = RecorderWorker()
        self.ai_processer = AIProcessorWorker()
        
        # TODO: 記得在這裡連接 Worker 的 finished signal
        # self.recorder.finished.connect(...)
        # self.ai_processer.finished_signal.connect(...)

        self.sig_hotkey_voice.connect(self.change_voice_button)
        self.sig_hotkey_text.connect(self.change_text_input)
        self.sig_hotkey_task.connect(self.change_task)

        keyboard.add_hotkey("Alt+R", lambda: self.sig_hotkey_voice.emit())
        keyboard.add_hotkey("Alt+T", lambda: self.sig_hotkey_text.emit())
        keyboard.add_hotkey("Alt+A", lambda: self.sig_hotkey_task.emit())
        
        self.move_to_corner()

    def move_to_corner(self):
        self.move(self.screen.width() - self.width() - 20, self.screen.height() - self.height() - 20)

    def change_text_input(self, text=None):
        self.reset()
        
        self.voice_button.hide()
        self.task_view.hide()
        
        if text :
            print(f"Processing text: {text}")
            self.ai_processer.set_var("text", text)
            self.ai_processer.start()
            self.text_input.clear()
            self.hide()
        else:
            self.setFixedSize(self.size_set["text"][0], self.size_set["text"][1])
            self.text_input.show()
            self.text_input.setFocus()
            self.move_to_corner()

    def change_voice_button(self):
        self.reset()
        self.text_input.hide()
        self.task_view.hide()

        if not self.recorder.isRunning(): 
            self.auto_fade_timer.stop()
            self.setFixedSize(self.size_set["record"][0], self.size_set["record"][1])
            self.voice_button.show()
            self.voice_button.start_anim()
            self.recorder.start()
            self.move_to_corner()
        else:
            self.recorder.stop()
            self.voice_button.stop_anim()
            self.voice_button.hide()
            self.auto_fade_timer.start()

    def change_task(self):
        self.reset()
        self.text_input.hide()
        self.voice_button.hide()
        
        self.setFixedSize(self.size_set["task"][0], self.size_set["task"][1])
        self.task_view.update(db.get_current_task())
        self.task_view.show()
        self.move_to_corner()

    def reset(self):
        self.setWindowOpacity(0.95)
        if self.isHidden():
            self.show()
            
        self.auto_fade_timer.start()

    def fade_out(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0.95)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.finished.connect(self.hide)
        self.animation.start()

    def mouseMoveEvent(self, event):
        self.reset()
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        self.reset()
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        self.reset()
        super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        self.move_to_corner()
        super().resizeEvent(event)