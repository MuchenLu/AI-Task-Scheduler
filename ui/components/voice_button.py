from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMovie
from pathlib import Path
from config import ROOT_DIR

class VoiceButton(QLabel) :
    def __init__(self, parent = None) :
        super().__init__(parent)
        
        self.movie = QMovie(str(Path(ROOT_DIR) / "assets" / "icons" / "record.gif"))
        self.setMovie(self.movie)
        self.movie.start()
        self.setScaledContents(True)
        self.setFixedSize(200, 200)
        self.movie.stop()
        self.movie.jumpToFrame(0)
    
    def start_anim(self) :
        self.movie.jumpToFrame(0)
        self.movie.start()
        
    def stop_anim(self) :
        self.movie.stop()
        self.movie.jumpToFrame(0)