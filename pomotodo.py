# pomotodo.py
"""
Main application file for the Pomotodo application.
This file contains the main window class, UI setup, and all application logic.
"""
import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QSizePolicy,
    QMessageBox,
    QDialog,
    QLineEdit,
    QSpinBox,
    QListWidget,
    QListWidgetItem,
    QStyleFactory,
    QAbstractItemView,
    QMenu,
)
from PyQt6.QtCore import QTimer, Qt, QUrl, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QFont, QAction, QCursor, QIcon
from PyQt6.QtSvgWidgets import QSvgWidget

from settings_dialog import SettingsDialog
from edit_task_dialog import EditTaskDialog
from drag_task import DraggableListWidget
from task_widget import TaskWidgetItem


class PomodoroAppWithTodo(QMainWindow):
    """The main window class for the Pomodoro application with a to-do list."""

    def __init__(self):
        """Initializes the application."""
        super().__init__()
        # Load user data on initialization
        self.data_file = "pomodoro_data.json"
        self._load_data()

        self.setWindowTitle("Pomotodo")
        self.setGeometry(1, 1, 1, 1)

        # Timer settings
        self.current_time_left = self.focus_time
        self.is_running = False
        self.current_state = "pomodoro"
        self.completed_pomodoros_in_cycle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.current_task_index = None

        # Sound player setup
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.1)
        self._preload_sounds()

        # Initialize the UI
        self.init_ui()
        self._update_ui_for_state()
        self._update_task_list_display()

    def _load_data(self):
        """Loads user data from JSON file. Initializes with defaults if file is missing or corrupt."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                settings = data.get("settings", {})
                self.tasks = data.get("tasks", [])
                self.focus_time_min = settings.get("focus_time_min", 25)
                self.short_break_time_min = settings.get(
                    "short_break_time_min", 5
                )
                self.long_break_time_min = settings.get(
                    "long_break_time_min", 15
                )
                self.long_break_interval = settings.get(
                    "long_break_interval", 4
                )
                self.dark_mode_enabled = settings.get("dark_mode_enabled", False)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file not found or invalid, set default values
            self.tasks = []
            self.focus_time_min = 25
            self.short_break_time_min = 5
            self.long_break_time_min = 15
            self.long_break_interval = 4
            self.dark_mode_enabled = False
            self._save_data()

        # Convert minutes to seconds for internal timer use
        self.focus_time = self.focus_time_min * 60
        self.short_break_time = self.short_break_time_min * 60
        self.long_break_time = self.long_break_time_min * 60

    def _save_data(self):
        """Saves the current settings and tasks to the JSON file."""
        data = {
            "settings": {
                "focus_time_min": self.focus_time_min,
                "short_break_time_min": self.short_break_time_min,
                "long_break_time_min": self.long_break_time_min,
                "long_break_interval": self.long_break_interval,
                "dark_mode_enabled": self.dark_mode_enabled,
            },
            "tasks": self.tasks,
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _preload_sounds(self):
        """Preloads sound files to ensure they are ready to play without delay."""
        self.focus_end_sound_path = os.path.join(
            os.getcwd(), "sounds", "focus_end.mp3"
        )
        self.break_end_sound_path = os.path.join(
            os.getcwd(), "sounds", "break_end.mp3"
        )
        if os.path.exists(self.focus_end_sound_path):
            self.focus_end_media = QUrl.fromLocalFile(
                self.focus_end_sound_path
            )
        else:
            self.focus_end_media = None
        if os.path.exists(self.break_end_sound_path):
            self.break_end_media = QUrl.fromLocalFile(
                self.break_end_sound_path
            )
        else:
            self.break_end_media = None

    def init_ui(self):
        """Initializes the main user interface and layouts."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        timer_container = self._create_timer_container()
        main_layout.addWidget(timer_container)
        self.todolist_container = self._create_todolist_container()
        main_layout.addWidget(self.todolist_container)
        main_layout.setStretch(1, 1)
        self._update_timer_display()

    def _toggle_dark_mode(self, checked):
        """Toggles dark mode on/off, saves the state, and updates the UI."""
        self.dark_mode_enabled = checked
        self._save_data()
        self._update_ui_for_state()

    def _create_timer_container(self):
        """Creates the top container widget for the timer and controls."""
        timer_container = QWidget()
        timer_container.setObjectName("Card")
        timer_container_layout = QVBoxLayout(timer_container)
        timer_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_container_layout.setContentsMargins(20, 15, 20, 20)
        timer_container_layout.setSpacing(10)
        mode_switch_layout = QHBoxLayout()
        mode_switch_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_switch_layout.setSpacing(10)
        self.pomodoro_mode_btn = QPushButton("Focus")
        self.pomodoro_mode_btn.clicked.connect(lambda: self._set_mode("pomodoro"))
        self.short_break_mode_btn = QPushButton("Short Break")
        self.short_break_mode_btn.clicked.connect(
            lambda: self._set_mode("short_break")
        )
        self.long_break_mode_btn = QPushButton("Long Break")
        self.long_break_mode_btn.clicked.connect(
            lambda: self._set_mode("long_break")
        )
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(40, 30)
        self.settings_menu = QMenu(self)
        dark_mode_action = QAction("Dark Mode", self)
        dark_mode_action.setCheckable(True)
        dark_mode_action.setChecked(self.dark_mode_enabled)
        dark_mode_action.toggled.connect(self._toggle_dark_mode)
        self.settings_menu.addAction(dark_mode_action)
        timer_settings_action = QAction("Timer Settings", self)
        timer_settings_action.triggered.connect(self._open_settings_dialog)
        self.settings_menu.addAction(timer_settings_action)
        self.settings_menu.addSeparator()
        about_action = QAction("About", self)
        about_action.setEnabled(False)
        self.settings_menu.addAction(about_action)
        self.settings_button.setMenu(self.settings_menu)
        for btn in [
            self.pomodoro_mode_btn,
            self.short_break_mode_btn,
            self.long_break_mode_btn,
            self.settings_button,
        ]:
            mode_switch_layout.addWidget(btn)
        timer_container_layout.addLayout(mode_switch_layout)
        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet(
            "font-size: 78px; font-weight: bold; color: white; background: transparent;"
        )
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_container_layout.addWidget(self.timer_label)
        self.current_task_display_label = QLabel("No Task Selected")
        self.current_task_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_task_display_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: white; background: transparent;"
        )
        timer_container_layout.addWidget(self.current_task_display_label)
        timer_buttons_layout = QHBoxLayout()
        timer_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_buttons_layout.setSpacing(10)
        self.start_pause_button = QPushButton("START")
        self.start_pause_button.setFixedSize(120, 40)
        self.start_pause_button.clicked.connect(self._toggle_timer)
        timer_buttons_layout.addWidget(self.start_pause_button)
        self.skip_button = QPushButton("▶▶")
        self.skip_button.setFixedSize(50, 40)
        self.skip_button.clicked.connect(self._skip_current_phase)
        timer_buttons_layout.addWidget(self.skip_button)
        timer_container_layout.addLayout(timer_buttons_layout)
        return timer_container

    def _create_todolist_container(self):
        """Creates the bottom container widget for the to-do list."""
        todolist_container = QWidget()
        todolist_container.setObjectName("Card")

        todolist_layout = QVBoxLayout(todolist_container)
        todolist_layout.setContentsMargins(15, 15, 15, 15)
        todolist_layout.setSpacing(10)

        # Styled "Add Task" layout
        add_task_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("What are you working on?")
        self.task_input.returnPressed.connect(self._add_task)

        self.pomodoro_estimate_input = QSpinBox()
        self.pomodoro_estimate_input.setMinimum(1)
        self.pomodoro_estimate_input.setMaximum(10)
        self.pomodoro_estimate_input.setToolTip("Estimated Pomodoros")
        self.pomodoro_estimate_input.setFixedWidth(40)

        self.add_task_button = QPushButton()
        self.add_task_button.setObjectName("AddTaskButton")
        self.add_task_button.setFixedSize(35, 35)
        self.add_task_button.setIcon(QIcon("icons/plus.svg"))
        self.add_task_button.setIconSize(QSize(18, 18))
        self.add_task_button.clicked.connect(self._add_task)

        add_task_layout.addWidget(self.task_input)
        add_task_layout.addWidget(self.pomodoro_estimate_input)
        add_task_layout.addWidget(self.add_task_button)
        todolist_layout.addLayout(add_task_layout)

        self.task_list_widget = DraggableListWidget(self.tasks, self)
        self.task_list_widget.itemDoubleClicked.connect(self._edit_selected_task)
        self.task_list_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.task_list_widget.customContextMenuRequested.connect(
            self._show_task_context_menu
        )
        self.task_list_widget.itemClicked.connect(self._task_item_clicked)
        todolist_layout.addWidget(self.task_list_widget)

        return todolist_container

    def _update_ui_for_state(self):
        """Applies the appropriate theme based on the current timer state and dark mode setting."""
        active_button_text_color = ""
        if self.dark_mode_enabled:
            main_window_color = "#1c1c1c"
            theme_text_color = "#FFFFFF"
            active_button_text_color = main_window_color
        else:
            if self.current_state == "pomodoro":
                main_window_color, theme_text_color = "#D15A51", "#D15A51"
            elif self.current_state == "short_break":
                main_window_color, theme_text_color = "#51A499", "#51A499"
            else:
                main_window_color, theme_text_color = "#4682B4", "#4682B4"
            active_button_text_color = theme_text_color

        dynamic_stylesheet = f"""
            QMainWindow {{ background-color: {main_window_color}; }}
            QWidget#Card {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            QPushButton {{
                background-color: #FFFFFF; color: {active_button_text_color}; border: none;
                border-radius: 5px; padding: 8px 15px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #f0f0f0; }}
            QPushButton#ModeButton, QPushButton#SettingsButton, QPushButton#SkipButton {{
                background-color: rgba(255, 255, 255, 0.2); color: white;
            }}
            QPushButton#ModeButton:hover, QPushButton#SettingsButton:hover, QPushButton#SkipButton:hover {{
                background-color: rgba(255, 255, 255, 0.3);
            }}
            QLabel {{ color: #FFFFFF; background-color: transparent; }}
            QLineEdit, QSpinBox {{
                background-color: rgba(0, 0, 0, 0.2); color: white;
                border: none; border-radius: 5px; padding: 8px;
                font-size: 14px;
            }}
            QPushButton#AddTaskButton {{
                color: {theme_text_color};
                background-color: white; border-radius: 17px;
            }}
            QPushButton#AddTaskButton:hover {{ background-color: #f0f0f0; }}

            /* === To-Do List Styling === */
            QListWidget {{
                background-color: transparent; border: none;
            }}
            QListWidget::item {{
                border-radius: 8px;
                background-color: transparent;
                padding: 2px 0px;
            }}
            QWidget#TaskItemWidget {{
                background-color: rgba(0, 0, 0, 0.15);
                border-radius: 8px;
                color: white;
                font-size: 14px;
            }}
            QListWidget::item:selected QWidget#TaskItemWidget,
            QListWidget::item:hover QWidget#TaskItemWidget {{
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QLabel#PomodoroCountLabel {{
                color: #cccccc;
                font-size: 12px;
            }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                image: url(icons/circle.svg);
            }}
            QCheckBox::indicator:checked {{
                image: url(icons/check-circle.svg);
            }}

            /* === Scrollbar Styling === */
            QScrollBar:vertical {{
                border: none; background: rgba(0,0,0,0.2);
                width: 10px; margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.3); border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            /* === Menu Styling === */
            QMenu {{
                background-color: #3b3b3b; color: white;
                border: 1px solid #555;
            }}
            QMenu::item:selected {{ background-color: {theme_text_color}; }}
            QMenu::item:disabled {{ color: #777; }}
        """
        self.setStyleSheet(dynamic_stylesheet)

        self.centralWidget().findChild(QWidget).setObjectName("Card")
        self.todolist_container.setObjectName("Card")
        for btn in [
            self.pomodoro_mode_btn,
            self.short_break_mode_btn,
            self.long_break_mode_btn,
        ]:
            btn.setObjectName("ModeButton")
        self.settings_button.setObjectName("SettingsButton")
        self.skip_button.setObjectName("SkipButton")
        active_btn_style = f"background-color: white; color: {active_button_text_color}; border-radius: 5px; padding: 5px 12px;"
        for btn in [
            self.pomodoro_mode_btn,
            self.short_break_mode_btn,
            self.long_break_mode_btn,
        ]:
            btn.setStyleSheet("")
            btn.setObjectName("ModeButton")
        if self.current_state == "pomodoro":
            self.current_time_left = self.focus_time
            self.pomodoro_mode_btn.setStyleSheet(active_btn_style)
        elif self.current_state == "short_break":
            self.current_time_left = self.short_break_time
            self.short_break_mode_btn.setStyleSheet(active_btn_style)
        elif self.current_state == "long_break":
            self.current_time_left = self.long_break_time
            self.long_break_mode_btn.setStyleSheet(active_btn_style)
        self._update_timer_display()
        if not self.is_running:
            self.start_pause_button.setText("START")

    def _add_task(self):
        """Adds a new task to the list from the input fields."""
        task_text = self.task_input.text().strip()
        if not task_text:
            return
        task_data = {
            "text": task_text,
            "estimated": self.pomodoro_estimate_input.value(),
            "completed": 0,
            "done": False,
        }
        self.tasks.append(task_data)
        self.task_input.clear()
        self.pomodoro_estimate_input.setValue(1)
        self._update_task_list_display()
        self._save_data()

    def _update_task_list_display(self):
        """Rebuilds the entire task list using the custom TaskWidgetItem."""
        self.task_list_widget.clear()
        for i, task_data in enumerate(self.tasks):
            task_widget = TaskWidgetItem(task_data)
            task_widget.checkStateChanged.connect(self._task_check_state_changed)
            list_item = QListWidgetItem(self.task_list_widget)
            list_item.setSizeHint(task_widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, i)
            self.task_list_widget.addItem(list_item)
            self.task_list_widget.setItemWidget(list_item, task_widget)
            if i == self.current_task_index:
                self.task_list_widget.setCurrentItem(list_item)

    def _show_task_context_menu(self, pos):
        """Shows a context menu (right-click) for a task item."""
        item = self.task_list_widget.itemAt(pos)
        if not item:
            return
        menu = QMenu()
        edit_action = menu.addAction("✏️ Edit Task")
        delete_action = menu.addAction("🗑️ Delete Task")
        action = menu.exec(QCursor.pos())
        if action == edit_action:
            self._edit_selected_task(item)
        elif action == delete_action:
            self._delete_selected_tasks()

    def _edit_selected_task(self, item):
        """Opens a dialog to edit the selected task."""
        row = self.task_list_widget.row(item)
        if not (0 <= row < len(self.tasks)):
            return
        task_data = self.tasks[row]
        dialog = EditTaskDialog(task_data["text"], task_data["estimated"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_text, new_est = dialog.get_data()
            if not new_text:
                QMessageBox.warning(
                    self, "Invalid Input", "Task description cannot be empty."
                )
                return
            task_data["text"] = new_text
            task_data["estimated"] = new_est
            if task_data["done"] and task_data["completed"] < new_est:
                task_data["done"] = False
            self._update_task_list_display()
            self._save_data()

    def _delete_selected_tasks(self):
        """Deletes all selected tasks after confirmation."""
        selected_items = self.task_list_widget.selectedItems()
        if not selected_items:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the selected {len(selected_items)} task(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            rows_to_delete = sorted(
                [self.task_list_widget.row(item) for item in selected_items],
                reverse=True,
            )
            for row in rows_to_delete:
                if 0 <= row < len(self.tasks):
                    if row == self.current_task_index:
                        self.current_task_index = None
                        self.current_task_display_label.setText(
                            "No Task Selected"
                        )
                    del self.tasks[row]
            self._update_task_list_display()
            self._save_data()

    def keyPressEvent(self, event):
        """Handles key press events for the main window."""
        if (
            event.key() == Qt.Key.Key_Delete
            and self.task_list_widget.hasFocus()
        ):
            self._delete_selected_tasks()
        else:
            super().keyPressEvent(event)

    def _task_item_clicked(self, item):
        """Handles the click event on a task item."""
        self.current_task_index = item.data(Qt.ItemDataRole.UserRole)
        if 0 <= self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index]
            self.current_task_display_label.setText(f"Doing: {task['text']}")

    def _task_check_state_changed(self, widget, is_checked):
        """Handles the check state change signal from a TaskWidgetItem."""
        for i, task in enumerate(self.tasks):
            if (
                self.task_list_widget.itemWidget(self.task_list_widget.item(i))
                is widget
            ):
                if task["done"] == is_checked:
                    return
                task["done"] = is_checked
                if is_checked:
                    task["completed"] = task["estimated"]
                widget.update_visual_state()
                self._save_data()
                break

    def _advance_state_machine(self):
        """Advances the timer to the next state (focus -> break, or break -> focus)."""
        self._toggle_timer_off_if_running()
        previous_state = self.current_state
        if previous_state == "pomodoro":
            self._update_task_progress()
            self.completed_pomodoros_in_cycle += 1
            if (
                self.completed_pomodoros_in_cycle % self.long_break_interval
                == 0
            ):
                self.current_state = "long_break"
            else:
                self.current_state = "short_break"
        else:
            self.current_state = "pomodoro"
            if previous_state == "long_break":
                self.completed_pomodoros_in_cycle = 0
        self._update_ui_for_state()

    def _skip_current_phase(self):
        """Skips the current timer phase and moves to the next one."""
        sound_media = (
            self.focus_end_media
            if self.current_state == "pomodoro"
            else self.break_end_media
        )
        self._play_sound(sound_media)
        self._advance_state_machine()

    def _update_task_progress(self):
        """Increments the completed pomodoros for the current task."""
        if (
            self.current_task_index is not None
            and self.current_task_index < len(self.tasks)
        ):
            task = self.tasks[self.current_task_index]
            if not task["done"]:
                task["completed"] += 1
                if task["completed"] >= task["estimated"]:
                    task["done"] = True
                    QMessageBox.information(
                        self,
                        "Task Completed!",
                        f"Congratulations! You completed the task:\n'{task['text']}'",
                    )
                    self.current_task_index = None
                    self.current_task_display_label.setText(
                        "No Task Selected"
                    )
                self._update_task_list_display()
                self._save_data()

    def _update_timer_display(self):
        """Updates the timer label with the current time left."""
        minutes, seconds = divmod(self.current_time_left, 60)
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def _toggle_timer(self):
        """Starts or pauses the timer."""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.start_pause_button.setText("START")
        else:
            self.timer.start(1000)
            self.is_running = True
            self.start_pause_button.setText("PAUSE")

    def _update_timer(self):
        """Called every second by the QTimer to decrement the time."""
        if self.current_time_left > 0:
            self.current_time_left -= 1
            self._update_timer_display()
        else:
            sound_media = (
                self.focus_end_media
                if self.current_state == "pomodoro"
                else self.break_end_media
            )
            self._play_sound(sound_media)
            self.timer.stop()
            self.is_running = False
            self._advance_state_machine()

    def _set_mode(self, mode):
        """Switches the timer to a specific mode (pomodoro, short_break, long_break)."""
        self._toggle_timer_off_if_running()
        self.current_state = mode
        if mode == "pomodoro":
            self.completed_pomodoros_in_cycle = 0
        self._update_ui_for_state()

    def _toggle_timer_off_if_running(self):
        """Stops the timer if it is currently running."""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.start_pause_button.setText("START")

    def _play_sound(self, media_source: QUrl):
        """Plays a sound from the given media source."""
        if media_source:
            self.media_player.setSource(media_source)
            self.media_player.play()

    def _open_settings_dialog(self):
        """Opens the settings dialog."""
        self._toggle_timer_off_if_running()
        dialog = SettingsDialog(
            self,
            focus_time=self.focus_time_min,
            short_break_time=self.short_break_time_min,
            long_break_time=self.long_break_time_min,
            long_break_interval=self.long_break_interval,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if new_settings := dialog.get_settings():
                new_focus, new_short, new_long, new_interval = new_settings
                (
                    self.focus_time_min,
                    self.short_break_time_min,
                    self.long_break_time_min,
                ) = (new_focus, new_short, new_long)
                (
                    self.focus_time,
                    self.short_break_time,
                    self.long_break_time,
                ) = (new_focus * 60, new_short * 60, new_long * 60)
                self.long_break_interval = new_interval
                self.completed_pomodoros_in_cycle = 0
                self.current_state = "pomodoro"
                self._update_ui_for_state()
                self._save_data()
                QMessageBox.information(
                    self, "Settings Saved", "New settings have been applied!"
                )


if __name__ == "__main__":
    # Create the application instance
    app = QApplication(sys.argv)
    # Apply a modern style
    app.setStyle("Fusion")
    # Create the main window
    window = PomodoroAppWithTodo()
    # Center the window on the primary screen
    if screen := app.primaryScreen():
        screen_geometry = screen.geometry()
        window.move(
            int((screen_geometry.width() - window.width()) / 2),
            int((screen_geometry.height() - window.height()) / 2),
        )
    # Show the window and start the event loop
    window.show()
    sys.exit(app.exec())