# sound_player.py
from PyQt6.QtCore import QThread, pyqtSignal
from playsound import playsound
import os

class SoundPlayer(QThread):
    """
    A separate thread for asynchronous sound playback to avoid blocking the main UI thread.
    """
    # Define a signal to notify the main thread when playback is finished (optional, but useful for debugging or future expansion)
    finished_playing = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sound_file_path = None

    def set_sound_file(self, path):
        """Sets the path of the sound file to be played."""
        self.sound_file_path = path

    def run(self):
        """
        This method executes in the new thread.
        When start() is called, QThread automatically runs the code here.
        """
        if self.sound_file_path and os.path.exists(self.sound_file_path):
            try:
                # playsound is blocking, but it's now running in a separate thread,
                # so it won't block the main UI thread.
                playsound(self.sound_file_path)
                self.finished_playing.emit(f"Playback finished: {self.sound_file_path}")
            except Exception as e:
                # Note: Error messages will still be printed to the console
                print(f"Error playing sound in thread: {e}")
                self.finished_playing.emit(f"Playback failed: {self.sound_file_path} - {e}")
        else:
            print(f"Sound file not found or not set: {self.sound_file_path}")
            self.finished_playing.emit(f"File not found or not set: {self.sound_file_path}")

        # The thread automatically terminates after the run() method completes.