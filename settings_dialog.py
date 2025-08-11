# settings_dialog.py
"""
Defines the SettingsDialog for configuring application settings.
"""
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QSizePolicy,
    QApplication,
    QSpinBox,
)
from PyQt6.QtCore import Qt
import sys


class SettingsDialog(QDialog):
    """A modal dialog to let the user change timer durations and other settings."""

    def __init__(
        self,
        parent=None,
        focus_time=25,
        short_break_time=5,
        long_break_time=15,
        long_break_interval=4,
    ):
        """Initializes the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("Pomodoro Settings")
        # Set a fixed size to maintain layout consistency
        self.setFixedSize(300, 290)
        # Set as modal to block interaction with the main window
        self.setModal(True)

        # Store the initial values passed from the main window
        self.focus_time_min = focus_time
        self.short_break_time_min = short_break_time
        self.long_break_time_min = long_break_time
        self.long_break_interval = long_break_interval

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """Initializes the UI components of the dialog."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Focus Time Setting
        focus_layout = QHBoxLayout()
        focus_layout.addWidget(QLabel("Focus Time (minutes):"))
        self.focus_input = QLineEdit(str(self.focus_time_min))
        self.focus_input.setPlaceholderText("e.g., 25")
        self.focus_input.setMaximumWidth(80)
        self.focus_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        focus_layout.addWidget(self.focus_input)
        main_layout.addLayout(focus_layout)

        # Short Break Time Setting
        short_break_layout = QHBoxLayout()
        short_break_layout.addWidget(QLabel("Short Break (minutes):"))
        self.short_break_input = QLineEdit(str(self.short_break_time_min))
        self.short_break_input.setPlaceholderText("e.g., 5")
        self.short_break_input.setMaximumWidth(80)
        self.short_break_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        short_break_layout.addWidget(self.short_break_input)
        main_layout.addLayout(short_break_layout)

        # Long Break Time Setting
        long_break_layout = QHBoxLayout()
        long_break_layout.addWidget(QLabel("Long Break (minutes):"))
        self.long_break_input = QLineEdit(str(self.long_break_time_min))
        self.long_break_input.setPlaceholderText("e.g., 15")
        self.long_break_input.setMaximumWidth(80)
        self.long_break_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        long_break_layout.addWidget(self.long_break_input)
        main_layout.addLayout(long_break_layout)

        # Long Break Interval Setting
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Pomodoros before Long Break:"))
        self.interval_input = QSpinBox()
        self.interval_input.setMinimum(2)
        self.interval_input.setMaximum(10)
        self.interval_input.setValue(self.long_break_interval)
        self.interval_input.setMaximumWidth(80)
        self.interval_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        interval_layout.addWidget(self.interval_input)
        main_layout.addLayout(interval_layout)

        # Spacer to push buttons to the bottom
        main_layout.addStretch()

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        button_layout.setSpacing(10)

        self.save_button = QPushButton("Save")
        self.save_button.setFixedSize(80, 30)
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def apply_styles(self):
        """Applies QSS stylesheets to the dialog widgets."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #3b3b3b;
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit, QSpinBox {
                background-color: #555555;
                color: #FFFFFF;
                border: 1px solid #777777;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #d15a51;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e06b60;
            }
            QPushButton#cancel_button {
                background-color: #777777;
            }
            QPushButton#cancel_button:hover {
                background-color: #888888;
            }
        """
        )
        # Set object name to be targeted by the stylesheet
        self.cancel_button.setObjectName("cancel_button")

    def get_settings(self):
        """
        Validates and returns the user-entered settings.
        Returns a tuple of (focus, short, long, interval) on success, or None on failure.
        """
        try:
            focus = int(self.focus_input.text())
            short = int(self.short_break_input.text())
            long = int(self.long_break_input.text())
            interval = self.interval_input.value()

            if focus <= 0 or short <= 0 or long <= 0:
                QMessageBox.warning(
                    self, "Input Error", "All times must be positive integers!"
                )
                return None
            return focus, short, long, interval
        except ValueError:
            QMessageBox.warning(
                self, "Input Error", "Please enter valid numbers for times!"
            )
            return None


# A simple test block to run and display the dialog independently.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Use the correct method name and unpack all values
        settings = dialog.get_settings()
        if settings is not None:
            focus, short, long, interval = settings
            print(f"Saved Focus Time: {focus} minutes")
            print(f"Saved Short Break Time: {short} minutes")
            print(f"Saved Long Break Time: {long} minutes")
            print(f"Saved Long Break Interval: {interval} pomodoros")
    else:
        print("Settings cancelled")
    sys.exit(app.exec())