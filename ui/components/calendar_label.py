from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from ui.styles import Colors

class FixedEventLabel(QFrame) :
    def __init__(self, text: str, time: str, height: int, parent = None) :
        super().__init__(parent)
        self.setFixedSize(200, height)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        self.title = QLabel(text, self)
        self.title.setWordWrap(True)
        self.title.setStyleSheet(f"""QLabel {{
                                font-size: 13px;
                                font-weight: bold;
                                color: {Colors.TEXT_PRIMARY};
                                background-color: transparent; /* 重要：透明背景才不會蓋住卡片底色 */
                                border: none;
                                padding: 0px;
                                margin-bottom: 2px;
                            }}""")
        self.layout.addWidget(self.title)
        
        self.time = QLabel(time, self)
        self.time.setWordWrap(True)
        self.time.setStyleSheet(f"""
                                QLabel {{
                                    font-size: 11px;
                                    color: {Colors.TEXT_SECONDARY};
                                    background-color: transparent;
                                    border: none;
                                    padding: 0px;
                                    margin-top: 2px;
                                }}
                                """)
        self.layout.addWidget(self.time)
        
        self.setStyleSheet(f"""
                           QFrame {{
                background-color: {Colors.EVENT_BG};
                border: 1px solid {Colors.EVENT_BORDER};
                border-radius: 6px;
                padding: 2px;
            }}
            """)

class SuggestEventLabel(QLabel) :
    choose_signal = pyqtSignal()  # Signal emitted when the label is clicked
    def __init__(self, text: str, time: str, height: int, parent = None) :
        super().__init__(parent)
        self.setFixedSize(200, height)  
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        self.title = QLabel(text, self)
        self.title.setWordWrap(True)
        self.title.setStyleSheet(f"""QLabel {{
                                font-size: 13px;
                                font-weight: bold;
                                color: {Colors.TEXT_PRIMARY};
                                background-color: transparent;
                                border: none;
                                padding: 0px;
                                margin-bottom: 2px;
                            }}""")
        self.layout.addWidget(self.title)
        
        self.time = QLabel(time, self)
        self.time.setWordWrap(True)
        self.time.setStyleSheet(f"""
                                QLabel {{
                                    font-size: 11px;
                                    color: {Colors.TEXT_SECONDARY};
                                    background-color: transparent;
                                    border: none;
                                    padding: 0px;
                                    margin-top: 2px;
                                }}
                                """)
        self.layout.addWidget(self.time)
        
        
        self.setWordWrap(True)  # 允許長文字自動換行
        self.setStyleSheet(f"""
                           QFrame {{
                background-color: {Colors.SUGGEST_BG};
                border: 1px dashed {Colors.STATUS_THINKING};
                border-radius: 6px;
                padding: 2px;
            }}
            """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
    def mouseReleaseEvent(self, event) :
        if event.button() == Qt.MouseButton.LeftButton :
            self.change_status(selected=True)
            self.choose_signal.emit()
        super().mouseReleaseEvent(event)
    
    def change_status(self, selected: bool) :
        if selected :
            self.setStyleSheet(f"""
                               QLabel {{
                    background-color: {Colors.SELECTED_BG};
                    color: {Colors.TEXT_PRIMARY};
                    border: 1px solid {Colors.STATUS_THINKING};
                    border-radius: 6px;
                    padding: 2px;
                    font-size: 12px;
                }}
                """)
        else :
            self.setStyleSheet(f"""
                               QLabel {{
                    background-color: {Colors.SUGGEST_BG};
                    color: {Colors.TEXT_SECONDARY};
                    border: 1px dashed {Colors.STATUS_THINKING};
                    border-radius: 6px;
                    padding: 2px;
                    font-size: 12px;
                }}
                """)