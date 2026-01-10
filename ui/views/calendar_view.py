from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget
from PyQt6.QtCore import pyqtSignal, Qt
from ui.components.calendar_label import FixedEventLabel, SuggestEventLabel
from ui.styles import Colors
from datetime import datetime
from core.state_machine import task_state_manager
from services.calendar_sync import calendar_service

MIN_PIXEL = 1.5

class CalendarView(QFrame) :
    choose_time = pyqtSignal(dict)  # Signal emitted when a suggest event is chosen
    def __init__(self, parent = None) :
        """Use to display suggest schedule insert to fixed schedule

        Args:
            dates (set): Set of date strings to display.
            schedules (list): List of schedule dicts with 'start', "end", 'type', and 'text' keys.
            parent (QMainWindow, optional): Assign parent window. Defaults to None.
        """
        super().__init__(parent)
        self.setStyleSheet(f"""
                            QFrame {{
                                background-color: {Colors.BACKGROUND};
                                border: none;
                            }}
                            QScrollArea {{
                                border: none;
                                background-color: transparent;
                            }}
                            QWidget#scrollContent {{
                                background-color: transparent;
                            }}
                           """)
        
        # 主佈局，用於容納滾動區域
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 滾動區域，允許檢視超出視窗大小的內容
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # 用於滾動內容的容器 widget
        scroll_content_widget = QWidget()
        scroll_content_widget.setObjectName("scrollContent")
        scroll_area.setWidget(scroll_content_widget)
        
        # 這個佈局才真正持有日曆的欄位
        self.layout = QHBoxLayout(scroll_content_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        
        main_layout.addWidget(scroll_area)
        
        self.task_state_manager = task_state_manager
        self.task_state_manager.task_info.connect(self.update)
    
    def update(self, schedules: list):
        """更新視圖內容，顯示固定的與建議的行程"""
        # 清除舊有的佈局內容
        if self.layout is not None:
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    sub_layout = item.layout()
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        if sub_item.widget():
                            sub_item.widget().deleteLater()
                    sub_layout.deleteLater()
        
        if not schedules:
            return

        # 輔助函式：統一轉換為無時區 datetime 以防計算間距時出錯
        def to_naive(iso_str):
            return datetime.fromisoformat(iso_str).replace(tzinfo=None)

        # 設定顯示的時間軸範圍 (00:00 - 23:00)
        start_hour = 0
        end_hour = 23

        # --- 時間軸標籤繪製 ---
        time_ruler_layout = QVBoxLayout()
        time_ruler_layout.setSpacing(0)
        ruler_header = QLabel(" ")
        ruler_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        time_ruler_layout.addWidget(ruler_header)

        for hour in range(start_hour, end_hour + 1):
            time_label = QLabel(f"{hour:02d}:00")
            time_label.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY};")
            time_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            time_label.setFixedHeight(int(60 * MIN_PIXEL))
            time_label.setContentsMargins(0, 0, 10, 0)
            time_ruler_layout.addWidget(time_label)
        
        time_ruler_layout.addStretch()
        self.layout.addLayout(time_ruler_layout)

        # --- 按日期繪製行程欄位 ---
        dates = sorted(list({datetime.fromisoformat(s['start']['dateTime']).date() for s in schedules}))
        
        for date in dates:
            date_column = QVBoxLayout()
            date_column.setSpacing(0)

            date_label = QLabel(date.strftime('%Y-%m-%d'))
            date_label.setStyleSheet(f"font-size: 14px; font-weight: bold; margin-bottom: 5px; color: {Colors.TEXT_PRIMARY};")
            date_column.addWidget(date_label)
            
            today_schedules = [s for s in schedules if datetime.fromisoformat(s['start']['dateTime']).date() == date]
            today_schedules.sort(key=lambda x: x['start']['dateTime'])

            # 初始渲染位置設定為當天 00:00 (Naive)
            current_render_pos = datetime.combine(date, datetime.min.time()).replace(hour=start_hour)

            for schedule in today_schedules:
                # 統一轉為 naive datetime 進行運算，避免時區不一致的 TypeError
                start = to_naive(schedule['start']['dateTime'])
                end = to_naive(schedule['end']['dateTime'])

                # 計算行程前的空白間隙
                space_minutes = (start - current_render_pos).total_seconds() / 60
                if space_minutes > 0:
                    date_column.addSpacing(int(space_minutes * MIN_PIXEL))

                # 計算行程高度
                height = int(((end - start).total_seconds() / 60) * MIN_PIXEL)
                if height <= 5: height = 15 # 確保極短事件仍可見
                
                if schedule['type'] == 'fixed':
                    label = FixedEventLabel(schedule['text'], f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}", height, self)
                    date_column.addWidget(label)
                elif schedule['type'] == 'suggest':
                    label = SuggestEventLabel(schedule['text'], f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}", height, self)
                    label.choose_signal.connect(lambda sched=schedule: self.choose_time.emit(sched))
                    date_column.addWidget(label)
                
                current_render_pos = end
            
            date_column.addStretch()
            self.layout.addLayout(date_column)

        self.layout.addStretch()
        # 強制啟動佈局，確保父視窗能讀取到正確的 sizeHint
        self.layout.activate()