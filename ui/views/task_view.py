from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLayout
from PyQt6.QtCore import Qt, QSize
from ui.components.task_card import TaskCard
from ui.styles import Colors

class TaskView(QFrame) :
    def __init__(self, parent = None) :
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BACKGROUND};
                border-radius: 20px;
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        # 關鍵修正 1：靠上對齊。這能防止任務少時卡片被垂直拉伸
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        
        # 關鍵修正 2：設定佈局約束，讓 Widget 的大小嚴格跟隨佈局內容
        self.layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        
        # 關鍵修正 3：設定「一張卡片」的基準寬高。
        # 寬度 300 (卡片寬) + 邊距；高度 120 確保沒內容時也能看到一塊區域
        self.setMinimumWidth(320)
        self.setMinimumHeight(150)
    
    def update(self, tasks: list) :
        # 清除舊內容
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        # 如果沒內容就直接返回，靠 setMinimumHeight 維持基本外觀
        if not tasks:
            self.layout.activate()
            return
            
        for task in tasks:
            is_active = task.get("status") == "IN_PROGRESS"
            title = task.get("summary", "無標題任務")
            task_card = TaskCard(title=title, is_active=is_active)
            self.layout.addWidget(task_card)
        
        # 強制立刻計算佈局
        self.layout.activate()