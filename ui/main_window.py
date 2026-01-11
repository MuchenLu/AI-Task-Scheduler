from ui.components.text_input import TextInput
from ui.components.voice_button import VoiceButton
from ui.styles import Colors
from ui.views.task_view import TaskView
from ui.views.calendar_view import CalendarView
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal # 記得引入 pyqtSignal
from ui.workers import RecorderWorker, AIProcessorWorker
import keyboard
from core.state_machine import task_state_manager
from config import config
from services.calendar_sync import calendar_service
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
        self.setStyleSheet("QMainWindow { background: transparent; }")
        
        # 增加一個狀態旗標，判斷當前是否處於需要使用者互動的模式
        self.is_interactive = False
        
        self.size_set = {"record": (200, 200), "text": (350, 90), "task": (300, 600), "calendar": (600, 700)}
        
        self.setFixedSize(self.size_set["task"][0], self.size_set["task"][1])
        
        self.screen = QApplication.primaryScreen().availableGeometry()
        
        self.auto_fade_timer = QTimer(self)
        self.auto_fade_timer.setInterval(5000)
        self.auto_fade_timer.timeout.connect(self.fade_out)
        self.auto_fade_timer.setSingleShot(True) # 設為單次觸發，避免重複播放動畫
        
        self.text_input = TextInput(self)
        self.task_view = TaskView(parent=self)
        self.calendar_view = CalendarView(self)

        # 為語音模式建立一個專用的背景視圖
        self.voice_view = QFrame(self)
        self.voice_view.setFixedSize(self.size_set["record"][0], self.size_set["record"][1])
        self.voice_view.setStyleSheet(f"QFrame {{ background: {Colors.BACKGROUND}; border-radius: 20px; }}")
        self.voice_button = VoiceButton(self.voice_view) # 將 voice_view 設為父元件
        
        self.text_input.hide()
        self.voice_view.hide()
        self.task_view.show()
        self.calendar_view.hide()
        
        self.recorder = RecorderWorker()
        self.ai_processer = AIProcessorWorker()
        
        # Connect worker signals
        self.recorder.recorded.connect(self.process_audio)
        self.ai_processer.started.connect(self.hide)

        # Connect view signals
        self.calendar_view.choose_time.connect(self.handle_schedule_selection)
        self.text_input.input_content.connect(self.change_text_input)

        # Connect state manager signals
        task_state_manager.show_calendar_signal.connect(self.show_calendar_view)
        task_state_manager.error_info.connect(self.show_error_message)
        # 核心修正：當收到一般使用者訊息時 (例如 "任務已開始")，直接切換回任務列表。
        # 這樣可以確保介面在非同步操作完成後，回到一個穩定的狀態。
        task_state_manager.user_msg.connect(self.change_task)

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
        
        self.voice_view.hide()
        self.task_view.hide()
        self.calendar_view.hide()
        
        if text :
            self.ai_processer.set_var("text", text)
            self.ai_processer.start()
            self.text_input.clear()
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
        # 如果還沒開始錄音，代表即將進入互動模式
        # 如果正在錄音，代表即將結束互動
        self.is_interactive = not self.recorder.isRunning()

        self.reset()
        self.show_and_raise()
        self.text_input.hide()
        self.voice_view.hide()
        self.task_view.hide()
        self.calendar_view.hide()


        if not self.recorder.isRunning(): 
            self.setFixedSize(self.size_set["record"][0], self.size_set["record"][1])
            self.voice_view.show()
            # 手動將錄音按鈕置中
            self.voice_button.move(
                (self.voice_view.width() - self.voice_button.width()) // 2,
                (self.voice_view.height() - self.voice_button.height()) // 2
            )
            self.voice_button.start_anim()
            self.recorder.start()
            self.move_to_corner()
        else:
            self.recorder.stop()
            self.voice_button.stop_anim()
            self.voice_view.hide()
            # 互動結束，手動觸發一次 reset 來啟動計時器
            self.reset()

    def change_task(self):
        # 任務列表是純顯示，屬於非互動模式
        self.is_interactive = False
        self.reset()
        self.show_and_raise()
        self.text_input.hide()
        self.voice_view.hide()
        self.calendar_view.hide()
        
        self.setFixedSize(self.size_set["task"][0], self.size_set["task"][1])
        self.task_view.update(db.get_current_task())
        self.task_view.show()
        self.move_to_corner()

    def process_audio(self, audio_path):
        """Process the recorded audio file."""
        self.ai_processer.set_var("audio", audio_path)
        self.ai_processer.start()

    def show_calendar_view(self):
        """顯示日曆視圖，並根據內容動態調整大小。"""
        # 日曆視圖需要使用者選擇，屬於互動模式
        self.is_interactive = True

        self.reset()
        self.text_input.hide()
        self.voice_view.hide()
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

    def show_error_message(self, message: str):
        """顯示一個錯誤訊息對話框，並切換回任務視圖"""
        self.show_and_raise() # 確保主視窗可見，以作為訊息框的父元件
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("AI 處理錯誤")
        msg_box.setInformativeText(message)
        msg_box.setWindowTitle("錯誤")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        # 顯示錯誤後，切換回任務列表，避免卡在空白畫面
        self.change_task()

    def handle_schedule_selection(self, schedule):
        """處理使用者選擇的排程，將其新增至日曆並更新視圖。"""
        print(f"使用者選擇的排程: {schedule}")

        calendar_id = 'task'
        # 根據選擇的排程準備 Google Calendar API 的事件主體。
        event_body = {
            "summary": schedule['text'],
            "start": schedule['start'],
            "end": schedule['end']
        }

        # 使用 calendar_service 新增事件。
        status_code = calendar_service.add_event(
            calendar_id=calendar_id,
            event=event_body
        )

        if status_code == 200:
            print(f"成功將事件 '{event_body['summary']}' 新增至日曆 '{calendar_id}'。")
        else:
            print(f"新增事件至日曆失敗。狀態碼: {status_code}")

        # 最後，切換回任務視圖。
        self.is_interactive = False
        self.change_task()

    def closeEvent(self, event):
        """Ensure hotkeys are unhooked on application close."""
        keyboard.unhook_all_hotkeys()
        super().closeEvent(event)

    def reset(self):
        # 停止任何可能正在進行的淡出動畫，避免視窗在不該消失時消失
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        self.setWindowOpacity(1.0)
        if self.isHidden():
            self.show()
            
        # 根據互動旗標決定是否啟動或停止淡出計時器
        if self.is_interactive:
            self.auto_fade_timer.stop()
        else:
            self.auto_fade_timer.start()

    def fade_out(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(10000)
        self.animation.setStartValue(1.0)
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