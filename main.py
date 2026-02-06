from PyQt6.QtWidgets import QApplication
import sys
from pynput import keyboard
from config import config
from utils.logger import setup_logger, logger
from views.setup import SetupView
from settings.settings import load_user_config

setup = None
window = None
sytem_tray = None
hotkey = None

app = QApplication(sys.argv)
def launch() :
    global setup
    setup_logger(log_file = config.LOG_FILE)
    config.validate()
    if not load_user_config() :
        setup = SetupView()
        setup.show()
        setup.setup_complete.connect(main)
    else :
        main()

def main() :
    global window, system_tray, hotkey
    from models.hotkey_service import GlobalHotKey
    from views.main_view import MainWindow
    from views.system_tray import SystemTray
    logger.info("SCHEDAI 啟動成功！")
    window = MainWindow()
    system_tray = SystemTray()
    system_tray.show()
    system_tray.show_signal.connect(lambda: window.change_view("text_input"))
    hotkey = GlobalHotKey()
    hotkey.triggered.connect(window.change_view)
    hotkey.start()
    window.show()
    window.setFocus()

if __name__ == "__main__" :
    launch()
    sys.exit(app.exec())