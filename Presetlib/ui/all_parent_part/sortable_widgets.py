from pynasty import *
# Built-in libraries
import os
import stat
import sys
from functools import partial
import json
import maya.cmds as cmds
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
# Third-party libraries
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance

# Ensure the script path is in sys.path
SCRIPT_PATH = 'G:/Tech_Animation/scripts'
if SCRIPT_PATH not in sys.path:
    sys.path.append(SCRIPT_PATH)

# Local modules
#from pynasty import *
import mayan_utils.ui.qt_column_list as mq
import misc_pub.pyside2_utils as ps2u
import presetlib.functions.presetlib_func as pf
import presetlib.ui.all_parent_part.presetlib_user_input_dailog as pui
import presetlib.ui.all_parent_part.presetlib_frame_lay as presetlib_frame_lay
import presetlib.ui.all_parent_part.delegate as pd
from presetlib.utils.preset_logger import PRESETLIBLogger
import presetlib.utils.qss_setting as qss_setting
import presetlib.ui.all_parent_part.progress_bar as ppb

# Reloading modules to ensure the latest version is in use
reload(presetlib_frame_lay)
reload(ps2u)
reload(mq)
reload(pf)
reload(pui)
reload(pd)
reload(qss_setting)
reload(ppb)

LOCAL_PRESET_BASE = pf.LOCAL_PRESET_BASE
SERVER_PRESET_BASE = pf.SERVER_PRESET_BASE
USER = os.environ.get('TT_USER')
PRESET_DELEGATE = pd.PresetDelegate()
logger = PRESETLIBLogger().get_logger()
# Changed user access to rewrite files.
# os.chmod(SERVER_PRESET_BASE, stat.S_IRWXU)


ParentSelectedRole = Qt.UserRole + 1

class HighlightParentDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.data(ParentSelectedRole):
            option.backgroundBrush = QBrush(QColor("#FFD700"))
        super(HighlightParentDelegate, self).paint(painter, option, index)


# Custom header view class to support sorting
class SortableHeaderView(QHeaderView):
    def __init__(self, parent):
        super(SortableHeaderView, self).__init__(Qt.Horizontal, parent)
        self.setSectionsMovable(True)
        self.setSectionResizeMode(QHeaderView.Stretch)


class SortableListWidget(QWidget):
    def __init__(self, headers=None, sort_at_dept=0, TARIG=False):
        print(TARIG)
        super(SortableListWidget, self).__init__()

        if not headers:
            headers = ['column1', 'column2', 'column3']

        # Define the depth at which clicking the header will sort
        self.sort_at_dept = sort_at_dept

        # Set up the widget layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Initialize and set the tree widget
        self.tree_widget = QTreeWidget()
        if TARIG:
            self.tree_widget.setStyleSheet(qss_setting.TREEWIDGET_LITTLE_QSS)
        else:
            self.tree_widget.setStyleSheet(qss_setting.TREEWIDGET_QSS)
        layout.addWidget(self.tree_widget)
        self.tree_widget.setHeaderLabels(headers)

        # Use the custom header view
        header_view = SortableHeaderView(self.tree_widget)
        self.tree_widget.setHeader(header_view)

        # Enable column header-based sorting
        header_view.setSortIndicatorShown(True)
        header_view.setSectionsClickable(True)
        header_view.sectionClicked.connect(self.sort_items)

        # Store current sorting order for each column
        self.sort_orders = [Qt.AscendingOrder] * len(headers)

        self.export_directory_edit = QLineEdit()

        self.preset_name = None

        self.original_parent_texts = {}

        #self.initialize_style()

    def initialize_style(self):
        self.tree_widget.setStyleSheet("""
            QTreeWidget::item[parent-selected="true"] {
                background-color: #FFD700;  
            }
        """)

    def populate_tree(self, data):
        """Add the given data to the tree."""
        for row in data:
            item = QTreeWidgetItem(self.tree_widget, row)
            self.tree_widget.addTopLevelItem(item)

    def add_item(self, item_data, parent=None):
        """Add an item to the tree. If parent is provided, add as a child."""
        if parent:
            item = QTreeWidgetItem(parent, item_data)
        else:
            item = QTreeWidgetItem(self.tree_widget, item_data)
        self.tree_widget.addTopLevelItem(item)
        return item

    def sort_items(self, column):
        """Sort the items based on the clicked column header."""
        order = self.sort_orders[column]

        # Toggle sort order for the column
        if order == Qt.AscendingOrder:
            self.sort_orders[column] = Qt.DescendingOrder
            sorted_ord = 0
        else:
            self.sort_orders[column] = Qt.AscendingOrder
            sorted_ord = 1

        # Handle sorting based on depth
        if self.sort_at_dept == 0:
            self.tree_widget.sortItems(column, order)
        else:  # NOTE: Sorting at depth greater than 1 hasn't been tested
            dpth = 1
            targets = ps2u.tree_get_toplevel_children(self.tree_widget)
            for branch in targets:
                depth_obj = branch
                while dpth != self.sort_at_dept:
                    try:
                        depth_obj = depth_obj.child(0)
                    except:
                        logger.info(' ')
                    dpth += 1
                ps2u.tree_sort_branch(depth_obj, column, order=sorted_ord)

    def get_obj_list(self, depth=0):
        out_dict = {}
        [out_dict.update({self.tree_widget.topLevelItem(i).text(depth): self.tree_widget.topLevelItem(i)}) for i in
         range(self.tree_widget.topLevelItemCount())]
        return out_dict

    def get_selected(self, *args):
        return self.tree_widget.selectedItems()

    def open(self, no_show=False):
        if not no_show:
            # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()

    def on_item_selected(self):
        selected_items = self.tree_widget.selectedItems()
        maya_objs_to_select = []
        selected_texts = [item.text(0) for item in selected_items]

        for i in range(self.tree_widget.topLevelItemCount()):
            parent = self.tree_widget.topLevelItem(i)
            is_child_selected = False

            for j in range(parent.childCount()):
                child = parent.child(j)
                if child.text(0) in selected_texts:
                    is_child_selected = True
                    break

            if is_child_selected:
                if parent not in self.original_parent_texts:
                    self.original_parent_texts[parent] = parent.text(0)
                parent.setText(0, self.original_parent_texts[parent] + " - Something Selected!")
            else:
                if parent in self.original_parent_texts:
                    parent.setText(0, self.original_parent_texts[parent])

        for item in selected_items:
            if item.parent():
                maya_objs_to_select.append(item.text(0))

    # Slot function to update the directory based on the radio button selection
    def update_directory_path(self):
        if self.local_rad_btn.isChecked():
            self.export_directory_edit.setText(LOCAL_PRESET_BASE)
        elif self.server_rad_btn.isChecked():
            self.export_directory_edit.setText(SERVER_PRESET_BASE)

    def open_export_directory_dialog(self):
        """Open a dialog for selecting the export directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if directory:
            self.export_directory_edit.setText(directory)

    def get_selected_items_text(self):
        """Get the text of the selected items and their parents in the QTreeWidget as a dictionary."""
        selected_items = self.tree_widget.selectedItems()
        items_dict = {}
        for item in selected_items:
            parent_text = item.parent().text(0) if item.parent() else "Root"
            if " - Something Selected!" in parent_text:
                parent_text = parent_text.split(" - Something Selected!")[0]
            if parent_text not in items_dict:
                items_dict[parent_text] = []
            items_dict[parent_text].append(item.text(0))
        return items_dict

    def export_selected_presets(self):
        # Pass the reference of ExportSelectPart to LocalPublishPart
        local_publish_directory_edit = self.export_directory_edit
        base_path = local_publish_directory_edit.text()
        # Pop up a dialog asking the user to enter the preset name
        dialog = pui.UserInputDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.preset_name = dialog.get_input()
        else:
            return

        # Get the selected items from the list widget
        selected_node_names = self.get_selected_items_text()
        total_steps = len(selected_node_names)  # Calculate the total number of steps
        current_step = 0
        # Instantiate ProgressBarDialog
        progressBarDialog = ppb.ProgressBarDialog()
        progressBarDialog.show()
        # Use the Attr_Lib_IO_Tool to save the selected items
        for char_name, node_list in selected_node_names.items():
            result = pf.extract_letters(char_name)
            if result:
                char_name = result
            else:
                logger.info("No match found")
            fin_base_path = base_path
            if self.server_rad_btn.isChecked() and base_path == SERVER_PRESET_BASE:
                fin_base_path = os.path.join(SERVER_PRESET_BASE, char_name, 'work/elems')
                fin_base_path = pf.create_preset_structure(fin_base_path, USER, self.preset_name, char_name)
            else:
                fin_base_path = pf.create_preset_structure(fin_base_path, USER, self.preset_name, char_name)
            logger.info(fin_base_path)
            io_tool = pf.Attr_Lib_IO_Tool(fin_base_path)

            for node_name in node_list:
                io_tool.save_lib_preset(node_name, "")
                # Update progress bar after processing each file
                current_step += 1
                progress_percentage = int((current_step / total_steps))
                progressBarDialog.setProgress(progress_percentage)
                QCoreApplication.processEvents()
        # Ensure progress bar reaches 100% at the end
        progressBarDialog.setProgress(100)
        progressBarDialog.close()
        logger.info("Export preset done")


