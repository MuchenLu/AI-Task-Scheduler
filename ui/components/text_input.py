from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSignal, Qt
from ui.styles import Colors

class TextInput(QTextEdit) :
    input_content = pyqtSignal(str) # Signal emitted when the text input changes
    
    def __init__(self, parent = None) :
        super().__init__(parent)
        # 核心修正：設定 WA_StyledBackground 屬性。
        # 這會告訴 QTextEdit 不要繪製預設的、不透明的背景，
        # 而是完全依賴樣式表來決定背景外觀，從而解決透明視窗下的方框問題。
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(350, 90)
        self.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
                color: #2f3640;
                selection-background-color: #a29bfe;
            }
            QTextEdit:focus {
                background: transparent;
                border: 1px solid #74b9ff; 
            }
        """)
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) :
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier :
                super().keyPressEvent(event)  # Allow newline with Shift + Enter
            else :
                text = self.toPlainText().strip()
                if text :
                    self.input_content.emit(text)
                    self.clear()
        else :
            super().keyPressEvent(event)