import sys
import threading
import random
import pyautogui
import time
import requests
import uuid
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QWidget, QComboBox, QLabel, QLineEdit, QMessageBox, QInputDialog, QDialog, QTextBrowser, QStatusBar, QHBoxLayout)
from PyQt5.QtCore import pyqtSlot, QTimer

# Function to get the machine's unique ID
def get_machine_id():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])

# Typing simulation thread
class TypingThread(threading.Thread):
    def __init__(self, text, speed_option, error_option, start_delay):
        threading.Thread.__init__(self)
        self.text = text
        self.speed_option = speed_option
        self.error_option = error_option
        self.start_delay = start_delay
        self._stop_event = threading.Event()
        self.characters_typed = 0
        self.errors_made = 0

    def run(self):
        time.sleep(self.start_delay)
        words = self.text.split()

        for word in words:
            if self.stopped():
                break

            for char in word:
                if self.stopped():
                    return

                self.type_char(char)

            self.type_char(' ')

    def type_char(self, char):
        if random.random() < self.error_option:
            pyautogui.write(char, interval=random.uniform(*self.speed_option))
            pyautogui.press('backspace', interval=random.uniform(*self.speed_option))
            self.errors_made += 1

        pyautogui.write(char, interval=random.uniform(*self.speed_option))
        self.characters_typed += 1

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

# About Dialog
class InfoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("About AutoType")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        infoText = QTextBrowser()
        infoText.setHtml("""
            <h1>AutoType</h1>
            <p>Created by Navadeep Budda</p>
            <p>This application was built using PyQt5, pyautogui, and other Python libraries.</p>
            <p>For more information, please visit: <a href='https://example.com'>https://example.com</a></p>
        """)
        layout.addWidget(infoText)

        self.setLayout(layout)

# Main application window
class AutoTypeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.typing_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AutoType by Navadeep Budda')
        self.setGeometry(100, 100, 800, 500)
        layout = QVBoxLayout()

        self.textEdit = QTextEdit()
        self.startButton = QPushButton('Start Typing')
        self.stopButton = QPushButton('Stop Typing', enabled=False)
        self.aboutButton = QPushButton('About')
        self.speedCombo = QComboBox()
        self.speedCombo.addItems(["Fast", "Really Fast", "Extremely Fast"])
        self.errorCombo = QComboBox()
        self.errorCombo.addItems(["Low", "Medium", "High"])
        self.delayLine = QLineEdit("3")
        self.statusBar = QStatusBar()

        layout.addWidget(QLabel('Typing Text'))
        layout.addWidget(self.textEdit)
        layout.addWidget(QLabel('Typing Speed'))
        layout.addWidget(self.speedCombo)
        layout.addWidget(QLabel('Error Variability'))
        layout.addWidget(self.errorCombo)
        layout.addWidget(QLabel('Start Delay (seconds)'))
        layout.addWidget(self.delayLine)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.aboutButton)
        layout.addLayout(buttonLayout)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.setStatusBar(self.statusBar)

        self.startButton.clicked.connect(self.on_start)
        self.stopButton.clicked.connect(self.on_stop)
        self.aboutButton.clicked.connect(self.show_about)

        self.check_license()

    @pyqtSlot()
    def on_start(self):
        text = self.textEdit.toPlainText()
        speed_option = self.get_speed_range()
        error_option = self.get_error_rate()
        start_delay = float(self.delayLine.text())

        self.typing_thread = TypingThread(text, speed_option, error_option, start_delay)
        self.typing_thread.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

        # Timer to update the status bar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Update every second

    @pyqtSlot()
    def on_stop(self):
        if self.typing_thread:
            self.typing_thread.stop()
            self.update_status(final=True)
            self.typing_thread = None

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        if hasattr(self, 'timer'):
            self.timer.stop()

    def update_status(self, final=False):
        if final and self.typing_thread:
            typed = self.typing_thread.characters_typed
            errors = self.typing_thread.errors_made
            self.statusBar.showMessage(f"Typing Finished. Total Characters Typed: {typed}, Total Errors Made: {errors}")
        elif self.typing_thread:
            typed = self.typing_thread.characters_typed
            errors = self.typing_thread.errors_made
            self.statusBar.showMessage(f"Characters Typed: {typed}, Errors Made: {errors}")

    def get_speed_range(self):
        speed_option = self.speedCombo.currentText()
        if speed_option == "Fast":
            return (0.1, 0.15)
        elif speed_option == "Really Fast":
            return (0.05, 0.1)
        else:  # "Extremely Fast"
            return (0.03, 0.05)

    def get_error_rate(self):
        error_text = self.errorCombo.currentText()
        if error_text == "Low":
            return 0.02
        elif error_text == "Medium":
            return 0.05
        elif error_text == "High":
            return 0.1

    def show_about(self):
        aboutDialog = InfoDialog()
        aboutDialog.exec_()

    def check_license(self):
        try:
            with open("license_key.txt", "r") as file:
                saved_key = file.read().strip()
                if saved_key and self.is_key_valid(saved_key, check_only=True):
                    return
            self.prompt_for_license_key()
        except FileNotFoundError:
            self.prompt_for_license_key()

    def is_key_valid(self, key, check_only=False):
        machine_id = get_machine_id()
        response = requests.post("http://127.0.0.1:5000/validate", data={"key": key, "check_only": str(check_only), "machine_id": machine_id})
        if response.status_code == 200:
            return response.json()['valid']
        return False

    def prompt_for_license_key(self):
        key, ok = QInputDialog.getText(self, 'License Key', 'Enter your license key:')
        if ok and key:
            if self.is_key_valid(key):
                with open("license_key.txt", "w") as file:
                    file.write(key)
            else:
                QMessageBox.warning(self, 'Invalid Key', 'The provided license key is invalid.', QMessageBox.Ok)
                sys.exit()
        elif not ok:
            sys.exit()

def main():
    app = QApplication(sys.argv)
    ex = AutoTypeWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
