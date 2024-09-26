from pynasty import *
# Built-in libraries
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import presetlib.utils.qss_setting as qss_setting

reload(qss_setting)

# Ensure the script path is in sys.path
SCRIPT_PATH = 'G:/Tech_Animation/scripts'
if SCRIPT_PATH not in sys.path:
    sys.path.append(SCRIPT_PATH)


# Local modules
#from pynasty import *


class DirSelectDialog(QDialog):
    def __init__(self, dir_list):
        super(DirSelectDialog, self).__init__()
        self.setStyleSheet(qss_setting.DIALOG_QSS)
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet(qss_setting.LISTWIDGET_QSS)
        self.list_widget.addItems(dir_list)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)

        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.ok_button)

        self.setWindowTitle("Please do a Selection...")
        self.setLayout(self.layout)

    def get_selected_item(self):
        return self.list_widget.currentItem().text()
