# Built-in libraries
import os
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# Third-party libraries
from pynasty import *

# Ensure the script path is in sys.path
# SCRIPT_PATH = 'G:/Tech_Animation/scripts'
# if SCRIPT_PATH not in sys.path:
#    sys.path.append(SCRIPT_PATH)

import mayan_utils.ui.qt_column_list as mq
import misc_pub.pyside2_utils as ps2u
import presetlib.functions.presetlib_func as pf
import presetlib.ui.all_parent_part.presetlib_frame_lay as presetlib_frame_lay
import presetlib.ui.all_parent_part.delegate as pd
from presetlib.ui.all_parent_part import sortable_widgets
from presetlib.ui.export_part import export_widgets
from presetlib.ui.import_part import import_widgets
from presetlib.ui.edit_part import edit_widgets
import presetlib.utils.qss_setting as qss_setting
import presetlib.utils.app_manager as app_manager
import presetlib.utils.maya_main_window as maya_main_window

# Reloading modules to ensure the latest version is in use
reload(presetlib_frame_lay)
reload(ps2u)
reload(mq)
reload(pf)
reload(pd)
reload(sortable_widgets)
reload(export_widgets)
reload(import_widgets)
reload(edit_widgets)
reload(qss_setting)
reload(app_manager)
reload(maya_main_window)

# Global vars.
LOCAL_PRESET_BASE = pf.LOCAL_PRESET_BASE
SERVER_PRESET_BASE = pf.SERVER_PRESET_BASE
USER = os.environ.get('TT_USER')

# Class.
SortableListWidget = sortable_widgets.SortableListWidget
ExportSortWidget = export_widgets.ExportSortWidget
ImportSortWidget = import_widgets.ImportSortWidget
EditWidget = edit_widgets.AnimationLayerEditor

# Ini.
PRESET_DELEGATE = pd.PresetDelegate()

# Info.
__author__ = "Martin Lee"
__copyright__ = "Copyright 2023, The greatest cfx department"
__credits__ = ["Martin Lee", "Perry Hsieh", "Tony Yu", "Damon Lavenski"]
__license__ = ""
__version__ = "2.8.5"
__maintainer__ = "Martin Lee"
__email__ = "martinle@iconcreativestudio.com"
__status__ = "CFX"

class MainPresetLibUI(QMainWindow):
    def __init__(self, parent=maya_main_window.get_main_window(), TARIG=False):
        super(MainPresetLibUI, self).__init__(parent)
        self.TARIG = TARIG
        for widget in QApplication.allWidgets():
            if widget.objectName() == "presetlib_ui":
                widget.deleteLater()
        self.setObjectName('presetlib_ui')
        if TARIG:
            self.setStyleSheet(qss_setting.MAIN_LITTLE_WINDOW_QSS)
        else:
            self.setStyleSheet(qss_setting.MAIN_WINDOW_QSS)
        self.setWindowTitle("Preset Lib")
        self.resize(850, 800)
        # Set central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Initialize the tabs widget
        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        # Set up individual tabs
        self.setup_import_tab()
        self.setup_export_tab()
        self.setup_edit_tab()
        self.setup_tab_widget_size()

        self.presetlib_vcs_lb = QLabel("Preset Lib V{}".format(__version__))
        self.presetlib_vcs_lb.setStyleSheet("font-size: 8pt;")
        self.presetlib_vcs_lb.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.presetlib_vcs_lb)

    def setup_import_tab(self):
        """Set up the Import tab."""
        self.import_tab = QWidget()
        self.import_layout = QVBoxLayout(self.import_tab)
        self.import_sort_widget = ImportSortWidget(TARIG=self.TARIG)
        self.import_layout.addWidget(self.import_sort_widget)
        self.tabs.addTab(self.import_tab, "Import")

    def setup_edit_tab(self):
        """Set up the Edit tab."""
        self.edit_tab = QWidget()
        self.edit_layout = QVBoxLayout(self.edit_tab)
        self.edit_list_widgets = EditWidget(TARIG=self.TARIG)
        if pf.check_shot_asset() == 'Shot':
            self.edit_layout.addWidget(self.edit_list_widgets)
        else:
            self.edit_layout_lb = QLabel("This function only allow to use in shot...")
            self.edit_layout.addWidget(self.edit_layout_lb)
        self.tabs.addTab(self.edit_tab, "Edit")

    def setup_export_tab(self):
        """Set up the Export tab."""
        self.export_tab = QWidget()
        self.export_layout = QVBoxLayout(self.export_tab)

        # ------- Select Part Setup -------
        self.export_select_fl = presetlib_frame_lay.FrameLayout(title="Select Part")
        if self.export_select_fl._is_collasped:
            self.export_select_fl.toggleCollapsed()
        self.select_part_group = QGroupBox("Select Part")
        self.select_part_layout = QVBoxLayout(self.select_part_group)
        self.export_select_sort_widget = ExportSortWidget.ExportSelectPart(TARIG=self.TARIG)
        self.export_select_sort_widget.setup_export_path_ui(self.export_layout)
        self.export_select_sort_widget.setup_select_part_ui(self.export_layout)

        # ------- Export Part Setup -------
        self.export_export_fl = presetlib_frame_lay.FrameLayout(title="Export Part")
        self.export_export_fl._is_collasped = False
        self.export_part_group = QGroupBox("Export Part")
        self.export_part_layout = QVBoxLayout(self.export_part_group)
        self.export_sort_widget = ExportSortWidget.LocalPublishPart()
        self.export_sort_widget.setup_export_ui(self.export_part_layout)

        # Add the main Export tab to the main tabs widget
        self.tabs.addTab(self.export_tab, "Export")

    def setup_tab_widget_size(self):
        tab_count = self.tabs.count()
        tab_width = self.tabs.width() / (tab_count-0.69)
        self.tabs.setStyleSheet("QTabBar::tab { min-width: %dpx; }" % tab_width)

""" Execute """
if __name__ == "__main__":
    app = app_manager.get_app_instance()
    win = MainPresetLibUI()
    win.show()
