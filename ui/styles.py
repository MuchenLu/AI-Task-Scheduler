class Colors :
    #* === Backgrounds ===
    BACKGROUND = "rgba(245, 246, 250, 0.95)"
    
    #* === Texts ===
    TEXT_PRIMARY = "#2d3436"
    TEXT_SECONDARY = "#636e72"
    TEXT_WHITE = "#ffffff"
    
    #* === Statuses ===
    STATUS_IDLE = "#b2bec3"
    STATUS_RECORDING = "#ff7675"
    STATUS_THINKING = "#74b9ff"
    STATUS_SUCCESS = "#00b894"
    
    #* === Cards ===
    TASK_ACTIVE_BG = "#0984e3"
    TASK_ACTIVE_TEXT = "#ffffff"
    
    TASK_PAUSED_BG = "transparent"
    TASK_PAUSED_BORDER = "#dfe6e9"
    TASK_PAUSED_TEXT = "#b2bec3"
    
    #* === Calendar Events ===
    CALENDAR_HEADER_BG = "rgba(255, 255, 255, 0.5)"
    CALENDAR_HEADER_BORDER = STATUS_THINKING
    
    EVENT_BG = "rgba(255, 255, 255, 0.85)"
    EVENT_BORDER = "rgba(0, 0, 0, 0.05)"
    
    SUGGEST_BG = "rgba(9, 132, 227, 0.15)"
    
    SELECTED_BG = "rgba(9, 132, 227, 0.4)"
    
STYLESHEET = f"""
/* 全域設定 */
QWidget {{
    font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif; /* 優先使用無襯線字體 */
    font-size: 14px;
    outline: none; /* 移除點擊時的虛線框 */
}}

/* 主視窗容器 - 圓角與背景 */
/* 注意：真正的無邊框視窗需要在 Python code 設定 WindowFlag，這裡負責圓角與顏色 */
QMainWindow, QWidget#CentralWidget {{
    background-color: {Colors.BACKGROUND};
    border-radius: 20px; 
}}

/* 輸入框 (Input Field) */
QTextEdit {{
    background-color: rgba(255, 255, 255, 0.6); /* 比背景更透一點的白色 */
    border: 1px solid #dfe6e9;
    border-radius: 15px; /* 圓潤造型 */
    padding: 5px 15px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.STATUS_THINKING};
}}
QTextEdit:focus {{
    border: 1px solid {Colors.STATUS_RECORDING}; /* 聚焦時變藍 */
    background-color: rgba(255, 255, 255, 0.9);
}}

/* 錄音按鈕 (Record Button) */
/* 這裡只設定基礎，動畫 GIF 會在 Python 中控制 */
QPushButton#recordBtn {{
    background-color: white;
    border: 1px solid #dfe6e9;
    border-radius: 25px; /* 假設按鈕 50x50，半徑 25 變圓形 */
}}
QPushButton#recordBtn:pressed {{
    background-color: #f1f2f6;
    border-color: {Colors.STATUS_RECORDING};
}}

/* 捲軸美化 (可選，讓任務列表捲動時更好看) */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: #dfe6e9;
    min-height: 20px;
    border-radius: 4px;
}}
"""