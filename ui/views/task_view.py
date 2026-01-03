from PyQt6.QtWidgets import QFrame, QVBoxLayout
from ui.components.task_card import TaskCard
from ui.styles import Colors

class TaskView(QFrame) :
    def __init__(self, tasks: list, parent = None) :
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        for task in tasks :
            if task["is_active"] == "IN_PROGRESS" :
                task_card = TaskCard(title = task['task_name'], is_active = True)
            else :
                task_card = TaskCard(title = task['task_name'], is_active = False)
            self.layout().addWidget(task_card)
    
    def update(self, tasks: list) :
        if self.layout is not None :
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        for task in tasks :
            if task["is_active"] == "IN_PROGRESS" :
                task_card = TaskCard(title = task['task_name'], is_active = True)
            else :
                task_card = TaskCard(title = task['task_name'], is_active = False)
            self.layout().addWidget(task_card)