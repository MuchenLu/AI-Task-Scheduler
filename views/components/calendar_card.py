'''
./views/components/calendar_card.py
視圖用途：
1. 顯示 Google Calendar 事件 & A 推薦時間
2. 供使用者選擇時間
'''

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Literal
from datetime import datetime
from views.styles import COLORS

class CalendarCard(QWidget) :
    choose_signal = pyqtSignal(datetime, datetime)
    def __init__(self, parent, task_name: str, start_time: datetime, end_time: datetime, kind: Literal["fixed", "suggest"]) :
        super().__init__(parent)
        self.kind = kind
        self.start_time = start_time
        self.end_time = end_time
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(8, 5, 8, 5)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        self.per_min_height = 1.5
        self.setFixedWidth(135)
        height = int((end_time - start_time).total_seconds() / 60 * self.per_min_height)
        self.setFixedHeight(int(height))
        self.task_name = QLabel(task_name)
        self.task_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.task_name.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.task_name.setObjectName("TaskTitle")
        self.task_name.setWordWrap(True)
        self.task_time = QLabel(f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        self.task_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.task_time.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.task_time.setObjectName("TaskTime")
        self.layout.addWidget(self.task_name)
        # self.layout.addSpacing(5)
        self.layout.addWidget(self.task_time)
        self.layout.addStretch()
        
        match self.kind :
            case "fixed" :
                self.setStyleSheet(f"""QWidget {{
                    background-color: {COLORS["input_bg"]};
                    border: {COLORS["border"]};
                    border-radius: 8px;
                }}
                #TaskTitle {{
                    color: {COLORS["text_body"]};
                    font-size: 14px;
                }}
                #TaskTime {{
                    color: {COLORS["text_muted"]};
                    font-size: 12px;
                }}""")
            case "suggest" :
                self.setStyleSheet(f"""QWidget {{
                    background-color: {COLORS["primary"]};
                    border: {COLORS["border"]};
                    border-radius: 8px;
                }}
                QWidget:hover {{
                    background-color: {COLORS["primary_hover"]};
                }}
                #TaskTitle {{
                    background-color: transparent;
                    color: white;
                    font-size: 14px;
                }}
                #TaskTime {{
                    background-color: transparent;
                    color: white;
                    font-size: 12px;
                }}""")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton :
            if self.kind == "suggest" :
                self.setStyleSheet(f"""QWidget {{
                    background-color: {COLORS["primary_pressed"]};
                    border: {COLORS["border"]};
                    border-radius: 8px;
                }}
                #TaskTitle {{
                    background-color: transparent;
                    color: white;
                    font-size: 14px;
                }}
                #TaskTime {{
                    background-color: transparent;
                    color: white;
                    font-size: 12px;
                }}""")
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton :
            if self.kind == "suggest" :
                self.setStyleSheet(f"""QWidget {{
                    background-color: {COLORS["primary"]};
                    border: {COLORS["border"]};
                    border-radius: 8px;
                }}
                QWidget:hover {{
                    background-color: {COLORS["primary_hover"]};
                }}
                #TaskTitle {{
                    background-color: transparent;
                    color: white;
                    font-size: 14px;
                }}
                #TaskTime {{
                    background-color: transparent;
                    color: white;
                    font-size: 12px;
                }}""")
                self.choose_signal.emit(self.start_time, self.end_time)