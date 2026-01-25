from PyQt6.QtWidgets import QApplication
import sys
from config import config
from utils.logger import setup_logger, logger
from views.setup import SetupView
from settings.settings import load_user_config

app = QApplication(sys.argv)
def launch() :
    setup_logger(log_file = config.LOG_FILE)
    config.validate()
    if not load_user_config() :
        setup = SetupView()
        setup.show()
        setup.setup_complete.connect(main)
    else :
        main()

def main() :
    from models.llm_client import llm
    logger.info("SCHEDAI 啟動成功！")

if __name__ == "__main__" :
    launch()
    sys.exit(app.exec())