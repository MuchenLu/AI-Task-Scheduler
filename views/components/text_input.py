'''
./views/components/text_input.py
元件功能：
1. 提供輸入框供使用者輸入指令
'''

from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from views.styles import COLORS

class TextInput(QWidget) :
    user_input = pyqtSignal(str)
    def __init__(self, parent) :
        super().__init__(parent)
        self.resize(300, 50)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.input = QLineEdit()
        self.input.setPlaceholderText("輸入指令...")
        self.layout.addWidget(self.input)
        self.setStyleSheet(f"""QWidget {{
            background-color: transparent;
            border: none;
            }}
            QLineEdit {{
                background-color: {COLORS["input_bg"]};
                border: {COLORS["border"]};
                border-radius: 8px;
                padding: 10px;
                color: {COLORS["text_body"]};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS["primary"]};
                outline: none;
            }}""")
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) :
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier :
                self.input.insertPlainText("\n")
                cursor = self.textCursor()
                self.setTextCursor(cursor)
                return
            else :
                content = self.input.text()
                self.clearFocus()
                self.input.setText("")
                self.input.repaint()
                self.user_input.emit(content)
                return
        super().keyPressEvent(event)