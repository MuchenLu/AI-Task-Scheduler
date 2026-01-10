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
        self.setStyleSheet(f"QMainWindow {{ background: {Colors.BACKGROUND}; border-radius: 20px; }}")
        
        self.size_set = {"record": (200, 200), "text": (350, 90), "task": (300, 600), "calendar": (600, 700)}
        
        self.setFixedSize(self.size_set["task"][0], self.size_set["task"][1])
        
        self.screen = QApplication.primaryScreen().availableGeometry()
        
        self.auto_fade_timer = QTimer(self)
        self.auto_fade_timer.setInterval(5000)
        self.auto_fade_timer.timeout.connect(self.fade_out)
        self.auto_fade_timer.setSingleShot(True) # 設為單次觸發，避免重複播放動畫
        
        self.text_input = TextInput(self)
        self.voice_button = VoiceButton(self)
        self.task_view = TaskView(parent=self)
        self.calendar_view = CalendarView(self)
        
        self.text_input.hide()
        self.voice_button.hide()
        self.task_view.show()
        self.calendar_view.hide()
        
        self.recorder = RecorderWorker()
        self.ai_processer = AIProcessorWorker()
        
        # Connect worker signals
        self.recorder.recorded.connect(self.process_audio)
        self.ai_processer.finished.connect(self.show_calendar_view)

        # Connect view signals
        self.calendar_view.choose_time.connect(self.handle_schedule_selection)
        self.text_input.input_content.connect(self.change_text_input)

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
        self.show_and_raise()
        
        self.voice_button.hide()
        self.task_view.hide()
        self.calendar_view.hide()
        
        if text :
            print(f"Processing text: {text}")
            self.ai_processer.set_var("text", text)
            self.ai_processer.start()
            self.text_input.clear()
            self.hide()
        else:
            self.setFixedSize(self.size_set["text"][0], self.size_set["text"][1])
            self.text_input.show()
            # 手動將輸入框置中
            self.text_input.move(
                (self.width() - self.text_input.width()) // 2,
                (self.height() - self.text_input.height()) // 2
            )
            self.text_input.setFocus()
            self.move_to_corner()

    def change_voice_button(self):
        self.reset()
        self.show_and_raise()
        self.text_input.hide()
        self.task_view.hide()
        self.calendar_view.hide()

        if not self.recorder.isRunning(): 
            self.auto_fade_timer.stop()
            self.setFixedSize(self.size_set["record"][0], self.size_set["record"][1])
            self.voice_button.show()
            # 手動將錄音按鈕置中
            self.voice_button.move(
                (self.width() - self.voice_button.width()) // 2,
                (self.height() - self.voice_button.height()) // 2
            )
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
        self.show_and_raise()
        self.text_input.hide()
        self.voice_button.hide()
        self.calendar_view.hide()
        
        self.setFixedSize(self.size_set["task"][0], self.size_set["task"][1])
        self.task_view.update(db.get_current_task())
        self.task_view.show()
        self.move_to_corner()

    def process_audio(self, audio_path):
        """Process the recorded audio file."""
        print(f"Processing audio at: {audio_path}")
        self.ai_processer.set_var("audio", audio_path)
        self.ai_processer.start()
        self.hide()

    def show_calendar_view(self):
        """顯示日曆視圖，並根據內容動態調整大小。"""
        self.reset()
        self.text_input.hide()
        self.voice_button.hide()
        self.task_view.hide()

        # 確保 CalendarView 已經更新內容
        self.calendar_view.show()
        
        # 強制佈局即時計算
        self.calendar_view.layout.activate()
        content_size = self.calendar_view.layout.sizeHint()

        # 計算合理的視窗大小 (給予邊距緩衝)
        new_width = min(content_size.width() + 40, self.screen.width() - 100)
        new_height = min(content_size.height() + 60, self.screen.height() - 100)
        
        # 限制最小與最大範圍，避免視窗太小或太大
        self.setFixedSize(max(400, new_width), max(300, new_height))
        self.calendar_view.setFixedSize(self.width(), self.height())
        
        self.move_to_corner()

    def handle_schedule_selection(self, schedule):
        """Handle the user's choice of a schedule."""
        print(f"User selected schedule: {schedule}")
        self.change_task()

    def closeEvent(self, event):
        """Ensure hotkeys are unhooked on application close."""
        keyboard.unhook_all_hotkeys()
        super().closeEvent(event)

    def reset(self):
        # 停止任何可能正在進行的淡出動畫，避免視窗在不該消失時消失
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        self.setWindowOpacity(0.95)
        if self.isHidden():
            self.show()
            
        self.auto_fade_timer.start()

    def fade_out(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(10000)
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

    def show_and_raise(self):
        """
        一個更可靠的方法來顯示視窗、將其置於頂層並啟用。
        """
        # 停止任何可能正在進行的淡出動畫
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()
        
        # 重設透明度、顯示視窗（如果已隱藏）並重啟計時器
        self.reset()
        
        # 這是個在很多情況下都有效的技巧，用來強制將視窗帶到前景。
        # 我們先取消 AlwaysOnTop，再重新設定它，這會觸發視窗管理器重新評估其層級。
        current_flags = self.windowFlags()
        self.setWindowFlags(current_flags & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show() # 應用 flag 變更
        self.setWindowFlags(current_flags | Qt.WindowType.WindowStaysOnTopHint)
        self.show() # 再次 show() 以確保 flag 生效並將視窗置頂
        
        # 最後再呼叫 activateWindow() 來取得焦點
        self.activateWindow()