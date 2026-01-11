from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ui.styles import Colors

class TaskCard(QFrame) :
    def __init__(self, title: str, is_active: bool = True, parent = None) :
        # 核心修正：QFrame 的建構子最多只應傳入 parent，第二個參數是 window flags，不應傳入 parent。
        super().__init__(parent)
        self.setObjectName("TaskCard")
        self.setFixedWidth(300)
        
        self.title = title
        self.is_active = is_active
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)
        self.layout.setSpacing(5)

        self.title_label = QLabel(self.title)
        self.title_label.setWordWrap(True) # 允許長文字自動換行
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self.shadow)
    
    def set_active(self, is_active: bool) :
        self.is_active = is_active
        self.update_status()
    
    def update_status(self) :
        if self.is_active :
            self.setStyleSheet(f"""
                TaskCard {{
                    background-color: {Colors.TASK_ACTIVE_BG};
                    border-radius: 12px;
                    border: none;
                }}
                QLabel {{
                    color: {Colors.TASK_WHITE_TEXT};
                }}
            """ )
            self.shadow.setEnabled(True)
        else :
            self.setStyleSheet(f"""
                TaskCard {{
                    background-color: rgba(255, 255, 255, 0.3); /* 微微的白底 */
                    border-radius: 12px;
                    border: 1px dashed {Colors.STATUS_IDLE}; /* 虛線邊框 */
                }}
                QLabel {{
                    color: {Colors.TEXT_PRIMARY}; /* 深灰字 */
                }}
            """)
            self.shadow.setEnabled(False)