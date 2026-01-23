"""
./views/setup.py
程式功能：
1. 提供 UI 畫面設定基本資訊
"""

from PyQt6.QtWidgets import QWidget, QProgressBar, QComboBox, QStackedWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QButtonGroup, QRadioButton, QMessageBox
from PyQt6.QtGui import QIcon
import json
import os
from config.config import ICON_ICO, USER_CONFIG
from views.styles import COLORS
from utils.logger import logger
from models.calendar_sync import calendar

class SetupView(QWidget) :
    def __init__(self) :
        super().__init__()
        self.setWindowTitle("SCHEDAI 初始設定")
        self.setWindowIcon(QIcon(str(ICON_ICO)))
        self.resize(800, 500)
        
        self.write_user_config = False
        self.user_config = {}
        
        self.step = None # 起始步驟
        self.complete = False
        self.careers = {"管理與經營": {"企業高階主管 (CEO/總經理)": "MANAGER",
                                      "部門經理 (行銷/研發/人資經理)": "MANAGER",
                                      "中高階公務員/民意代表": "MANAGER",
                                      "創業者/中小企業主": "MANAGER",},
                        "專業/研發人員": {"創業者/中小企業主": "MANAGER",
                                         "醫師/藥師/護理師": "RESPONDER",
                                         "教授/教師/講師": "PERFORMER",
                                         "會計師/財務分析師": "MAKER",
                                         "律師/法官/法務": "MAKER",
                                         "科學家/研究員": "MAKER",
                                         "建築師/設計師 (UI/UX/平面)": "MAKER",
                                         "作家/記者/編輯": "MAKER"},
                        "技術與業務人員": {"業務代表/推銷員 (Sales)": "RESPONDER",
                                          "房地產經紀人/保險業務": "RESPONDER",
                                          "資訊技術支援 (IT Support/網管)": "RESPONDER",
                                          "室內設計/裝修人員": "MAKER",
                                          "採購/報關/船務人員": "MANAGER",
                                          "健身教練/運動員": "PERFORMER"},
                        "行政與客服": {"行政助理/秘書": "MANAGER",
                                      "總務/一般事務人員": "RESPONDER",
                                      "客戶服務/電話客服": "RESPONDER",
                                      "社群小編/數位行銷助理": "MANAGER",
                                      "櫃台接待/總機": "RESPONDER",
                                      "會計助理/出納": "PERFORMER"},
                        "服務、銷售與軍警消": {"商店店員/收銀員": "PERFORMER",
                                             "餐飲服務員/廚師/西點師": "PERFORMER",
                                             "外送員/司機 (計程車/貨運)": "PERFORMER",
                                             "美髮/美容/造型師": "PERFORMER",
                                             "警察/消防員/軍人": "RESPONDER",
                                             "保全/警衛": "PERFORMER",
                                             "導遊/領隊": "PERFORMER"},
                        "學生與其他": {"高中/職學生": "LEARNER",
                                      "大專院校學生": "LEARNER",
                                      "碩/博研究生": "MAKER",
                                      "全職家管 (家庭主婦/夫)": "RESPONDER",
                                      "自由接案者": "MAKER",
                                      "待業中/退休": "LEARNER"}}
        self.calendar_list = []
        self.keys = ["USER_NAME", "CAREER", "AVAILABLE_TIME", "HIGH_EFFICIENCY_TIME", "REST_BUFFER_TIME", "DAILY_TASK_LIMIT", "TASK_DECOMPOSITION", "DEFAULT_TASK_DURATION", "GOOGLE_CALENDAR_ID"]
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.stack = QStackedWidget()
        
        # NOTE: 左側面板用於歡迎及顯示進度
        self.left_panel = QWidget()
        self.left_panel.setObjectName("LeftPanel")
        self.left_panel.setFixedWidth(250)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(40, 60, 40, 40)
        
        self.welcome_title = QLabel("歡迎來到\nSCHEDAI")
        self.welcome_title.setObjectName("LeftTitle")
        self.welcome_title.setWordWrap(True)
        self.process_label = QLabel("初始設定進度")
        self.process_label.setObjectName("ProcessLabel")
        self.process_bar = QProgressBar()
        self.process_bar.setRange(0, 9)
        self.process_bar.setValue(1)
        self.process_bar.setTextVisible(False)
        self.process_bar.setFixedHeight(6)
        self.left_layout.addWidget(self.process_bar)
        self.left_layout.addSpacing(20)
        
        self.process_frame = QWidget()
        self.process_frame.setFixedHeight(200)
        self.left_layout.addWidget(self.welcome_title)
        self.left_layout.addSpacing(20)
        self.left_layout.addWidget(self.process_label)

        self.process_frame_layout = QVBoxLayout(self.process_frame)
        self.process_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.process_frame_layout.setSpacing(0)
        self.step1_indicator = QLabel("1. 設定使用者名稱")
        self.step1_indicator.setObjectName("Step1Indicator")
        self.step2_indicator = QLabel("2. 選擇你的職業")
        self.step2_indicator.setObjectName("Step2Indicator")
        self.step3_indicator = QLabel("3. 設定可安排時間")
        self.step3_indicator.setObjectName("Step3Indicator")
        self.step4_indicator = QLabel("4. 設定高效率時間")
        self.step4_indicator.setObjectName("Step4Indicator")
        self.step5_indicator = QLabel("5. 設定休息緩衝時間")
        self.step5_indicator.setObjectName("Step5Indicator")
        self.step6_indicator = QLabel("6. 設定單日任務上限")
        self.step6_indicator.setObjectName("Step6Indicator")
        self.step7_indicator = QLabel("7. 設定任務拆解方式")
        self.step7_indicator.setObjectName("Step7Indicator")
        self.step8_indicator = QLabel("8. 設定預設任務時長")
        self.step8_indicator.setObjectName("Step8Indicator")
        self.step9_indicator = QLabel("9. Google Calendar ID")
        self.step9_indicator.setObjectName("Step9Indicator")
        self.process_frame_layout.addWidget(self.step1_indicator)
        self.process_frame_layout.addWidget(self.step2_indicator)
        self.process_frame_layout.addWidget(self.step3_indicator)
        self.process_frame_layout.addWidget(self.step4_indicator)
        self.process_frame_layout.addWidget(self.step5_indicator)
        self.process_frame_layout.addWidget(self.step6_indicator)
        self.process_frame_layout.addWidget(self.step7_indicator)
        self.process_frame_layout.addWidget(self.step8_indicator)
        self.process_frame_layout.addWidget(self.step9_indicator)
        self.left_layout.addWidget(self.process_frame)
        self.left_layout.addStretch()
        self.indicators = [self.step1_indicator, self.step2_indicator, self.step3_indicator, self.step4_indicator, self.step5_indicator, self.step6_indicator, self.step7_indicator, self.step8_indicator, self.step9_indicator]
        
        # NOTE: 右側面板第一頁
        self.page1 = QWidget()
        self.page1_layout = QVBoxLayout(self.page1)
        self.page1_layout.setContentsMargins(60, 60, 60, 40)
        self.page1_title = QLabel("怎麼稱呼您？")
        self.page1_title.setObjectName("PageTitle")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("請輸入您的暱稱...")
        # self.name_input.textChanged.connect(lambda text : self.update_user_config("USER_NAME", text))
        self.page1_layout.addWidget(self.page1_title)
        self.page1_layout.addSpacing(20)
        self.page1_layout.addWidget(self.name_input)
        self.page1_layout.addStretch()
        
        # NOTE: 右側面板第二頁
        self.page2 = QWidget()
        self.page2_layout = QVBoxLayout(self.page2)
        self.page2_layout.setContentsMargins(60, 60, 60, 40)
        self.page2_title = QLabel("您的職業是？")
        self.page2_title.setObjectName("PageTitle")
        self.career_type = QComboBox()
        self.career_type.addItems(self.careers.keys())
        self.career_type.setPlaceholderText("請選擇您的職業類型...")
        self.career_type.currentTextChanged.connect(self.update_career_options)
        self.career_job = QComboBox()
        self.career_job.setPlaceholderText("請選擇您的職業...")
        self.page2_layout.addWidget(self.page2_title)
        self.page2_layout.addSpacing(20)
        self.page2_layout.addWidget(self.career_type)
        self.page2_layout.addWidget(self.career_job)
        self.page2_layout.addStretch()
        
        # NOTE: 右側面板第三頁
        self.page3 = QWidget()
        self.page3_layout = QVBoxLayout(self.page3)
        self.page3_layout.setContentsMargins(60, 60, 60, 40)
        self.page3_title = QLabel("您哪些時間可以安排任務？")
        self.page3_title.setObjectName("PageTitle")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("請輸入您的可安排時間...（如有多段時間請以逗號分隔）")
        self.page3_layout.addWidget(self.page3_title)
        self.page3_layout.addSpacing(20)
        self.page3_layout.addWidget(self.time_input)
        self.page3_layout.addStretch()
        
        # NOTE: 右側面板第四頁
        self.page4 = QWidget()
        self.page4_layout = QVBoxLayout(self.page4)
        self.page4_layout.setContentsMargins(60, 60, 60, 40)
        self.page4_title = QLabel("您一天中什麼時間效率最高？")
        self.page4_title.setObjectName("PageTitle")
        self.efficiency_input = QLineEdit()
        self.efficiency_input.setPlaceholderText("請輸入您的高效率時間...（如有多段時間請以逗號分隔）")
        self.page4_layout.addWidget(self.page4_title)
        self.page4_layout.addSpacing(20)
        self.page4_layout.addWidget(self.efficiency_input)
        self.page4_layout.addStretch()
        
        # NOTE: 右側面板第五頁
        self.page5 = QWidget()
        self.page5_layout = QVBoxLayout(self.page5)
        self.page5_layout.setContentsMargins(60, 60, 60, 40)
        self.page5_title = QLabel("您希望任務之間保留多少休息緩衝時間？")
        self.page5_title.setObjectName("PageTitle")
        self.rest_input = QLineEdit()
        self.rest_input.setPlaceholderText("請輸入您的休息緩衝時間...（單位：分鐘）")
        self.page5_layout.addWidget(self.page5_title)
        self.page5_layout.addSpacing(20)
        self.page5_layout.addWidget(self.rest_input)
        self.page5_layout.addStretch()
        
        # NOTE: 右側面板第六頁
        self.page6 = QWidget()
        self.page6_layout = QVBoxLayout(self.page6)
        self.page6_layout.setContentsMargins(60, 60, 60, 40)
        self.page6_title = QLabel("您希望每天安排多少任務？")
        self.page6_title.setObjectName("PageTitle")
        self.total_num_input = QLineEdit()
        self.total_num_input.setPlaceholderText("請輸入您的單日任務上限...")
        self.am_num_input = QLineEdit()
        self.am_num_input.setPlaceholderText("請輸入您的上午任務上限...（選填）")
        self.pm_num_input = QLineEdit()
        self.pm_num_input.setPlaceholderText("請輸入您的下午任務上限...（選填）")
        self.page6_layout.addWidget(self.page6_title)
        self.page6_layout.addSpacing(20)
        self.page6_layout.addWidget(self.total_num_input)
        self.page6_layout.addWidget(self.am_num_input)
        self.page6_layout.addWidget(self.pm_num_input)
        self.page6_layout.addStretch()

        # NOTE: 右側面板第七頁
        self.page7 = QWidget()
        self.page7_layout = QVBoxLayout(self.page7)
        self.page7_layout.setContentsMargins(60, 60, 60, 40)
        self.page7_title = QLabel("您希望如何拆解任務？")
        self.page7_title.setObjectName("PageTitle")
        self.decompose_input = QLineEdit()
        self.decompose_input.setPlaceholderText("請輸入您的任務拆解方式...")
        self.page7_layout.addWidget(self.page7_title)
        self.page7_layout.addSpacing(20)
        self.page7_layout.addWidget(self.decompose_input)
        self.page7_layout.addStretch()

        # NOTE: 右側面板第八頁
        self.page8 = QWidget()
        self.page8_layout = QVBoxLayout(self.page8)
        self.page8_layout.setContentsMargins(60, 60, 60, 40)
        self.page8_title = QLabel("您預設的任務時長為多少？")
        self.page8_title.setObjectName("PageTitle")
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("請輸入您的預設任務時長...（單位：分鐘）")
        self.page8_layout.addWidget(self.page8_title)
        self.page8_layout.addSpacing(20)
        self.page8_layout.addWidget(self.duration_input)
        self.page8_layout.addStretch()
        
        # NOTE: 右側面板第九頁
        self.page9 = QWidget()
        self.page9_layout = QVBoxLayout(self.page9)
        self.page9_layout.setContentsMargins(60, 60, 60, 40)
        self.page9_title = QLabel("請輸入您的 Google Calendar ID")
        self.page9_title.setObjectName("PageTitle")
        self.add_calendar_layout = QHBoxLayout()
        self.calendar_id_input = QLineEdit()
        self.calendar_id_input.setPlaceholderText("請輸入您的 Google Calendar ID...")
        self.add_calendar_id_btn = QPushButton("新增") # NOTE: 同時附帶驗證功能
        self.add_calendar_id_btn.clicked.connect(lambda: self.add_calendar_list(self.calendar_id_input.text()))
        self.page9_layout.addWidget(self.page9_title)
        self.page9_layout.addSpacing(20)
        self.add_calendar_layout.addWidget(self.calendar_id_input)
        self.add_calendar_layout.addWidget(self.add_calendar_id_btn)
        self.page9_layout.addLayout(self.add_calendar_layout)
        self.page9_layout.addSpacing(20)
        self.calendar_check_layout = QGridLayout()
        self.calendar_check_title1 = QLabel("Calendar ID")
        self.calendar_check_title1.setObjectName("CalendarCheckTitle")
        self.calendar_check_title2 = QLabel("新增任務在此 Calendar")
        self.calendar_check_title2.setObjectName("CalendarCheckTitle")
        self.calendar_check_layout.addWidget(self.calendar_check_title1, 0, 0)
        self.calendar_check_layout.addWidget(self.calendar_check_title2, 0, 1)
        # TODO: 動態加入使用者新增的 Calendar ID 與對應的 Checkbox
        self.page9_layout.addLayout(self.calendar_check_layout)
        self.page9_layout.addStretch()
        
        self.inputs = {0: self.name_input,
                       1: self.career_type,
                       2: self.time_input,
                       3: self.efficiency_input,
                       4: self.rest_input,
                       5: self.total_num_input,
                       6: self.decompose_input,
                       7: self.duration_input,
                       8: self.calendar_id_input}

        # NOTE: 底部按鈕區
        self.btn = QWidget()
        self.btn_layout = QHBoxLayout(self.btn)
        self.btn_back = QPushButton("上一步")
        self.btn_back.setObjectName("BackButton")
        self.btn_back.setVisible(False)
        self.btn_back.clicked.connect(self.prev_step)
        self.btn_next = QPushButton("下一步")
        self.btn_next.setObjectName("NextButton")
        self.btn_next.clicked.connect(self.next_step)
        self.btn_layout.addWidget(self.btn_back)
        self.btn_layout.addStretch(1)
        self.btn_layout.addWidget(self.btn_next)
        
        # NOTE: 設定樣式
        self.left_panel.setStyleSheet(f"""#LeftPanel {{
            background-color: {COLORS['sidebar_bg']};
            }}
            #LeftTitle {{
                color: {COLORS['text_dark_primary']};
                font-size: 32px;
                font-weight: bold;
            }}
            #ProcessLabel {{
                color: {COLORS['text_dark_secondary']};
                font-size: 16px;
                line-height: 1.5;
            }}
            #Step1Indicator, #Step2Indicator, #Step3Indicator, #Step4Indicator, #Step5Indicator, #Step6Indicator, #Step7Indicator, #Step8Indicator, #Step9Indicator{{
                color: {COLORS['text_dark_tertiary']};
                font-size: 14px;
                line-height: 1.5;
            }}
            """)
        
        self.step1_indicator.setStyleSheet(f"color: {COLORS['text_dark_accent']};")

        self.page1.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}""")
        
        self.page2.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QComboBox {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}
            QComboBox QAbstractItemView {{
                color: {COLORS['text_muted']};
                background-color: {COLORS['input_bg']};
                selection-background-color: {COLORS['primary']};
                selection-color: {COLORS['text_body']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QComboBox::drop-down {{
                width: 0px;
                border: none;
                image: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
                width: 0px;
                height: 0px;
            }}""")
        
        self.page3.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}""")

        self.page4.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}""")
        
        self.page5.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}""")
        
        self.page6.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}""")
        
        self.page7.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}""")
        
        self.page8.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}""")
        
        self.page9.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #PageTitle {{
                color: {COLORS['text_header']};
                font-size: 28px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {COLORS['input_bg']};
                color: {COLORS['text_body']};
                placeholder-text-color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}
            
            QPushButton {{
                color: {COLORS["neutral_text"]};
                border: 1px solid {COLORS["neutral_border"]};
                font-size: 16px;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["neutral_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {COLORS["neutral_pressed"]};
            }}
            
            #CalendarCheckTitle {{
                color: {COLORS['text_header']};
                font-size: 16px;
            }}""")

        self.btn.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['content_bg']};
            }}
            #BackButton {{
                background-color: {COLORS['neutral_border']};
                color: {COLORS['neutral_text']};
                font-size: 16px;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            #BackButton:hover {{
                background-color: {COLORS['neutral_hover']};
            }}
            #BackButton:pressed {{
                background-color: {COLORS['neutral_pressed']};
            }}
            #NextButton {{
                background-color: {COLORS['success_bg']};
                color: white;
                font-size: 16px;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            #NextButton:hover {{
                background-color: {COLORS['success_hover']};
            }}
            #NextButton:pressed {{
                background-color: {COLORS['success_pressed']};
            }}""")
        
        # NOTE: 將所有頁面加入堆疊視圖
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)
        self.stack.addWidget(self.page4)
        self.stack.addWidget(self.page5)
        self.stack.addWidget(self.page6)
        self.stack.addWidget(self.page7)
        self.stack.addWidget(self.page8)
        self.stack.addWidget(self.page9)
        self.stack.setCurrentIndex(0)
        self.main_layout.addWidget(self.left_panel)
        self.content_layout.addWidget(self.stack)
        self.content_layout.addWidget(self.btn)
        self.main_layout.addLayout(self.content_layout)
        self.setLayout(self.main_layout)
        
        self.update_process_indicators()
        self.update_btns()
    
    def next_step(self) :
        self.step = self.stack.currentIndex()
        if not self.update_user_config() :
            return
        if self.step < self.stack.count() - 1 :
            self.stack.setCurrentIndex(self.step + 1)
        else :
            self.close()
        self.update_process_indicators()
        self.update_btns()

    def prev_step(self) :
        self.step = self.stack.currentIndex()
        if self.step > 0 :
            self.stack.setCurrentIndex(self.step - 1)
        self.update_process_indicators()
        self.update_btns()
    
    def update_process_indicators(self) :
        self.step = self.stack.currentIndex()
        for i in range(len(self.indicators)) :
            if i < self.step :
                self.indicators[i].setStyleSheet(f"color: {COLORS['text_dark_secondary']};")
                if i == self.step - 1 :
                    self.indicators[i].setVisible(True)
                else :
                    self.indicators[i].setVisible(False)
            elif i == self.step :
                self.indicators[i].setStyleSheet(f"color: {COLORS['text_dark_accent']};")
            else :
                self.indicators[i].setStyleSheet(f"color: {COLORS['text_dark_tertiary']};")
                if i == self.step + 1:
                    self.indicators[i].setVisible(True)
                else :
                    self.indicators[i].setVisible(False)
        self.indicators[0].setVisible(True)
        self.indicators[-1].setVisible(True)
        self.process_bar.setValue(self.step)
    
    def update_btns(self) :
        self.step = self.stack.currentIndex()
        if self.step == 0 :
            self.btn_back.setVisible(False)
        else :
            self.btn_back.setVisible(True)
        
        if self.step == self.stack.count() - 1 :
            self.btn_next.setText("完成")
            self.write_user_config = True
            self.complete = True
        else :
            self.btn_next.setText("下一步")
            self.write_user_config = False
    
    def update_career_options(self, text) :
        self.career_job.clear()
        jobs = self.careers.get(text, {})
        self.career_job.addItems(jobs.keys())
        self.career_job.setPlaceholderText("請選擇您的職業...")
    
    def add_calendar_list(self, calendar_id) :
        self.calendar_id_input.setText("")
        status = calendar.valiadate_calendar(calendar_id)
        match status :
            case 200 :
                pass
            case 404 :
                QMessageBox.critical(self, "新增錯誤", "日曆 ID 不存在")
                logger.warning(f"Calendar ID 不存在: {calendar_id}")
                return
            case 403 :
                QMessageBox.critical(self, "新增錯誤", "無法存取此日曆")
                logger.error(f"無法存取 {calendar_id} 日曆")
                return
            case _ :
                QMessageBox.critical(self, "新增錯誤", "新增日曆時出現未知錯誤")
                logger.error(f"新增 {calendar_id} 時出現未知錯誤")
                return
            
        self.calendar_list.append(calendar_id)
        row = self.calendar_check_layout.rowCount()
        calendar_label = QLabel(calendar_id)
        calendar_label.setWordWrap(True)
        calendar_label.setObjectName("CalendarCheckLabel")
        calendar_checkbox = QRadioButton()
        calendar_checkbox.setObjectName("CalendarCheckButton")
        calendar_delete_btn = QPushButton("刪除")
        calendar_delete_btn.setObjectName("CalendarDeleteButton")
        calendar_delete_btn.clicked.connect(lambda: self.delete_calendar_list(calendar_id))
        self.calendar_check_layout.addWidget(calendar_label, row, 0)
        self.calendar_check_layout.addWidget(calendar_checkbox, row, 1)
        self.calendar_check_layout.addWidget(calendar_delete_btn, row, 2)
        calendar_label.setFixedWidth(200)
        calendar_label.setStyleSheet(f"""#CalendarCheckLabel {{
            color: {COLORS['text_body']};
            font-size: 14px;
        }}""")
        calendar_checkbox.setStyleSheet(f"""#CalendarCheckButton {{
            spacing: 0px;
            padding: 0px; 
        }}
        #CalendarCheckButton::indicator {{
            width: 20px;
            height: 20px;
            background-color: transparent;
            border: 1px solid {COLORS['border']};
            border-radius: 11px;
            border-color: {COLORS['border']};
        }}
        #CalendarCheckButton::indicator:hover {{
            border-color: {COLORS['primary']};
            background-color: transparent;
        }}
        #CalendarCheckButton::indicator:checked {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['primary']};
        }}""")
        calendar_delete_btn.setFixedWidth(100)
        calendar_delete_btn.setStyleSheet(f"""#CalendarDeleteButton {{
            color: white;
            background: {COLORS['danger_bg']};
            font-size: 14px;
            padding: 8px 16px;
            border-radius: 8px;
        }}
        #CalendarDeleteButton:hover {{
            background-color: {COLORS['danger_hover']};
        }}
        #CalendarDeleteButton:pressed {{
            background-color: {COLORS['danger_pressed']};
        }}""")
    
    def delete_calendar_list(self, calendar_id) :
        self.calendar_list.remove(calendar_id)
        for i in range(self.calendar_check_layout.count()) :
            if self.calendar_check_layout.itemAt(i).widget().text() == calendar_id :
                row = self.calendar_check_layout.getItemPosition(i)[0]
                for j in range(self.calendar_check_layout.columnCount()) :
                    item = self.calendar_check_layout.itemAtPosition(row, j)
                    if item :
                        widget = item.widget()
                        self.calendar_check_layout.removeWidget(widget)
                        widget.deleteLater()
                break
    
    def update_user_config(self) :
        obj = self.inputs.get(self.step, [])
        if isinstance(obj, QLineEdit) :
            value = obj.text()
        elif isinstance(obj, QComboBox) :
            value = obj.currentText()
        if obj == self.career_type :
            career_job = self.career_job.currentText()
            career_code = self.careers.get(value, {}).get(career_job, "")
            if career_code :
                self.user_config[self.keys[self.step]] = career_code
                value = career_code
        if not value :
            QMessageBox.warning(self, "輸入錯誤", "請填寫所有欄位後再進行下一步。")
            self.stack.setCurrentIndex(self.step)
            return False
        else :
            self.user_config[self.keys[self.step]] = value
        
        if self.write_user_config :
            with open(USER_CONFIG, "w", encoding="utf-8") as f :
                json.dump(self.user_config, f, ensure_ascii=False, indent=4)
            logger.info("使用者設定檔已更新。")
        
        return True

    def closeEvent(self, event) :
        if self.complete :
            event.accept()
        else :
            accept = QMessageBox.question(self, "設定未完成", "參數尚未設定完成，是否關閉視窗？")
            if accept == QMessageBox.StandardButton.Yes :
                event.accept()
            else :
                event.ignore()