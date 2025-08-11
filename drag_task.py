# drag_task.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QListWidget, 
    QAbstractItemView
)

class DraggableListWidget(QListWidget):
    def __init__(self, tasks_ref, parent=None):
        super().__init__(parent)
        self.tasks_ref = tasks_ref  # Direct reference to the main app's tasks list
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

    def dropEvent(self, event):
        # First, execute the default drag-and-drop behavior (visually moves items)
        super().dropEvent(event)
        
        # Then, reconstruct the internal self.tasks_ref list based on the new visual order
        new_tasks_order = []
        for i in range(self.count()):
            item = self.item(i)
            # Read the original task data we stored in the item
            task_data = item.data(Qt.ItemDataRole.UserRole)
            new_tasks_order.append(task_data)
            
        # Clear and update the original tasks list with the new order
        self.tasks_ref.clear()
        self.tasks_ref.extend(new_tasks_order)
        # Assuming the main app has a way to save data after reordering
        # You might need to add a signal here to trigger saving in the main app
        # For now, this will be handled by explicit calls in other methods if tasks_ref is modified
        # If this is the ONLY place tasks_ref order changes, add self.parent()._save_data()
        # provided parent is PomodoroAppWithTodo and _save_data is public/protected
        if hasattr(self.parent(), '_save_data'): # Check if parent has _save_data method
            self.parent()._save_data()