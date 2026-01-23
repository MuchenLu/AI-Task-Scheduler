## 專案架構
```text
SCHEDAI/ # 專案根目錄
|── assets/ # 靜態檔案
    |── images/ # 圖片檔
        |── logo.png # logo
        |── icon.png # 圖標 png 檔
        |── icon.ico # 圖標 icon 檔
        |── record.gif # 錄音 gif 檔
|── config/ # 設定檔
    |── config.py # 設定程式
    |── credentials.json # API 金鑰
|── settings/ # 使用者設定檔
|── utils/ # 工具
    |── logger.py # log 設定
    |── date_helper.py # 日期轉換
    |── format.py # 格式轉換
    |── prompts.py # 提示詞
|── data/ # 本地資料紀錄
    |── history/ # 歷史完成資料紀錄
    |── current.json # 現在進行中任務（狀態為 IN_PROGRESS 或 PAUSED）
|── logs/ # 運行日誌
|── models/ # 後端
    |── llm_client.py # LLM 請求
    |── calendar_sync.py # Calendar 同步
    |── voice_processer.py # 語音處理
    |── json_manager.py # 資料管理
|── views/ # 前端
    |── components/ # 元件
        |── calendar_card.py # 日曆視圖單一事件
        |── record_button.py # 錄音鈕
        |── text_input.py # 文字輸入框
        |── task_card.py # 任務狀態卡
        |── notifi_box.py # 通知框
    |── setup.py # 初始設定視窗
    |── calendar_view.py # 日曆視圖
    |── status_view.py # 任務狀態視圖
    |── main_view.py # 主視窗
|── controller/ # 串接端
    |── voice_controller.py # 語音串接
    |── calendar_controller.py # 日曆串接
    |── llm_controller.py # AI 串接
    |── data_controller.py # 資料串接
|── main.py # 主入口
|── .env
|── .gitignore
|── requirements.txt
|── README.md
```