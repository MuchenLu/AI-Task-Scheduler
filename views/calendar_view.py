'''
./views/components/calendar_card.py
視圖用途：
1. 顯示 Google Calendar 事件 & AI 推薦時間
2. 供使用者選擇時間
'''

from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Literal
from utils.date_helpper import to_ISO8601, set_to_start
from views.styles import COLORS
from views.components.calendar_card import CalendarCard

class HSeparator(QFrame):
    """ 水平分隔線 (Horizontal Line) """
    def __init__(self, width, parent=None):
        super().__init__(parent)
        # 設定形狀 (雖然我們會用 CSS 覆蓋，但保留語意)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Plain)
        
        # 關鍵：設定高度與顏色
        self.setFixedHeight(1)
        self.setFixedWidth(width)
        self.setStyleSheet(f"""background-color: {COLORS["border"]};
                           border: none""")

class CalendarView(QWidget) :
    def __init__(self, parent = None) :
        super().__init__(parent)
        self.per_min_height = 1.5
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.widget = QWidget()
        self.widget.setFixedHeight(int(25 * 60 * self.per_min_height - 30 * self.per_min_height))
        self.widget.setObjectName("CalendarWidget")
        
        scroll.setWidget(self.widget)
        layout.addWidget(scroll)
        
        temp_time = [f"{h:02d}:00" for h in range(24)]
        x = 0
        y = -int(30 * self.per_min_height)
        width = 100
        height = int(60 * self.per_min_height)
        for time in temp_time :
            label = QLabel(self.widget, text = time)
            label.setGeometry(x, y, width, height)
            label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
            label.setObjectName("CalendarTimeLabel")
            y += height
        
        self.setStyleSheet(f"""#CalendarWidget {{
            background-color: {COLORS["content_bg"]}
        }}
                           
        #CalendarTimeLabel{{
            background-color: transparent;
            color: {COLORS["text_header"]};
            font-size: 16px;
        }}""")
        
        self.setFixedHeight(int(8 * 60 * self.per_min_height - 30 * self.per_min_height))
        
    def update_content(self, suggest_time: list, fixed_event: list) :
        """更新日曆視圖

        Args:
            suggest_time (list): AI 推薦的時間，須為 Google Calendar API 格式
            fixed_event (list): 針對 AI 推薦時間所取得原有的事件，須為 Google Calendar API 格式
        """
        
        dates = []
        for item in suggest_time :
            date = item["start"]["dateTime"].split("T")[0]
            if date not in dates :
                dates.append(date)
        x = 100
        y = 0
        width = 150
        height = int(30 * self.per_min_height)
        for date in dates :
            label = QLabel(self.widget, text = date[5:])
            label.setObjectName("CalendarDateLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setGeometry(x, y, width, height)
            x += width
        self.setFixedWidth(100 + 150 * len(dates))
        
        x = 0
        y = int(30 * self.per_min_height)
        for _ in range(24) :
            line = HSeparator(100 + 150 * len(dates), self.widget)
            line.move(x, y)
            y += int(60 * self.per_min_height)
        
        for item in suggest_time :
            summary = item["summary"]
            start = item["start"]["dateTime"]
            end = item["end"]["dateTime"]
            card = CalendarCard(self.widget, summary, to_ISO8601(start, "datetime"), to_ISO8601(end, "datetime"), "suggest")
            x = int(100 + 150 * dates.index(start.split("T")[0])) # NOTE: 時間的位移再加上日期的位置
            y = int(30 * self.per_min_height + (to_ISO8601(start, "datetime") - set_to_start(start, "datetime")).total_seconds() / 60 * self.per_min_height) # 先位移一格（因為從第二格起算）再來開始到該時間的像素
            card.move(int(x + ((150 - card.width()) / 2)), y)
            card.show()
        
        for item in fixed_event :
            summary = item["summary"]
            start = item["start"]["dateTime"]
            end = item["end"]["dateTime"]
            try :
                pos = dates.index(start.split("T")[0])
            except ValueError :
                continue
            card = CalendarCard(self.widget, summary, to_ISO8601(start, "datetime"), to_ISO8601(end, "datetime"), "fixed")
            x = int(100 + 150 * dates.index(start.split("T")[0])) # NOTE: 時間的位移再加上日期的位置
            y = int(30 * self.per_min_height + (to_ISO8601(start, "datetime") - set_to_start(start, "datetime")).total_seconds() / 60 * self.per_min_height) # 先位移一格（因為從第二格起算）再來開始到該時間的像素
            card.move(int(x + ((150 - card.width()) / 2)), y)
            card.show()
        
        self.setStyleSheet(f"""#CalendarWidget {{
            background-color: {COLORS["content_bg"]}
        }}          
        #CalendarTimeLabel{{
            background-color: transparent;
            color: {COLORS["text_header"]};
            font-size: 16px;
        }}
        #CalendarDateLabel{{
            background-color: transparent;
            color: {COLORS["text_header"]};
            font-size: 16px;
        }}""")