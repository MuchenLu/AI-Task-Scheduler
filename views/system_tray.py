'''
./views/system_tray.py
視圖功能：
1. 顯示系統托盤
2. 操控退出系統
3. 手動喚醒系統
'''

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from config.config import ICON_ICO
import sys

class SystemTray(QSystemTrayIcon) :
    show_signal = pyqtSignal()
    def __init__(self) :
        super().__init__()
        self.setIcon(QIcon(str(ICON_ICO)))
        self.setToolTip("SCHEDAI")
        self.menu = QMenu()
        
        self.quit_action = QAction("退出")
        self.quit_action.triggered.connect(self.quit_system)
        self.menu.addAction(self.quit_action)
        
        self.menu.addSeparator()
        
        self.show_text_input_action = QAction("顯示輸入框")
        self.show_text_input_action.triggered.connect(self.show_text_input)
        self.menu.addAction(self.show_text_input_action)
        
        self.setContextMenu(self.menu)
    
    def quit_system(self) :
        sys.exit(0)
    
    def show_text_input(self) :
        self.show_signal.emit()