'''
./views/components/loading.py
視圖用途：
1. 顯示 loading 狀態
2. 告知使用者步驟
'''

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen
from views.styles import COLORS

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50) # 預設大小
        
        self.color = QColor(COLORS["primary"])
        self.track_color = QColor(COLORS["input_bg"])
        self.line_width = 5
        
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.start()

    def start(self):
        if not self.timer.isActive():
            self.timer.start(30) # 控制 FPS

    def rotate(self):
        self.angle = (self.angle + 12) % 360 # 控制速度
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(
            self.line_width / 2, 
            self.line_width / 2, 
            self.width() - self.line_width, 
            self.height() - self.line_width
        )
        
        track_pen = QPen(self.track_color)
        track_pen.setWidth(self.line_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)
        
        spinner_pen = QPen(self.color)
        spinner_pen.setWidth(self.line_width)
        spinner_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(spinner_pen)
        
        painter.drawArc(rect, -self.angle * 16, -100 * 16)
        painter.end()

class Loading(QWidget) :
    def __init__(self, text) :
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.text = text
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.spinner = LoadingSpinner(self)
        self.layout.addWidget(self.spinner)
        
        self.label = QLabel(self.text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        
    def update_text(self, text) :
        self.label.setText(text)
        self.update()