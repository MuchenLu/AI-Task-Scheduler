from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ui.styles import Colors

class TaskCard(QFrame) :
    def __init__(self, title: str, is_active: bool = True, parent = None) :
        super().__init__(parent)
        self.setObjectName("TaskCard")
        
        # 關鍵修正 1：移除 setFixedWidth(300)
        # 關鍵修正 2：設定尺寸策略，讓寬度可擴張，高度則隨內容最小化 (Minimum)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.title = title
        self.is_active = is_active
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 12, 15, 12)
        self.layout.setSpacing(5)

        self.title_label = QLabel(self.title)
        self.title_label.setWordWrap(True) # 允許長文字自動換行
        self.title_label.setStyleSheet("font-size: 15px; font-weight: bold; background: transparent;")
        
        # 關鍵修正 3：讓標籤的尺寸策略也配合換行
        self.title_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        
        self.layout.addWidget(self.title_label)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self.shadow)
        
        self.update_status()
    
    def set_active(self, is_active: bool) :
        self.is_active = is_active
        self.update_status()
    
    def update_status(self) :
        if self.is_active :
            self.setStyleSheet(f"""
                TaskCard {{
                    background-color: {Colors.TASK_ACTIVE_BG};
                    border-radius: 12px;
                }}
                QLabel {{ color: {Colors.TASK_ACTIVE_TEXT}; }}
            """)
            self.shadow.setEnabled(True)
        else :
            self.setStyleSheet(f"""
                TaskCard {{
                    background-color: rgba(255, 255, 255, 0.4);
                    border-radius: 12px;
                    border: 1px dashed {Colors.STATUS_IDLE};
                }}
                QLabel {{ color: {Colors.TEXT_PRIMARY}; }}
            """)
            self.shadow.setEnabled(False)