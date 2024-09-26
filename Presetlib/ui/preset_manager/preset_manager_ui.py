from pynasty import *
import sys
import os
import shutil
from PySide2.QtWidgets import *
import maya.OpenMayaUI
import shiboken2
import PySide2.QtWidgets as qt
import presetlib.utils.qss_setting as qss_setting
import presetlib.utils.app_manager as app_manager
import json
import presetlib.utils.maya_main_window as maya_main_window
import presetlib.functions.presetlib_func as pf

reload(qss_setting)
reload(maya_main_window)
reload(pf)
# Reload app_manager, if necessary
# reload(app_manager)  # For Python 2
# importlib.reload(app_manager)  # For Python 3, add "import importlib" at the top


class RenameDialog(QDialog):
    def __init__(self, parent=None):
        super(RenameDialog, self).__init__(parent)
        self.new_name = ""  # Initialize new_name as empty string
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Rename")
        layout = QVBoxLayout(self)
        self.setStyleSheet(qss_setting.DIALOG_QSS)
        label = QLabel("Enter new name:", self)
        self.line_edit = QLineEdit(self)
        self.line_edit.setStyleSheet(qss_setting.LINE_EDIT_QSS)
        button_layout = QVBoxLayout()
        ok_button = QPushButton("OK", self)
        cancel_button = QPushButton("Cancel", self)
        ok_button.clicked.connect(self.accept_rename)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)
        self.setLayout(layout)

    def accept_rename(self):
        self.new_name = self.line_edit.text()
        if self.new_name:  # Ensure new_name is not empty
            self.accept()  # Close the dialog and return success


class ConfirmDeleteDialog(QDialog):
    def __init__(self, folder_name, parent=None):
        super(ConfirmDeleteDialog, self).__init__(parent)
        self.folder_name = folder_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Confirm Delete")
        self.setStyleSheet(qss_setting.DIALOG_QSS)
        layout = QVBoxLayout(self)
        label = QLabel("Are you sure you want to delete \"{0}\"?".format(self.folder_name), self)
        layout.addWidget(label)
        button_layout = QVBoxLayout()
        yes_button = QPushButton("Yes", self)
        no_button = QPushButton("No", self)
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)
        layout.addWidget(yes_button)
        layout.addWidget(no_button)
        self.setLayout(layout)


class PublishDialog(QDialog):
    def __init__(self, folder_name, parent=None):
        super(PublishDialog, self).__init__(parent)
        self.folder_name = folder_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Confirm Publish")
        self.setStyleSheet(qss_setting.DIALOG_QSS)
        layout = QVBoxLayout(self)
        label = QLabel("Are you sure you want to publish \"{0}\"?".format(self.folder_name), self)
        layout.addWidget(label)
        button_layout = QVBoxLayout()
        yes_button = QPushButton("Yes", self)
        no_button = QPushButton("No", self)
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)
        layout.addWidget(yes_button)
        layout.addWidget(no_button)
        self.setLayout(layout)


class UnPublishDialog(QDialog):
    def __init__(self, folder_name, parent=None):
        super(UnPublishDialog, self).__init__(parent)
        self.folder_name = folder_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Confirm Unpublish")
        self.setStyleSheet(qss_setting.DIALOG_QSS)
        layout = QVBoxLayout(self)
        label = QLabel("Are you sure you want to unpublish \"{0}\"?".format(self.folder_name), self)
        layout.addWidget(label)
        button_layout = QVBoxLayout()
        yes_button = QPushButton("Yes", self)
        no_button = QPushButton("No", self)
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)
        layout.addWidget(yes_button)
        layout.addWidget(no_button)
        self.setLayout(layout)


class ManagerUI(QDialog):
    def __init__(self, parent=maya_main_window.get_main_window(), current_path=""):
        super(ManagerUI, self).__init__(parent)
        for widget in QApplication.allWidgets():
            if widget.objectName() == "preset_manager_ui":
                widget.deleteLater()
        self.setObjectName('preset_manager_ui')
        self.current_path = current_path
        self.history = []  # For tracking the path history
        self.initUI()
        self.update_folder_list()  # Update the folder list at initialization

    def initUI(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet(qss_setting.MAIN_WINDOW_QSS)
        self.back_button = QPushButton("Back", self)  # New button for going back
        self.back_button.setStyleSheet(qss_setting.BUTTON_QSS)
        self.back_button.clicked.connect(self.go_back)

        self.path_edit = QLineEdit(self)
        self.path_edit.setText(self.current_path)
        self.path_edit.setStyleSheet(qss_setting.LINE_EDIT_QSS)

        self.dir_button = QPushButton("Select Directory", self)
        self.dir_button.setStyleSheet(qss_setting.BUTTON_QSS)
        self.dir_button.clicked.connect(self.open_directory_dialog)

        # Layout for the path selection and back button
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.back_button)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.dir_button)

        self.preset_list = QListWidget()
        self.back_button.setStyleSheet(qss_setting.LISTWIDGET_QSS)
        self.preset_list.doubleClicked.connect(self.enter_folder)

        layout.addLayout(path_layout)
        layout.addWidget(self.preset_list)

        self.rename_button = QPushButton("Rename", self)
        self.delete_button = QPushButton("Delete", self)

        self.rename_button.setStyleSheet(qss_setting.BUTTON_QSS)
        self.delete_button.setStyleSheet(qss_setting.BUTTON_QSS)

        self.rename_button.clicked.connect(self.rename_function)
        self.delete_button.clicked.connect(self.delete_function)

        layout.addWidget(self.rename_button)
        layout.addWidget(self.delete_button)
        # if pf.server_user_access():
        self.publish_button = QPushButton("Publish", self)
        self.unpublish_button = QPushButton("Unpublish", self)
        layout.addWidget(self.publish_button)
        layout.addWidget(self.unpublish_button)
        self.publish_button.setStyleSheet(qss_setting.BUTTON_QSS)
        self.unpublish_button.setStyleSheet(qss_setting.BUTTON_QSS)
        self.publish_button.clicked.connect(self.publish_function)
        self.unpublish_button.clicked.connect(self.unpublish_function)

        self.setWindowTitle('Preset Manager')
        self.setGeometry(300, 300, 500, 400)

    def open_directory_dialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.change_directory(directory)

    def update_info_json(self, action, old_name=None, new_name=None):
        info_json_path = os.path.join(self.path_edit.text(), 'info.json')
        if os.path.exists(info_json_path):
            with open(info_json_path, 'r') as file:
                data = json.load(file)

            if action == 'rename' and old_name in data:
                data[new_name] = data.pop(old_name)
            elif action == 'delete' and old_name in data:
                del data[old_name]
            elif action == 'unpublish' and 'publish' in data[old_name].keys():
                data[old_name]['publish'] = False

            with open(info_json_path, 'w') as file:
                json.dump(data, file, indent=4)

    def rename_function(self):
        dialog = RenameDialog(self)
        if dialog.exec_():
            new_name = dialog.new_name
            if new_name:  # Ensure new_name is not empty
                old_name = self.preset_list.currentItem().text()
                if old_name.endswith("---(Published)"):
                    old_name = old_name.replace("---(Published)", "")
                current_path = os.path.join(self.path_edit.text(), old_name)
                parent_dir = os.path.dirname(current_path)
                new_path = os.path.join(parent_dir, new_name)
                try:
                    os.rename(current_path, new_path)
                    self.update_info_json('rename', old_name, new_name)
                    print("Directory renamed successfully.")
                except Exception as e:
                    print("Error renaming directory:", e)
                self.update_folder_list()

    def delete_function(self):
        preset_name = self.preset_list.currentItem().text()
        if preset_name.endswith("---(Published)"):
            preset_name = preset_name.replace("---(Published)", "")
        current_path = os.path.join(self.path_edit.text(), preset_name)
        folder_name = os.path.basename(current_path)
        confirm_dialog = ConfirmDeleteDialog(folder_name, self)
        if confirm_dialog.exec_():
            try:
                shutil.rmtree(current_path)
                self.update_info_json('delete', folder_name)
                QMessageBox.information(self, "Deleted", "\"{0}\" has been deleted successfully.".format(folder_name))
            except Exception as e:
                QMessageBox.critical(self, "Error", "Failed to delete \"{0}\": {1}".format(folder_name, e))
            self.update_folder_list()

    def change_directory(self, directory):
        if os.path.exists(directory):
            self.history.append(self.current_path)  # Save the current path to history
            self.current_path = directory
            self.path_edit.setText(directory)
            self.update_folder_list()

    def update_folder_list(self):
        self.preset_list.clear()  # Clear the list
        if os.path.exists(self.current_path):
            for folder_name in os.listdir(self.current_path):
                folder_path = os.path.join(self.current_path, folder_name)
                info_json_path = os.path.join(self.current_path, "info.json")
                if os.path.exists(info_json_path):
                    if os.path.isdir(folder_path):
                        with open(info_json_path, "r") as f:
                            info_data = json.load(f)
                        publish = pf.preset_publish_checker(info_data, folder_name)
                        if publish is not None:
                            self.preset_list.addItem("{}---({})".format(folder_name, publish))
                        else:
                            if os.path.isdir(folder_path):
                                self.preset_list.addItem(folder_name)
                else:
                    if os.path.isdir(folder_path):
                        self.preset_list.addItem(folder_name)

    def enter_folder(self):
        selected_item = self.preset_list.currentItem()
        if selected_item:
            new_path = os.path.join(self.current_path, selected_item.text())
            self.change_directory(new_path)

    def go_back(self):
        if self.history:
            previous_path = self.history.pop()  # Get and remove the last path from history
            self.current_path = previous_path
            self.path_edit.setText(previous_path)
            self.update_folder_list()

    def publish_function(self):
        preset_name = self.preset_list.currentItem().text()
        if preset_name.endswith("---(Published)"):
            preset_name = preset_name.replace("---(Published)", "")
        current_path = os.path.join(self.path_edit.text(), preset_name)
        current_path = current_path.replace('\\', '/')
        info_json_path = os.path.join(self.path_edit.text(), "info.json")
        info_json_path = info_json_path.replace('\\', '/')
        folder_name = os.path.basename(current_path)
        confirm_dialog = PublishDialog(folder_name, self)
        if confirm_dialog.exec_():
            if not os.path.exists(info_json_path):
                print('asdasdasdas')
                pf.build_info_json_for_old(self.path_edit.text())

            with open(info_json_path, "r") as f:
                info_data = json.load(f)
            info_data[preset_name]["publish"] = True
            with open(info_json_path, "w") as f:
                json.dump(info_data, f, indent=4)
            # self.update_info_json('delete', folder_name)
            QMessageBox.information(self, "Publish", "\"{0}\" has been publish successfully.".format(folder_name))
            try:
                pass
            except Exception as e:
                QMessageBox.critical(self, "Error", "Failed to publish \"{0}\": {1}".format(folder_name, e))
            self.update_folder_list()

    def unpublish_function(self):
        preset_name = self.preset_list.currentItem().text()
        if preset_name.endswith("---(Published)"):
            preset_name = preset_name.replace("---(Published)", "")
        current_path = os.path.join(self.path_edit.text(), preset_name)
        current_path = current_path.replace('\\', '/')
        info_json_path = os.path.join(self.path_edit.text(), "info.json")
        info_json_path = info_json_path.replace('\\', '/')
        folder_name = os.path.basename(current_path)
        confirm_dialog = UnPublishDialog(folder_name, self)
        if confirm_dialog.exec_():
            if os.path.exists(info_json_path):
                try:
                    self.update_info_json('unpublish', preset_name)
                    self.update_folder_list()
                    print("Preset {} unpublish successfully.".format(preset_name))
                except Exception as e:
                    print("Error unpublish directory:", e)
