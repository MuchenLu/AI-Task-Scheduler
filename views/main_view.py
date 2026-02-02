'''
./views/main_view.py
視圖功能：
1. 串接所有 UI
2. 控制視窗位置、樣式、動畫等
'''
from typing import Literal
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QSizePolicy, QApplication, QWidget, QVBoxLayout, QLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QEvent, QEasingCurve
from PyQt6.QtGui import QWindow
from views.components.text_input import TextInput
from views.calendar_view import CalendarView
from controllers.llm_controller import llm_controller
from controllers.calendar_controller import calendar_controller
from utils.logger import logger

class MainWindow(QMainWindow) :
    def __init__(self) :
        super().__init__()
        self.fade_out = True
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(1.0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim.setDuration(5000)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.hide)
        
        self.stack = QStackedWidget()
        self.text_input = TextInput(self)
        self.calendar_view = CalendarView(self)
        
        self.stack.addWidget(self.text_input)
        self.stack.addWidget(self.calendar_view)
        self.setCentralWidget(self.stack)
        self.stack.setCurrentWidget(self.text_input)
        
        self.text_input.user_input.connect(llm_controller.start_processing)
        llm_controller.signal.proccesing.connect(self.loading)
        llm_controller.signal.schedule.connect(lambda suggest_time, fixed_events: self.change_view("calendar_view", suggest_time = suggest_time, fixed_events = fixed_events))
        llm_controller.signal.backup.connect(self.backup)
        self.calendar_view.choose_signal.connect(calendar_controller.add_task)
        self.calendar_view.choose_signal.connect(self.reset)
        
        self.widgets = {"text_input": self.text_input,
                        "calendar_view": self.calendar_view}
        
        self.text_input.installEventFilter(self)
        
        self.change_view("text_input")
        self.anim.start()
    
    def move_to_bottom_right(self) :
        screen = QApplication.primaryScreen()
        screen = screen.availableGeometry()
        margin = 20
        x = (screen.x() + screen.width()) - self.width() - margin
        y = (screen.y() + screen.height()) - self.height() - margin
        self.move(x, y)
    
    def resizeEvent(self, event) :
        print(self.width(), self.height())
        self.move_to_bottom_right()
        return super().resizeEvent(event)
    
    def eventFilter(self, obj, event) :
        if self.fade_out :
            if obj == self.text_input :
                if event.type() == QEvent.Type.FocusIn :
                    self.anim.stop()
                    self.setWindowOpacity(1.0)
                elif event.type() == QEvent.Type.FocusOut :
                    self.anim.start()
            
        return super().eventFilter(obj, event)
    
    def enterEvent(self, event):
        if self.fade_out:
            self.anim.stop()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if self.fade_out:
            self.anim.start()
        super().leaveEvent(event)
        
    def loading(self, success: bool, info: str) :
        pass
    
    def backup(self, user_input: str) :
        self.text_input.setText(user_input)
        self.stack.setCurrentWidget(self.text_input)
        self.setWindowOpacity(1.0)
        self.show()
        self.anim.stop()
    
    def change_view(self, view: Literal["text_input", "calendar_view"], **kwargs) :
        self.setWindowOpacity(1.0)
        self.anim.stop()
        match view :
            case "text_input" :
                self.stack.setCurrentWidget(self.text_input)
                self.anim.start()
            case "calendar_view" :
                self.fade_out = False
                if not all(key in kwargs for key in ["suggest_time", "fixed_events"]) :
                    logger.error("更新 Calendar View 缺少必要參數")
                    return
                self.calendar_view.update_content(suggest_time = kwargs["suggest_time"], fixed_event = kwargs["fixed_events"])
                self.stack.setCurrentWidget(self.calendar_view)
                self.anim.stop()
        
        for key, obj in self.widgets.items() :
            if key == view :
                obj.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                width = obj.width()
                height = obj.height()
            else :
                obj.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        self.setFixedSize(width, height)
        QApplication.processEvents()
        self.show()
        self.move_to_bottom_right()
    
    def reset(self) :
        self.fade_out = True
        self.setWindowOpacity(1.0)
        self.anim.start()