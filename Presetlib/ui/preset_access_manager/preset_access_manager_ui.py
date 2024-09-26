from pynasty import *
import sys
import os
import shutil
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import maya.OpenMayaUI
import shiboken2
import PySide2.QtWidgets as qt
import presetlib.utils.qss_setting as qss_setting
import presetlib.utils.app_manager as app_manager
import json
import presetlib.utils.maya_main_window as maya_main_window
import presetlib.functions.presetlib_func as pf
from presetlib.utils.preset_logger import PRESETLIBLogger
from functools import partial

reload(qss_setting)
reload(maya_main_window)
reload(pf)

logger = PRESETLIBLogger().get_logger()
ACCESS_JSON_BASE = "G:/Tech_Animation/preference"
ACCESS_USER_LIST = os.listdir(ACCESS_JSON_BASE)

class AccessManagerUI(QDialog):
    def __init__(self, parent=maya_main_window.get_main_window(), current_path=""):
        super(AccessManagerUI, self).__init__(parent)
        for widget in QApplication.allWidgets():
            if widget.objectName() == "preset_access_manager_ui":
                widget.deleteLater()
        self.setObjectName('preset_access_manager_ui')
        self.current_path = current_path
        self.history = []  # For tracking the path history
        self.initUI()
        self.list_name_fill()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet(qss_setting.MAIN_WINDOW_QSS)
        # Layout for the path selection and back button
        path_layout = QHBoxLayout()

        self.search_edit = QLineEdit(self)  # New search bar
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.setStyleSheet(qss_setting.LINE_EDIT_QSS)

        self.preset_list = QListView()  # Change QListWidget to QListView
        self.preset_list.setStyleSheet(qss_setting.LISTWIDGET_QSS)

        layout.addLayout(path_layout)
        layout.addWidget(self.search_edit)
        layout.addWidget(self.preset_list)

        self.rename_button = QPushButton("Give Access", self)
        self.delete_button = QPushButton("Remove Access", self)

        self.rename_button.setStyleSheet(qss_setting.BUTTON_QSS)
        self.delete_button.setStyleSheet(qss_setting.BUTTON_QSS)

        self.rename_button.clicked.connect(partial(self._access, access='give'))
        self.delete_button.clicked.connect(partial(self._access, access='remove'))

        layout.addWidget(self.rename_button)
        layout.addWidget(self.delete_button)

        self.setWindowTitle('Preset Access Manager')
        self.setGeometry(300, 300, 500, 400)

        # Connecting the search bar to the filter function
        self.search_edit.textChanged.connect(self.filter_list)

    def filter_list(self):
        filter_text = self.search_edit.text().lower()
        self.proxy_model.setFilterFixedString(filter_text)

    def list_name_fill(self):
        model = QStandardItemModel()
        for user_name in ACCESS_USER_LIST:
            access_user_path = os.path.join(ACCESS_JSON_BASE, user_name, 'preset_access.json')
            if pf.server_user_access(access_user_path):
                item_text = "{} - (Have Access!)".format(user_name)
                item_a = QStandardItem(item_text)
                item_a.setForeground(QBrush(QColor("#D4AF37")))
                item_a.setBackground(QBrush(QColor("#808080")))
                font = QFont("Arial", 14, QFont.Bold)
                item_a.setFont(font)
                model.appendRow(item_a)
            else:
                item_a = QStandardItem(user_name)
                model.appendRow(item_a)

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns
        self.preset_list.setModel(self.proxy_model)

    def _access(self, access='give'):
        user = self.preset_list.currentIndex().data()
        if user.endswith('(Have Access!)'):
            user = user.split(' - ')[0]
        access_user_path = os.path.join(ACCESS_JSON_BASE, user, 'preset_access.json')
        if os.path.exists(access_user_path) and os.path.getsize(access_user_path) > 0:
            with open(access_user_path, 'r') as f:
                json_data = json.load(f)
        else:
            json_data = {}
        if access == 'give':
            json_data['access'] = True
            logger.info("Preset access created for: {}".format(user))
        else:
            json_data['access'] = False
            logger.info("Preset access removed for: {}".format(user))
        with open(access_user_path, "w") as f:
            json.dump(json_data, f, indent=4)
        self.list_name_fill()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AccessManagerUI()
    window.show()
    sys.exit(app.exec_())
