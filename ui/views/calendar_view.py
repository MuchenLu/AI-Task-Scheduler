from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QLayout
from PyQt6.QtCore import pyqtSignal, Qt
from ui.components.calendar_label import FixedEventLabel, SuggestEventLabel
from ui.styles import Colors
from datetime import datetime
import pytz
from core.state_machine import task_state_manager
from services.calendar_sync import calendar_service
from utils.logger import logger

MIN_PIXEL = 1.5

def to_local_naive(iso_str: str) -> datetime:
    """
    關鍵修正：將 UTC 或帶有偏移的 ISO 時間字串轉換為本地 (台北) 時間，再轉為 naive datetime 供 UI 計算。
    """
    try:
        # 處理 Google API 回傳的 Z (UTC) 或帶有時區偏移的格式
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        # 轉換為台北時區 (+8)
        taipei_tz = pytz.timezone('Asia/Taipei')
        dt_taipei = dt.astimezone(taipei_tz)
        # 轉為無時區格式供 UI 計算
        return dt_taipei.replace(tzinfo=None)
    except (ValueError, TypeError) as e:
        logger.error(f"時間轉換錯誤: {e}，輸入: '{iso_str}'。使用當前時間作為備援。")
        return datetime.now()

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
        self.scroll_content_widget = QWidget()
        self.scroll_content_widget.setObjectName("scrollContent")
        scroll_area.setWidget(self.scroll_content_widget)
        
        # 這個佈局才真正持有日曆的欄位
        self.layout = QHBoxLayout(self.scroll_content_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        
        main_layout.addWidget(scroll_area)
        
        self.task_state_manager = task_state_manager
        self.task_state_manager.task_info.connect(self.update)
    
    def update(self, schedules: list):
        """
        最終精簡版：
        1. 移除事件內部的時間標籤，僅顯示事件名稱。
        2. 強制鎖定元件高度 (setFixedHeight)，確保 1:1 時間對齊。
        3. 統一日期與時間軸的文字顏色為 #888888。
        """
        # --- 1. 清理舊佈局 ---
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_sub_layout(item.layout())

        START_HOUR = 0
        END_HOUR = 24
        HEADER_HEIGHT = 45 

        # --- 2. 建立時間軸 (Ruler) ---
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
            time_label.setFixedHeight(int(60 * MIN_PIXEL)) 
            time_label.setContentsMargins(0, 0, 8, 0)
            time_ruler_layout.addWidget(time_label)
        
        time_ruler_layout.addStretch()
        self.layout.addLayout(time_ruler_layout)

        # --- 3. 建立日期與事件欄位 (Columns) ---
        # --- 核心修正：只顯示包含「建議行程」的日期 ---
        # 1. 首先，找出所有包含建議行程的日期。
        suggestion_dates = {to_local_naive(s['start']['dateTime']).date() 
                            for s in schedules 
                            if s.get('type') == 'suggest' and 'dateTime' in s.get('start', {})}

        # 2. 如果有建議行程，則只顯示那些天。
        if suggestion_dates:
            dates_to_display = suggestion_dates
        else:
            # 3. 如果沒有建議行程 (例如只是查詢)，則顯示所有有事件的天。
            dates_to_display = {to_local_naive(s['start']['dateTime']).date() for s in schedules if 'dateTime' in s.get('start', {})}
            # 如果仍然沒有任何日期，則備援為顯示今天，避免畫面空白。
            if not dates_to_display:
                dates_to_display.add(datetime.now().date())

        all_dates = sorted(list(dates_to_display))
        
        for date in all_dates:
            date_column = QVBoxLayout()
            date_column.setSpacing(0) # 關鍵：禁止元件間產生間距
            date_column.setContentsMargins(0, 0, 0, 0)

            # 日期標題：顏色設為 #888888
            date_label = QLabel(date.strftime('%Y-%m-%d'))
            date_label.setFixedHeight(HEADER_HEIGHT)
            date_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #888888; border-bottom: 1px solid #EEEEEE;")
            date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            date_column.addWidget(date_label)
            
            today_schedules = [s for s in schedules if 'dateTime' in s.get('start', {}) and to_local_naive(s['start']['dateTime']).date() == date]
            today_schedules.sort(key=lambda x: to_local_naive(x['start']['dateTime']))

            # 渲染基準點：當天 00:00
            current_render_pos = datetime.combine(date, datetime.min.time()).replace(hour=START_HOUR)

            for schedule in today_schedules:
                start = to_local_naive(schedule['start']['dateTime'])
                end = to_local_naive(schedule['end']['dateTime'])

                # A. 填補空白間隔
                gap_min = (start - current_render_pos).total_seconds() / 60
                if gap_min > 0:
                    date_column.addSpacing(int(gap_min * MIN_PIXEL))

                # B. 計算高度
                duration_min = (end - start).total_seconds() / 60
                height = int(duration_min * MIN_PIXEL)
                
                # C. 建立事件元件
                if schedule['type'] == 'fixed':
                    label = FixedEventLabel(schedule['text'], height, self)
                else:
                    label = SuggestEventLabel(schedule['text'], height, self)
                    label.choose_signal.connect(lambda s=schedule: self.choose_time.emit(s))
                
                # D. 強制鎖定高度，並設定 ToolTip 以備不時之需
                label.setFixedHeight(height)
                label.setToolTip(f"{schedule['text']}\n{start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
                
                date_column.addWidget(label)
                current_render_pos = end
            
            date_column.addStretch()
            self.layout.addLayout(date_column)

        self.layout.addStretch()

    def _clear_sub_layout(self, layout):
        """輔助函式：清理子佈局內容"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_sub_layout(item.layout())