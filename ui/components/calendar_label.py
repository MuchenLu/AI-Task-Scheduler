from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from ui.styles import Colors

class BaseEventLabel(QFrame):
    """
    一個基礎的事件標籤，僅包含標題。
    透過在內部佈局中設定 padding 來解決文字被邊框裁切的問題。
    """
    def __init__(self, title, height, parent=None):
        super().__init__(parent)
        # 設定最小高度，但允許內容稍微撐開以容納邊距
        self.setMinimumHeight(height)
        
        # 核心修正：在內部佈局中加入邊距 (padding)
        # 這會在 QFrame 的邊框和內部 QLabel 之間創造空間
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5) # 左右 8px, 上下 5px
        layout.setSpacing(0)

        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.title_label)
        layout.addStretch() # 將標題推到頂部

class FixedEventLabel(BaseEventLabel):
    """固定的日曆行程標籤"""
    def __init__(self, title, height, parent=None):
        super().__init__(title, height, parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.EVENT_BG};
                border: 1px solid {Colors.EVENT_BORDER};
                border-radius: 4px;
            }}
        """)
        self.title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")

class SuggestEventLabel(BaseEventLabel):
    """建議的日曆行程標籤，可點擊"""
    choose_signal = pyqtSignal()

    def __init__(self, title, height, parent=None):
        super().__init__(title, height, parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.SUGGEST_BG};
                border: 1px dashed {Colors.TASK_ACTIVE_BG};
                border-radius: 4px;
            }}
            QFrame:hover {{
                background-color: {Colors.SELECTED_BG};
            }}
        """)
        self.title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")

    def mousePressEvent(self, event):
        self.choose_signal.emit()
        super().mousePressEvent(event)