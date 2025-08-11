# task_widget.py
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont


class TaskWidgetItem(QWidget):
    """
    A custom widget to display a single task in the QListWidget.
    It includes a checkbox, task text, and pomodoro count.
    """

    # Define signals that can be emitted from this widget
    checkStateChanged = pyqtSignal(QObject, bool)  # object, is_checked

    def __init__(self, task_data: dict, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setObjectName("TaskItemWidget")  # For QSS styling

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # 1. Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(task_data.get("done", False))
        # When the checkbox is toggled by the user, emit our custom signal
        self.checkbox.stateChanged.connect(
            lambda: self.checkStateChanged.emit(
                self, self.checkbox.isChecked()
            )
        )
        layout.addWidget(self.checkbox)

        # 2. Task Text Label
        self.task_text_label = QLabel(task_data.get("text", "No Text"))
        self.task_text_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self.task_text_label)

        # 3. Pomodoro Count Label
        pomodoro_count_text = (
            f"{task_data.get('completed', 0)} / {task_data.get('estimated', 1)}"
        )
        self.pomodoro_count_label = QLabel(pomodoro_count_text)
        self.pomodoro_count_label.setObjectName("PomodoroCountLabel")
        layout.addWidget(self.pomodoro_count_label)

        self.setLayout(layout)
        self.update_visual_state()

    def update_visual_state(self):
        """Update font (e.g., strike-through) based on task status."""
        font = QFont()
        if self.task_data.get("done", False):
            font.setStrikeOut(True)
            self.task_text_label.setStyleSheet("color: #888888;")
        else:
            font.setStrikeOut(False)
            self.task_text_label.setStyleSheet("color: white;")
        self.task_text_label.setFont(font)