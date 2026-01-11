from PyQt6.QtWidgets import QFrame, QVBoxLayout
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
    
    def update(self, tasks: list) :
        if self.layout is not None :
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # 如果 tasks 是 None 或空列表，就直接返回，避免錯誤
        if not tasks:
            return
            
        for task in tasks :
            # 核心修正：使用 'status' 鍵取代 'is_active'，並用 'summary' 取代 'task_name'，以符合新的資料結構。
            # 使用 .get() 提供備援值，增加程式碼的穩健性。
            is_active = task.get("status") == "IN_PROGRESS"
            title = task.get("summary", "無標題任務")
            task_card = TaskCard(title=title, is_active=is_active)
            self.layout.addWidget(task_card)