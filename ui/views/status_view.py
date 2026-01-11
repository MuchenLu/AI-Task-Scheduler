from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from ui.styles import Colors

class StatusView(QFrame):
    """
    一個簡單的卡片，用於顯示應用程式的狀態，例如 "AI 正在處理中..."。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusView")
        self.setStyleSheet(f"""
            #StatusView {{
                background-color: {Colors.BACKGROUND};
                border-radius: 20px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label = QLabel("AI 正在處理中...")
        self.status_label.setStyleSheet(f"font-size: 16px; color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(self.status_label)

    def set_status_text(self, text: str, msg_type: str = 'info'):
        self.status_label.setText(text)
        if msg_type == 'error':
            self.status_label.setStyleSheet("font-size: 14px; color: #d63031; font-weight: bold;")
        else:
            self.status_label.setStyleSheet(f"font-size: 16px; color: {Colors.TEXT_SECONDARY};")