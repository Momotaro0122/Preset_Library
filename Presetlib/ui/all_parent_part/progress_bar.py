import sys
from pynasty import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# Local.
import presetlib.utils.qss_setting as qss_setting
import presetlib.utils.maya_main_window as maya_main_window

reload(qss_setting)
reload(maya_main_window)


class ProgressBarDialog(QDialog):
    def __init__(self, parent=maya_main_window.get_main_window()):
        super(ProgressBarDialog, self).__init__(parent)

        self.setWindowTitle("Preset Lib Progress Bar")
        self.setFixedSize(300, 100)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Please Wait....")
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progressBar)

        self.setStyleSheet(qss_setting.DIALOG_QSS)
        self.progressBar.setStyleSheet(qss_setting.PROGRESSBOX_QSS)

    def setProgress(self, value):
        self.progressBar.setValue(value)


def simulate_long_task(dialog):
    for i in range(101):
        QTimer.singleShot(i * 50, lambda value=i: dialog.setProgress(value))

"""
dialog = ProgressBarDialog()
dialog.show()

simulate_long_task(dialog)
"""