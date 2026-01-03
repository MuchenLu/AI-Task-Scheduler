from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from ui.components.calendar_label import FixedEventLabel, SuggestEventLabel
from ui.styles import Colors
from datetime import datetime

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
        
        '''
        schedules.sort(key = lambda x : x['dateTime'])
        for date in dates :
            date_column = QVBoxLayout()
            date_label = QLabel(date)
            date_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
            date_column.addWidget(date_label)
            
            today_schedules = [s for s in schedules if datetime.fromisoformat(s['date']).date() == datetime.fromisoformat(date).date()]
            for schedule in today_schedules :
                start = datetime.fromisoformat(schedule['start']['dateTime'])
                end = datetime.fromisoformat(schedule['end']['dateTime'])
                if schedule['type'] == 'fixed' :
                    label = FixedEventLabel(schedule['text'], f"{datetime.strftime(start, "%H:%M")} ~ {datetime.strftime(end, '%H:%M')}", int((datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60 / 2), self)
                    date_column.addWidget(label)
                elif schedule['type'] == 'suggest' :
                    label = SuggestEventLabel(schedule['text'], f"{datetime.strftime(start, '%H:%M')} ~ {datetime.strftime(end, '%H:%M')}", int((datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60 / 2), self)
                    label.choose_signal.connect(lambda : self.choose_time.emit(schedule))
                    date_column.addWidget(label)
                
                try :
                    space = int((datetime.strptime(today_schedules[today_schedules.index(schedule)+1]['start']['dateTime'], "%H:%M") - datetime.strptime(schedule['end']['dateTime'], "%H:%M")).total_seconds() / 60 / 2)
                    date_column.addSpacing(space)
                except IndexError :
                    pass
            
            self.layout.addLayout(date_column)
        '''
    
    def update(self, dates: set, schedules: list) :
        if self.layout is not None :
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        schedules.sort(key = lambda x : x['dateTime'])
        for date in dates :
            date_column = QVBoxLayout()
            date_label = QLabel(date)
            date_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
            date_column.addWidget(date_label)
            
            today_schedules = [s for s in schedules if datetime.fromisoformat(s['date']).date() == datetime.fromisoformat(date).date()]
            for schedule in today_schedules :
                start = datetime.fromisoformat(schedule['start']['dateTime'])
                end = datetime.fromisoformat(schedule['end']['dateTime'])
                if schedule['type'] == 'fixed' :
                    label = FixedEventLabel(schedule['text'], f"{datetime.strftime(start, "%H:%M")} ~ {datetime.strftime(end, '%H:%M')}", int((datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60 / 2), self)
                    date_column.addWidget(label)
                elif schedule['type'] == 'suggest' :
                    label = SuggestEventLabel(schedule['text'], f"{datetime.strftime(start, '%H:%M')} ~ {datetime.strftime(end, '%H:%M')}", int((datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60 / 2), self)
                    label.choose_signal.connect(lambda : self.choose_time.emit(schedule))
                    date_column.addWidget(label)
                
                try :
                    space = int((datetime.strptime(today_schedules[today_schedules.index(schedule)+1]['start']['dateTime'], "%H:%M") - datetime.strptime(schedule['end']['dateTime'], "%H:%M")).total_seconds() / 60 / 2)
                    date_column.addSpacing(space)
                except IndexError :
                    pass
            
            self.layout.addLayout(date_column)