from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt
from pathlib import Path
from config import ROOT_DIR

class VoiceButton(QLabel) :
    def __init__(self, parent = None) :
        super().__init__(parent)
        
        # 核心修正：設定屬性並將背景設為透明。
        # 這能確保 QLabel 本身不會繪製任何背景，只有 GIF 動畫是可見的。
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        
        self.movie = QMovie(str(Path(ROOT_DIR) / "assets" / "icons" / "record.gif"))
        self.setMovie(self.movie)
        self.movie.start()
        self.setScaledContents(True)
        self.setFixedSize(100, 100)
        self.movie.stop()
        self.movie.jumpToFrame(0)
    
    def start_anim(self) :
        self.movie.jumpToFrame(0)
        self.movie.start()
        
    def stop_anim(self) :
        self.movie.stop()
        self.movie.jumpToFrame(0)