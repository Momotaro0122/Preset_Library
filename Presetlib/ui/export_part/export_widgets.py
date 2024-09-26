from pynasty import *
# Built-in libraries
import os
import sys
from functools import partial
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# Ensure the script path is in sys.path
SCRIPT_PATH = 'G:/Tech_Animation/scripts'
if SCRIPT_PATH not in sys.path:
    sys.path.append(SCRIPT_PATH)

# Local modules
# ICON-TA
import mayan_utils.ui.qt_column_list as mq
import misc_pub.pyside2_utils as ps2u
# Preset Lib
import presetlib.functions.presetlib_func as pf
import presetlib.ui.all_parent_part.presetlib_frame_lay as presetlib_frame_lay
import presetlib.ui.all_parent_part.delegate as pd
from presetlib.ui.all_parent_part import sortable_widgets
import presetlib.utils.qss_setting as qss_setting
import presetlib.icon.icon_path as icon_path
import presetlib.utils.app_manager as app_manager
from presetlib.utils.preset_logger import PRESETLIBLogger
from presetlib.utils.animated_toggle import SwitchBtn
import presetlib.ui.all_parent_part.progress_bar as ppb

# Reloading modules to ensure the latest version is in use
reload(presetlib_frame_lay)
reload(ps2u)
reload(mq)
reload(pf)
reload(pd)
reload(sortable_widgets)
reload(qss_setting)
reload(icon_path)
reload(app_manager)
reload(ppb)

# Global vars.
LOCAL_PRESET_BASE = pf.LOCAL_PRESET_BASE
SERVER_PRESET_BASE = pf.SERVER_PRESET_BASE
USER = os.environ.get('TT_USER')
app = app_manager.get_app_instance()
logger = PRESETLIBLogger().get_logger()

# Ini.
SortableListWidget = sortable_widgets.SortableListWidget
PRESET_DELEGATE = pd.PresetDelegate()


def refresh_export_selection(sort_wigdet):
    """Refresh export selection."""
    sort_wigdet.clear_items()
    sort_wigdet.populate_from_maya_selection()


def add_custom_export_selection(sort_wigdet):
    sort_wigdet.populate_from_maya_selection()


class ExportSortWidget(SortableListWidget):
    def __init__(self, headers=None, sort_at_dept=0):
        super(ExportSortWidget, self).__init__(headers, sort_at_dept)
        self.export_select_part = self.ExportSelectPart()

    class ExportSelectPart(SortableListWidget):
        """A nested widget class to handle Maya object selection."""
        def __init__(self, parent=None, headers=['Asset', 'Node Type'], TARIG=False):
            super(ExportSortWidget.ExportSelectPart, self).__init__(headers=headers, TARIG=TARIG)
            self.layout = QVBoxLayout(self)
            self.setLayout(self.layout)
            self.tree_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            self.tree_widget.itemSelectionChanged.connect(self.on_item_selected)
            self.export_local_btn = QPushButton("Export Selections")

        def setup_export_path_ui(self, select_part_layout):
            # Radio button for switching server and local
            # Horizontal layout for the radio buttons
            self.radio_btn_layout = QHBoxLayout()

            # Local radio button
            self.local_rad_btn = QRadioButton("Local")
            self.local_rad_btn.setStyleSheet(qss_setting.RADIOBUTTON_QSS)
            local_rad_btn_icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
            self.local_rad_btn.setIcon(local_rad_btn_icon)
            self.radio_btn_layout.addWidget(self.local_rad_btn)

            # Server radio button
            self.server_rad_btn = QRadioButton("Server")
            self.server_rad_btn.setStyleSheet(qss_setting.RADIOBUTTON_QSS)
            local_rad_btn_icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
            self.server_rad_btn.setIcon(local_rad_btn_icon)
            self.radio_btn_layout.addWidget(self.server_rad_btn)

            # Connect the toggled signal of each radio button to the slot function
            self.local_rad_btn.toggled.connect(self.update_directory_path)
            self.server_rad_btn.toggled.connect(self.update_directory_path)
            self.update_directory_path()

            # Add the horizontal layout to the parent layout (e.g., export_layout or select_part_layout)
            # Please replace with the layout you want these buttons to be added to
            select_part_layout.addLayout(self.radio_btn_layout)

            # Directory selection for export
            self.export_dir_h_lay = QHBoxLayout()

            self.export_directory_edit = QLineEdit()
            self.export_directory_edit.setStyleSheet(qss_setting.LINE_EDIT_QSS)

            self.export_directory_browse_btn = QPushButton("Browse", select_part_layout.parentWidget())
            self.export_directory_browse_btn.setStyleSheet(qss_setting.BUTTON_QSS)
            browse_icon = app.style().standardIcon(QStyle.SP_DirIcon)
            self.export_directory_browse_btn.setIcon(browse_icon)
            self.export_directory_browse_btn.clicked.connect(self.open_export_directory_dialog)
            self.export_dir_h_lay.addWidget(self.export_directory_edit)
            self.export_dir_h_lay.addWidget(self.export_directory_browse_btn)
            select_part_layout.addLayout(self.export_dir_h_lay)
            # Set default path for 'Local' option as it's checked by default
            self.export_directory_edit.setText(LOCAL_PRESET_BASE)

            logger.info('Export Tab - server btn open')
            self.server_rad_btn.setChecked(True)

        def setup_select_part_ui(self, select_part_layout):
            """Set up UI components for the Select Part."""

            self.costum_mode_switch_H_lay = QHBoxLayout()
            self.export_custom_check = SwitchBtn(self)
            self.export_custom_lb = QLabel("Export Custom Node Mode")
            self.export_custom_add_btn = QPushButton("Add Custom Node To List")
            self.export_custom_add_btn.clicked.connect(partial(add_custom_export_selection, self))
            self.export_custom_add_btn.setStyleSheet(qss_setting.BUTTON_QSS)
            self.costum_mode_switch_H_lay.addWidget(self.export_custom_check)
            self.costum_mode_switch_H_lay.addWidget(self.export_custom_lb)
            self.costum_mode_switch_H_lay.addWidget(self.export_custom_add_btn)
            select_part_layout.addLayout(self.costum_mode_switch_H_lay)

            # "Refresh Selection" button
            self.export_refresh_btn = QPushButton("Refresh Selection")
            self.export_refresh_btn.setStyleSheet(qss_setting.BUTTON_QSS)
            refresh_btn_icon = QIcon(icon_path.get_icon_path('refresh.png'))
            self.export_refresh_btn.setIcon(refresh_btn_icon)
            self.export_refresh_btn.setIconSize(QSize(32, 32))
            select_part_layout.addWidget(self.export_refresh_btn)
            self.export_refresh_btn.clicked.connect(partial(refresh_export_selection, self))

            self.tree_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            self.tree_widget.itemSelectionChanged.connect(self.on_item_selected)
            select_part_layout.addWidget(self.tree_widget)

            # Horizontal layout for "Select All" and "Deselect All" buttons
            self.export_btn_layout = QHBoxLayout()
            select_part_layout.addLayout(self.export_btn_layout)
            self.export_select_all_btn = QPushButton("Select All")
            self.export_select_all_btn.setStyleSheet(qss_setting.BUTTON_QSS)
            select_all_btn_icon = QIcon(icon_path.get_icon_path('select_all.png'))
            self.export_select_all_btn.setIcon(select_all_btn_icon)
            self.export_select_all_btn.setIconSize(QSize(32, 32))
            self.export_select_all_btn.clicked.connect(self.select_all_items)
            self.export_btn_layout.addWidget(self.export_select_all_btn)

            self.export_deselect_all_btn = QPushButton("Deselect All")
            self.export_deselect_all_btn.setStyleSheet(qss_setting.BUTTON_QSS)
            deselect_all_btn_icon = QIcon(icon_path.get_icon_path('deselect_all.png'))
            self.export_deselect_all_btn.setIcon(deselect_all_btn_icon)
            self.export_deselect_all_btn.setIconSize(QSize(32, 32))
            self.export_deselect_all_btn.clicked.connect(self.deselect_all_items)
            self.export_btn_layout.addWidget(self.export_deselect_all_btn)

            self.export_btn = QPushButton("Export")
            self.export_btn.setStyleSheet(qss_setting.BUTTON_QSS)
            export_btn_icon = QIcon(icon_path.get_icon_path('export_icon.png'))
            self.export_btn.setIcon(export_btn_icon)
            self.export_btn.setIconSize(QSize(32, 32))
            self.export_btn.clicked.connect(self.export_selected_presets)
            select_part_layout.addWidget(self.export_btn)


        def populate_from_maya_selection(self):
            """Fill the widget with Maya's currently selected objects."""
            if self.export_custom_check.checked:
                selected_objects = pf.select_custom_nodes()
            else:
                selected_objects = pf.select_nodes()
            for ns, nodes_dict in selected_objects.items():
                character_ns_item = self.add_item([ns])
                character_ns_item.setFlags(character_ns_item.flags() & ~ Qt.ItemIsSelectable)
                for node, node_type in nodes_dict.items():
                    self.add_item([node, node_type], parent=character_ns_item)
            pf.print_tree_items(self.tree_widget)

        def select_all_items(self):
            # Select all items
            for i in range(self.tree_widget.topLevelItemCount()):
                top_item = self.tree_widget.topLevelItem(i)
                top_item.setSelected(True)
                for j in range(top_item.childCount()):
                    child_item = top_item.child(j)
                    child_item.setSelected(True)

        def deselect_all_items(self):
            # Deselect all items
            for i in range(self.tree_widget.topLevelItemCount()):
                top_item = self.tree_widget.topLevelItem(i)
                top_item.setSelected(False)
                for j in range(top_item.childCount()):
                    child_item = top_item.child(j)
                    child_item.setSelected(False)

        def clear_items(self):
            self.tree_widget.clear()

        def open_export_directory_dialog(self):
            """Open a dialog for selecting the export directory."""
            directory = QFileDialog.getExistingDirectory(self, "Select Export Directory", self.export_directory_edit.text())
            if directory:
                self.export_directory_edit.setText(directory)

    class LocalPublishPart(SortableListWidget):
        """A nested widget class for local publishing of Maya objects."""
        def __init__(self, parent=None, headers=['Asset', 'Node Type'], export_select_part=None):
            super(ExportSortWidget.LocalPublishPart, self).__init__(headers=headers)
            self.tree_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            self.tree_widget.itemSelectionChanged.connect(self.on_item_selected)
            self.export_select_part = export_select_part
            export_select_part_instance = ExportSortWidget.ExportSelectPart()
            self.export_local_btn = export_select_part_instance.export_local_btn
            self.export_directory_edit = export_select_part_instance.export_directory_edit

        def setup_export_ui(self, export_part_layout):
            # Radio button for switching server and local
            # Horizontal layout for the radio buttons
            self.radio_btn_layout = QHBoxLayout()

            # Local radio button
            self.local_rad_btn = QRadioButton("Local")
            self.radio_btn_layout.addWidget(self.local_rad_btn)

            # Server radio button
            self.server_rad_btn = QRadioButton("Server")
            self.radio_btn_layout.addWidget(self.server_rad_btn)

            # Connect the toggled signal of each radio button to the slot function
            self.local_rad_btn.toggled.connect(self.update_directory_path)
            self.server_rad_btn.toggled.connect(self.update_directory_path)
            self.update_directory_path()

            # Assuming you want the 'Local' option to be selected by default
            self.local_rad_btn.setChecked(True)

            # Add the horizontal layout to the parent layout (e.g., export_layout or select_part_layout)
            # Please replace with the layout you want these buttons to be added to
            export_part_layout.addLayout(self.radio_btn_layout)

            # Directory selection for export
            self.export_dir_h_lay = QHBoxLayout()
            self.export_directory_browse_btn = QPushButton("Browse", export_part_layout.parentWidget())
            self.export_directory_browse_btn.clicked.connect(self.open_export_directory_dialog)
            self.export_dir_h_lay.addWidget(self.export_directory_edit)
            self.export_dir_h_lay.addWidget(self.export_directory_browse_btn)
            export_part_layout.addLayout(self.export_dir_h_lay)
            # Set default path for 'Local' option as it's checked by default
            self.export_directory_edit.setText(LOCAL_PRESET_BASE)

            # Tabs within the "Export Part"
            self.export_content_tabs = QTabWidget()
            export_part_layout.addWidget(self.export_content_tabs)

            # "Directly Export" tab
            self.driect_export_tab = QWidget()
            self.driect_export_tab_layout = QVBoxLayout(self.driect_export_tab)
            self.driect_export_tab_layout.addWidget(self.export_local_btn)
            self.export_content_tabs.addTab(self.driect_export_tab, "Directly Export")

            # "Publish From Local" tab
            self.local_tab = QWidget()
            self.local_tab_layout = QVBoxLayout(self.local_tab)
            self.get_local_btn = QPushButton("Get Local Source")
            self.local_tab_layout.addWidget(self.get_local_btn)

            self.export_local_sort_widget = ExportSortWidget.LocalPublishPart()
            self.local_tab_layout.addWidget(self.export_local_sort_widget)
            self.export_content_tabs.addTab(self.local_tab, "Publish From Local")

        def populate_from_maya_selection(self):
            """Fill the widget with Maya's currently selected objects."""
            selected_objects = pf.select_nodes()
            for ns, nodes_dict in selected_objects.items():
                character_ns_item = self.add_item([ns])
                character_ns_item.setFlags(character_ns_item.flags() & ~ Qt.ItemIsSelectable)
                for node, node_type in nodes_dict.items():
                    self.add_item([node, node_type], parent=character_ns_item)
