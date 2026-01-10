from PyQt6.QtWidgets import QFrame, QVBoxLayout
from ui.components.task_card import TaskCard
from ui.styles import Colors

class TaskView(QFrame) :
    def __init__(self, parent = None) :
        super().__init__(parent)
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
            if task["is_active"] == "IN_PROGRESS" :
                task_card = TaskCard(title = task['task_name'], is_active = True)
            else :
                task_card = TaskCard(title = task['task_name'], is_active = False)
            self.layout().addWidget(task_card)