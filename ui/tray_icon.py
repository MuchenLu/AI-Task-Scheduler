from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication
from config import ROOT_DIR

class TrayIcon(QSystemTrayIcon) :
    def __init__(self, main_window) :
        super().__init__()
        self.main_window = main_window
        
        self.setIcon(QIcon(str(ROOT_DIR / "assets" / "icons" / "icon.png")))
        self.setToolTip("AI Task Manager")
        
        self.menu = QMenu()
        
        self.action_wake = QAction("喚醒助理", self)
        self.action_wake.triggered.connect(self.wake_up_app)
        self.menu.addAction(self.action_wake)
        
        self.menu.addSeparator()
        
        self.action_quit = QAction("結束程式", self)
        self.action_quit.triggered.connect(self.quit_app)
        self.menu.addAction(self.action_quit)
        
        self.setContextMenu(self.menu)
        
        self.activated.connect(self.on_activated)
    
    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.wake_up_app()
    
    def wake_up_app(self):
        self.main_window.show_and_raise()

    def quit_app(self):
        QApplication.instance().quit()