from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget
from PyQt6.QtCore import pyqtSignal, Qt
from ui.components.calendar_label import FixedEventLabel, SuggestEventLabel
from ui.styles import Colors
from datetime import datetime
from core.state_machine import task_state_manager
from services.calendar_sync import calendar_service
from utils.logger import logger

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
        """
        核心修復：
        1. 移除事件內部時間標籤，僅顯示事件名稱。
        2. 使用 setFixedHeight 鎖死元件高度，確保 1:1 時間對齊。
        3. 嚴格控管 Layout Spacing 為 0。
        """
        # --- 1. 清理舊有的佈局與元件 ---
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_sub_layout(item.layout())

        if not schedules:
            return

        # 時區處理工具
        def to_naive(iso_str):
            try:
                dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
                return dt.replace(tzinfo=None)
            except Exception as e:
                logger.error(f"Time conversion error: {e}")
                return datetime.now().replace(tzinfo=None)

        # 佈局基準參數
        START_HOUR = 0
        END_HOUR = 24
        HEADER_HEIGHT = 45 

        # --- 2. 建立左側時間軸 (Ruler) ---
        time_ruler_layout = QVBoxLayout()
        time_ruler_layout.setSpacing(0)
        time_ruler_layout.setContentsMargins(0, 0, 0, 0)

        ruler_header = QLabel(" ")
        ruler_header.setFixedHeight(HEADER_HEIGHT)
        time_ruler_layout.addWidget(ruler_header)

        for hour in range(START_HOUR, END_HOUR):
            time_label = QLabel(f"{hour:02d}:00")
            time_label.setStyleSheet("font-size: 11px; color: #888888; border-top: 1px solid #EEEEEE;")
            time_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            # 每個小時的高度鎖死為 90px (60 * 1.5)
            time_label.setFixedHeight(int(60 * MIN_PIXEL)) 
            time_label.setContentsMargins(0, 0, 8, 0)
            time_ruler_layout.addWidget(time_label)
        
        time_ruler_layout.addStretch()
        self.layout.addLayout(time_ruler_layout)

        # --- 3. 建立日期欄位 (Columns) ---
        all_dates = sorted(list({to_naive(s['start']['dateTime']).date() for s in schedules}))
        
        for date in all_dates:
            date_column = QVBoxLayout()
            date_column.setSpacing(0) # 關鍵：禁止元件間產生額外像素間距
            date_column.setContentsMargins(0, 0, 0, 0)

            # 日期標題
            date_label = QLabel(date.strftime('%Y-%m-%d'))
            date_label.setFixedHeight(HEADER_HEIGHT)
            date_label.setStyleSheet("font-size: 13px; font-weight: bold; border-bottom: 1px solid #DDDDDD;")
            date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            date_column.addWidget(date_label)
            
            # 過濾當日行程並排序
            today_schedules = [s for s in schedules if to_naive(s['start']['dateTime']).date() == date]
            today_schedules.sort(key=lambda x: to_naive(x['start']['dateTime']))

            # 渲染起始基準點：當天 00:00
            current_render_pos = datetime.combine(date, datetime.min.time()).replace(hour=START_HOUR)

            for schedule in today_schedules:
                start = to_naive(schedule['start']['dateTime'])
                end = to_naive(schedule['end']['dateTime'])

                # A. 填補「空白時間」
                gap_min = (start - current_render_pos).total_seconds() / 60
                if gap_min > 0:
                    date_column.addSpacing(int(gap_min * MIN_PIXEL))

                # B. 計算「事件高度」
                duration_min = (end - start).total_seconds() / 60
                height = int(duration_min * MIN_PIXEL)
                
                # C. 建立 Label (不傳入時間字串，只傳入事件標題)
                if schedule['type'] == 'fixed':
                    # 傳入空字串作為時間標籤內容
                    label = FixedEventLabel(schedule['text'], "", height, self)
                else:
                    label = SuggestEventLabel(schedule['text'], "", height, self)
                    label.choose_signal.connect(lambda s=schedule: self.choose_time.emit(s))
                
                # D. 強制鎖定元件高度，防止 Layout 撐大
                label.setFixedHeight(height)
                # 滑鼠移上去依然可以看到完整時間細節
                label.setToolTip(f"{schedule['text']}\n{start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
                
                date_column.addWidget(label)
                
                # 更新渲染進度
                current_render_pos = end
            
            # 填滿底部剩餘空間
            date_column.addStretch()
            self.layout.addLayout(date_column)

        self.layout.addStretch()

    def _clear_sub_layout(self, layout):
        """遞迴清理子佈局的輔助函式"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_sub_layout(item.layout())