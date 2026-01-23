from PyQt6.QtWidgets import QApplication
import sys
from config import config
from utils.logger import setup_logger, logger
from views.setup import SetupView
from settings.settings import load_user_config

def main() :
    app = QApplication(sys.argv)
    setup_logger(log_file = config.LOG_FILE)
    config.validate()
    if not load_user_config() :
        setup = SetupView()
        setup.show()
    config.validate()
    logger.info("SCHEDAI 啟動成功！")
    sys.exit(app.exec())

if __name__ == "__main__" :
    main()