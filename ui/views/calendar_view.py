from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout
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
            """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        
        self.task_state_manager = task_state_manager
        self.task_state_manager.task_info.connect(self.update)
    
    def update(self, schedules: list) :
        # NOTE: Use to clean the layout
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
        
        # Find the earliest and latest times across all schedules to create a dynamic time range
        all_starts = [datetime.fromisoformat(s['start']['dateTime']) for s in schedules]
        all_ends = [datetime.fromisoformat(s['end']['dateTime']) for s in schedules]
        min_time = min(all_starts)
        max_time = max(all_ends)

        start_hour = min_time.hour
        end_hour = max_time.hour

        # If the latest event doesn't end exactly on the hour, extend the ruler to include the next hour
        if max_time.minute > 0 or max_time.second > 0:
            end_hour += 1
        
        # Ensure the view has at least a one-hour span
        if end_hour <= start_hour:
            end_hour = start_hour + 1

        # --- 時間軸 ---
        time_ruler_layout = QVBoxLayout()
        time_ruler_layout.setSpacing(0)
        
        # 用於對齊日期標籤的空白標頭
        ruler_header = QLabel(" ")
        ruler_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        time_ruler_layout.addWidget(ruler_header)

        # Add time labels for each hour within the dynamic range
        for hour in range(start_hour, end_hour + 1):
            time_label = QLabel(f"{hour:02d}:00")
            time_label.setStyleSheet("font-size: 12px; color: #888888;")
            time_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            time_label.setFixedHeight(int(60 * MIN_PIXEL))
            time_label.setContentsMargins(0, 0, 10, 0)
            time_ruler_layout.addWidget(time_label)
        
        time_ruler_layout.addStretch()
        self.layout.addLayout(time_ruler_layout)

        # --- 日期欄位 ---
        dates = sorted(list({datetime.fromisoformat(schedule['start']['dateTime']).date() for schedule in schedules}))
        for date in dates:
            date_column = QVBoxLayout()
            date_column.setSpacing(0) # 手動控制間距

            date_label = QLabel(date.strftime('%Y-%m-%d'))
            date_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
            date_column.addWidget(date_label)
            
            today_schedules = [s for s in schedules if datetime.fromisoformat(s['start']['dateTime']).date() == date]
            today_schedules.sort(key=lambda x: x['start']['dateTime'])

            if not today_schedules:
                date_column.addStretch()
                self.layout.addLayout(date_column)
                continue

            # This marker tracks the vertical position for placing the next widget.
            tz = datetime.fromisoformat(today_schedules[0]['start']['dateTime']).tzinfo
            current_render_pos = datetime.combine(date, datetime.min.time(), tzinfo=tz).replace(hour=start_hour)

            for i, schedule in enumerate(today_schedules) :
                start = datetime.fromisoformat(schedule['start']['dateTime'])
                end = datetime.fromisoformat(schedule['end']['dateTime'])

                # Define the visible boundaries for this day's column
                view_start_dt = current_render_pos
                view_end_dt = datetime.combine(date, datetime.min.time(), tzinfo=tz).replace(hour=end_hour + 1)

                # Skip events that are completely outside the remaining visible area
                if end <= view_start_dt or start >= view_end_dt:
                    continue

                # The part of the event that is actually visible on screen
                visible_start = max(start, view_start_dt)
                visible_end = min(end, view_end_dt)

                # Add spacing from the last rendered position to the start of this event's visible part
                space_minutes = (visible_start - current_render_pos).total_seconds() / 60
                if space_minutes > 0:
                    date_column.addSpacing(int(space_minutes * MIN_PIXEL))

                # Height is based on the visible duration of the event
                height = int(((visible_end - visible_start).total_seconds() / 60) * MIN_PIXEL)
                if height <= 0: continue
                
                if schedule['type'] == 'fixed' :
                    label = FixedEventLabel(schedule['text'], f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}", height, self)
                    date_column.addWidget(label)
                elif schedule['type'] == 'suggest' :
                    label = SuggestEventLabel(schedule['text'], f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}", height, self)
                    label.choose_signal.connect(lambda sched=schedule: self.choose_time.emit(sched))
                    date_column.addWidget(label)
                
                # Update the render position to the end of the visible part of this event
                current_render_pos = visible_end
            
            date_column.addStretch()
            self.layout.addLayout(date_column)

        self.layout.addStretch()