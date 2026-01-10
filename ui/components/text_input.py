from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSignal, Qt
from ui.styles import Colors

class TextInput(QTextEdit) :
    input_content = pyqtSignal(str) # Signal emitted when the text input changes
    
    def __init__(self, parent = None) :
        super().__init__(parent)
        self.setFixedSize(350, 90)
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                color: #2f3640;
                selection-background-color: #a29bfe;
            }
            QTextEdit:focus {
                background-color: rgba(255, 255, 255, 0.95);
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