import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from config import config
from ui.main_window import MainWindow
from core.state_machine import task_state_manager
from ui.tray_icon import TrayIcon
from utils.logger import logger

def is_admin():
    """Check if the script is running with administrator privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 即使主視窗關閉，應用程式仍在系統匣中運行
    app.setQuitOnLastWindowClosed(False)

    # 檢查設定檔
    if not config.validate():
        logger.critical("Configuration validation failed. Exiting application.")
        sys.exit(1)
    logger.info("Configuration validation passed.")

    # 檢查管理員權限，因為全域熱鍵需要它
    if not is_admin():
        logger.warning("Application is not running with administrator privileges. Global hotkeys may not work.")
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("未以系統管理員身分執行")
        msg_box.setInformativeText("全域熱鍵 (例如 Alt+R) 可能無法正常運作。\n請嘗試以右鍵點擊腳本或終端機，並選擇「以系統管理員身分執行」。")
        msg_box.setWindowTitle("權限警告")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    # MainWindow 現在是核心，處理所有UI邏輯和工作線程
    window = MainWindow()
    
    # 新增：啟動後立刻要求狀態機更新一次日曆，預載入今天的資料
    task_state_manager.fetch_and_emit_calendar()
    
    # 設定系統匣圖示
    tray = TrayIcon(window)
    tray.show()

    # 應用程式啟動時，預設顯示 TaskView
    window.change_task()

    sys.exit(app.exec())