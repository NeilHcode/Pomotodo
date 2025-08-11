# edit_task_dialog.py
from PyQt6.QtWidgets import (
    QVBoxLayout, QLineEdit, QDialog, QHBoxLayout,
    QLabel, QSpinBox, QDialogButtonBox
)

class EditTaskDialog(QDialog):
    def __init__(self, current_text, current_est, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task") # Set window title

        layout = QVBoxLayout(self)

        # Task description input field
        self.text_edit = QLineEdit(current_text)
        layout.addWidget(self.text_edit)

        # Estimated Pomodoros spin box
        est_layout = QHBoxLayout()
        est_layout.addWidget(QLabel("Estimated Pomodoros:"))
        self.est_spinbox = QSpinBox()
        self.est_spinbox.setMinimum(1)
        self.est_spinbox.setMaximum(20) # You can adjust the maximum value as needed
        self.est_spinbox.setValue(current_est)
        est_layout.addWidget(self.est_spinbox)
        layout.addLayout(est_layout)

        # OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_data(self):
        """Retrieves the new data from the dialog."""
        return self.text_edit.text().strip(), self.est_spinbox.value()