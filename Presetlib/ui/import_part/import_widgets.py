from pynasty import *
# Built-in libraries
import os
import sys
import json

import maya.cmds as cmds
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# Ensure the script path is in sys.path
SCRIPT_PATH = 'G:/Tech_Animation/scripts'
if SCRIPT_PATH not in sys.path:
    sys.path.append(SCRIPT_PATH)

# Local modules
# from pynasty import *
import presetlib.functions.presetlib_func as pf
import presetlib.ui.all_parent_part.delegate as pd
import presetlib.ui.all_parent_part.list_dialog as pl
from presetlib.ui.all_parent_part import sortable_widgets
from presetlib.ui.export_part import export_widgets
from presetlib.ui.import_part import preset_path_dailog
from presetlib.utils.preset_logger import PRESETLIBLogger
import presetlib.utils.qss_setting as qss_setting
import presetlib.utils.app_manager as app_manager
import presetlib.icon.icon_path as icon_path
import presetlib.ui.all_parent_part.progress_bar as ppb
import presetlib.ui.preset_manager.preset_manager_ui as preset_manager_ui
import presetlib.ui.preset_access_manager.preset_access_manager_ui as preset_access_manager_ui
from presetlib.utils.animated_toggle import SwitchBtn

# Reloading modules to ensure the latest version is in use
reload(pf)
reload(pd)
reload(pl)
reload(sortable_widgets)
reload(export_widgets)
reload(preset_path_dailog)
reload(qss_setting)
reload(app_manager)
reload(icon_path)
reload(ppb)

# Global vars.
ACCESS_JSON_BASE = "G:/Tech_Animation/preference"
LOCAL_PRESET_BASE = pf.LOCAL_PRESET_BASE
SERVER_PRESET_BASE = pf.SERVER_PRESET_BASE
DATA_DUMP_PATH = pf.DATA_DUMP_PATH
USER = os.environ.get('TT_USER')
app = app_manager.get_app_instance()
CURRENT_PATH = []

# Class.
SortableListWidget = sortable_widgets.SortableListWidget

# Ini.
PRESET_DELEGATE = pd.PresetDelegate()

preset_path_dailog = preset_path_dailog.preset_path_dailog
logger = PRESETLIBLogger().get_logger()


class ImportSortWidget(SortableListWidget):
    def __init__(self, parent=None, headers=['Node', 'Node Type'], TARIG=False):
        super(ImportSortWidget, self).__init__(headers=headers, TARIG=TARIG)
        self.PRESET_DELEGATE = pd.PresetDelegate(self)
        self.tree_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selected_hint)
        self.path_edit = QLineEdit()
        self.path_edit.setStyleSheet(qss_setting.LINE_EDIT_QSS)
        # Radio button for switching server and local
        # Horizontal layout for the radio buttons
        self.radio_btn_layout = QHBoxLayout()

        self.server_local_group = QButtonGroup(self)
        self.node_attribute_group = QButtonGroup(self)

        # Local radio button
        self.local_rad_btn = QRadioButton("Local")
        self.local_rad_btn.setStyleSheet(qss_setting.RADIOBUTTON_QSS)
        local_rad_btn_icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
        self.local_rad_btn.setIcon(local_rad_btn_icon)
        self.radio_btn_layout.addWidget(self.local_rad_btn)

        # Server radio button
        self.server_rad_btn = QRadioButton("Server")
        self.server_rad_btn.setStyleSheet(qss_setting.RADIOBUTTON_QSS)
        server_rad_btn_icon = app.style().standardIcon(QStyle.SP_DriveHDIcon)
        self.server_rad_btn.setIcon(server_rad_btn_icon)
        self.radio_btn_layout.addWidget(self.server_rad_btn)

        self.server_local_group.addButton(self.local_rad_btn)
        self.server_local_group.addButton(self.server_rad_btn)

        # Connect the toggled signal of each radio button to the slot function
        self.local_rad_btn.toggled.connect(self.update_directory_path)
        self.server_rad_btn.toggled.connect(self.update_directory_path)

        # Assuming you want the 'Local' option to be selected by default
        self.server_rad_btn.setChecked(True)

        # Initialize and set up a QLineEdit for directory path input
        self.path_edit = QLineEdit(self)
        self.path_edit.setStyleSheet(qss_setting.LINE_EDIT_QSS)
        # Set default path for 'Local' option as it's checked by default
        self.path_edit.setText(LOCAL_PRESET_BASE)
        self.update_directory_path()

        # Initialize and set up a QPushButton for browsing directories
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.setStyleSheet(qss_setting.BUTTON_QSS)
        browse_icon = app.style().standardIcon(QStyle.SP_DirIcon)
        self.browse_button.setIcon(browse_icon)
        self.browse_button.clicked.connect(self.open_directory_dialog)

        # Create and set a horizontal layout for QLineEdit and QPushButton
        self.path_layout = QHBoxLayout()
        self.path_layout.addWidget(self.path_edit)
        self.path_layout.addWidget(self.browse_button)

        # Load button.
        self.v_lay = QVBoxLayout()
        self.import_load_btn = QPushButton("Load")
        self.import_load_btn.clicked.connect(self.load_import)
        load_btn_icon = app.style().standardIcon(QStyle.SP_ToolBarVerticalExtensionButton)
        self.import_load_btn.setIcon(load_btn_icon)
        self.import_load_btn.setStyleSheet(qss_setting.BUTTON_QSS)
        self.v_lay.addWidget(self.import_load_btn)

        self.import_char_v_lay = QVBoxLayout()
        self.import_preset_v_lay = QVBoxLayout()
        self.import_char_lb = QLabel("Characters")
        self.import_char_cb = QComboBox()
        self.import_char_cb.setStyleSheet(qss_setting.COMBOBOX_QSS)
        self.import_char_cb.activated.connect(self.load_prest_name)

        html_content = """
        <table width="100%">
            <tr>
                <td width="33%" align="center">Preset Name</td>
                <td width="33%" align="center">Create By</td>
                <td width="33%" align="center">Last Save</td>
            </tr>
        </table>
        """

        self.import_preset_lb = QLabel(html_content)
        self.import_preset_cb = PresetEditComboBox()
        self.import_preset_cb.setStyleSheet(qss_setting.COMBOBOX_QSS)
        self.import_preset_cb.activated.connect(self.load_list_preset_nodes)
        # self.import_preset_cb.addItems(["Click to see more Characters..."])
        self.import_char_v_lay.addWidget(self.import_char_lb)
        self.import_char_v_lay.addWidget(self.import_char_cb)
        self.import_preset_v_lay.addWidget(self.import_preset_lb)
        self.import_preset_v_lay.addWidget(self.import_preset_cb)

        self.import_tree_nodes_rbtn_layout = QHBoxLayout()
        self.import_tree_nodes_rbtn = QRadioButton("Whole nodes")
        self.import_tree_nodes_rbtn.setStyleSheet(qss_setting.RADIOBUTTON_QSS)
        import_tree_nodes_rbtn_icon = QIcon(icon_path.get_icon_path('Frac_1_1_pizza8.png'))
        self.import_tree_nodes_rbtn.setIconSize(QSize(45, 45))
        self.import_tree_nodes_rbtn.setIcon(import_tree_nodes_rbtn_icon)
        self.import_tree_nodes_rbtn_layout.addWidget(self.import_tree_nodes_rbtn)

        self.import_tree_attr_rbtn = QRadioButton("Single Attribute")
        self.import_tree_attr_rbtn.setStyleSheet(qss_setting.RADIOBUTTON_QSS)
        import_tree_attr_rbtn_icon = QIcon(icon_path.get_icon_path('Frac_1_1_pizza1.png'))
        self.import_tree_attr_rbtn.setIconSize(QSize(45, 45))
        self.import_tree_attr_rbtn.setIcon(import_tree_attr_rbtn_icon)
        self.import_tree_nodes_rbtn_layout.addWidget(self.import_tree_attr_rbtn)

        self.node_attribute_group.addButton(self.import_tree_nodes_rbtn)
        self.node_attribute_group.addButton(self.import_tree_attr_rbtn)

        self.import_select_h_lay = QHBoxLayout()

        # Connect the toggled signal of each radio button to the slot function
        self.import_tree_nodes_rbtn.toggled.connect(self.update_select_node_attr)
        self.import_tree_attr_rbtn.toggled.connect(self.update_select_node_attr)

        # Assuming you want the 'Local' option to be selected by default
        self.import_tree_nodes_rbtn.setChecked(True)

        self.import_select_all_btn = QPushButton("Select All")
        self.import_select_all_btn.setStyleSheet(qss_setting.BUTTON_QSS)
        self.import_select_all_btn.clicked.connect(self.select_all_items)
        self.import_select_h_lay.addWidget(self.import_select_all_btn)
        select_all_btn_icon = QIcon(icon_path.get_icon_path('select_all.png'))
        self.import_select_all_btn.setIcon(select_all_btn_icon)
        self.import_select_all_btn.setIconSize(QSize(32, 32))

        self.import_deselect_all_btn = QPushButton("Deselect All")
        self.import_deselect_all_btn.setStyleSheet(qss_setting.BUTTON_QSS)
        deselect_all_btn_icon = QIcon(icon_path.get_icon_path('deselect_all.png'))
        self.import_deselect_all_btn.setIcon(deselect_all_btn_icon)
        self.import_deselect_all_btn.setIconSize(QSize(32, 32))
        self.import_deselect_all_btn.clicked.connect(self.deselect_all_items)
        self.import_select_h_lay.addWidget(self.import_deselect_all_btn)

        # Add the horizontal layout to the parent layout (e.g., export_layout or select_part_layout)
        # Please replace with the layout you want these buttons to be added to
        self.v_lay.addLayout(self.import_char_v_lay)
        self.v_lay.addLayout(self.import_tree_nodes_rbtn_layout)
        self.v_lay.addLayout(self.import_preset_v_lay)

        self.layout().insertLayout(0, self.radio_btn_layout)
        # Insert the horizontal layout at the top of the main layout
        self.layout().insertLayout(1, self.path_layout)
        self.layout().insertLayout(2, self.v_lay)
        self.layout().addLayout(self.import_select_h_lay)

        # self.import_override_switch_parent_widget = QWidget()
        self.import_override_switch_H_lay = QHBoxLayout()
        self.import_override_switch = SwitchBtn(self)
        self.import_override_switch_lb = QLabel("Override attribute if connected. \n"
                                                "(Care :: This will disconnect all the "
                                                "attributes base on what you import!!)\n"
                                                "Animation key will be remove by default already")
        #import_override_switch_lb_icon = QIcon(icon_path.get_icon_path('aware.png'))
        #self.import_override_switch.setIcon(import_override_switch_lb_icon)
        #self.import_override_switch.setIconSize(QSize(32, 32))
        self.import_override_switch_H_lay.addWidget(self.import_override_switch)
        self.import_override_switch_H_lay.addWidget(self.import_override_switch_lb)
        self.layout().addLayout(self.import_override_switch_H_lay)

        # Initialize and set up a QPushButton for browsing directories
        self.import_button = QPushButton("Import Preset", self)
        self.import_button.setStyleSheet(qss_setting.BUTTON_QSS)
        import_button_btn_icon = QIcon(icon_path.get_icon_path('import_icon.png'))
        self.import_button.setIcon(import_button_btn_icon)
        self.import_button.setIconSize(QSize(32, 32))
        self.import_button.clicked.connect(self.import_preset)
        self.layout().addWidget(self.import_button)

        """
        path = 'Y:\\DJA\\assets\\type\\Character\\Ariel\\work\\elems\\Presetlib'
        path_list = path.split("\\")[1:]  # [1:] is to remove "Y:"
        nested_dict = build_nested_dict(path_list)

        print(nested_dict)
        """
        self.base_path = None
        self.check_paths = None
        self.character = None
        self.preset_name = None
        self.preset_user_path = None
        self.final_path_dict = {}
        self.info_json_path_list = []
        self.imported_preset_dict = {}
        self.exist_asset = []

    def open_directory_dialog(self):
        """Show a directory selection dialog and update the QLineEdit with the chosen path."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.path_edit.text())
        if directory:
            self.path_edit.setText(directory)

    # Slot function to update the directory based on the radio button selection
    def update_directory_path(self):
        if self.local_rad_btn.isChecked():
            self.path_edit.setText(LOCAL_PRESET_BASE)
        elif self.server_rad_btn.isChecked():
            self.path_edit.setText(SERVER_PRESET_BASE)

    def update_select_node_attr(self):
        for i in range(self.import_select_h_lay.count()):
            item = self.import_select_h_lay.itemAt(i)
            widget = item.widget()
            if widget:
                if self.import_tree_nodes_rbtn.isChecked():
                    widget.show()
                else:
                    widget.hide()

    def load_import(self):
        self.import_char_cb.clear()
        self.import_preset_cb.clear()
        self.clear_items()
        self.base_path = self.path_edit.text()
        self.check_paths = pf.check_all_shot_asset_path_exist(self.base_path)
        self.exist_asset = pf.check_asset_scene_exist() # self.base_path != SERVER_PRESET_BASE
        if self.base_path == SERVER_PRESET_BASE and pf.check_shot_asset() == 'Shot':
            print(self.check_paths, self.exist_asset)
            [self.import_char_cb.addItems([asset]) for asset in self.exist_asset
             if pf.extract_letters(asset) in self.check_paths.keys()]
        elif self.base_path != SERVER_PRESET_BASE:
            for asset, path in self.check_paths.items():
                # Load the info.json
                preset_path_base = os.path.join(path, "Presetlib")
                prest_user_list = os.listdir(preset_path_base)
                if len(prest_user_list) == 1:
                    self.preset_user_path = os.path.join(preset_path_base, prest_user_list[0])
                elif len(prest_user_list) > 1:
                    user = preset_path_dailog(prest_user_list)
                    self.preset_user_path = os.path.join(preset_path_base, user)
                else:
                    logger.error('Please make sure you have user folder in your Preset folder....')
                info_json_path = os.path.join(self.preset_user_path, "info.json")
                self.info_json_path_list.append(info_json_path)
                if info_json_path and os.path.exists(info_json_path):
                    if os.path.exists(info_json_path):
                        with open(info_json_path, "r") as f:
                            info_data = json.load(f)
                        self.import_char_cb.addItems([info_data['character_name']])
                    else:
                        logger.error("info.json not found in", info_json_path)
        else:
            self.exist_asset = [asset[:-4] if asset.endswith('_REF') else asset for asset in self.exist_asset]
            [self.import_char_cb.addItems([asset]) for asset in self.exist_asset]

    def load_prest_name(self):
        self.import_preset_cb.clear()
        model = QStandardItemModel()
        if self.base_path == SERVER_PRESET_BASE:
            self.character = self.import_char_cb.currentText()
            if pf.check_shot_asset() == 'Shot':
                self.character = pf.extract_letters(self.import_char_cb.currentText())
            self.preset_path = os.path.join(self.base_path, self.character, 'work/elems/Presetlib')
            users = os.listdir(self.preset_path)
            CURRENT_PATH.append(self.preset_path)
        else:
            self.preset_path = os.path.join(self.base_path, "Presetlib")
            users = os.listdir(self.preset_path)
            CURRENT_PATH.append(self.preset_path)

        for user in users:
            preset_name_path = os.path.join(self.preset_path, user)
            for preset_name in os.listdir(preset_name_path):
                if preset_name == "info.json":
                    continue
                save_time_dict = pf.get_file_info(os.path.join(preset_name_path, preset_name))

                if self.base_path == SERVER_PRESET_BASE:
                    info_json_path = os.path.join(preset_name_path, "info.json")
                    self.info_json_path_list.append(info_json_path)
                    if info_json_path and os.path.exists(info_json_path):
                        with open(info_json_path, "r") as f:
                            info_data = json.load(f)
                        publish = pf.preset_publish_checker(info_data, preset_name)

                        if publish is not None:
                            item_text = "{} - {} - {} ({})".format(preset_name, user, save_time_dict["save_time"],
                                                                   publish)
                            item_a = QStandardItem(item_text)
                            item_a.setForeground(QBrush(QColor("#D4AF37")))
                            item_a.setBackground(QBrush(QColor("#808080")))
                            font = QFont("Arial", 14, QFont.Bold)
                            item_a.setFont(font)
                            model.appendRow(item_a)
                        else:
                            item_text = "{} - {} - {}".format(preset_name, user, save_time_dict["save_time"])
                            item = QStandardItem(item_text)
                            model.appendRow(item)
                    else:
                        item_text = "{} - {} - {}".format(preset_name, user, save_time_dict["save_time"])
                        item = QStandardItem(item_text)
                        model.appendRow(item)
                else:
                    item_text = "{} - {} - {}".format(preset_name, user, save_time_dict["save_time"])
                    item = QStandardItem(item_text)
                    model.appendRow(item)
                    # self.import_preset_cb.addItem(item_text)

        self.import_preset_cb.setModel(model)
        if not hasattr(self, 'PresetDelegate'):
            self.PRESET_DELEGATE = pd.PresetDelegate(self)
        # self.import_preset_cb.setItemDelegate(self.PRESET_DELEGATE)

    def load_list_preset_nodes(self):
        self.clear_items()
        if self.import_tree_attr_rbtn.isChecked():
            self.tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        else:
            self.tree_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.preset_name = self.import_preset_cb.currentText()
        if self.base_path == SERVER_PRESET_BASE:
            path = os.path.join(self.base_path, self.character, 'work/elems/Presetlib',
                                self.preset_name.split(' - ')[1], self.preset_name.split(' - ')[0])
        else:
            path = os.path.join(self.base_path, 'Presetlib', self.preset_name.split(' - ')[1],
                                self.preset_name.split(' - ')[0])
        nodes_folders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
        for node_type in nodes_folders:
            node_name_item = self.add_item([node_type])
            node_name_item.setFlags(node_name_item.flags() & ~ Qt.ItemIsSelectable)
            node_files_path = os.path.join(path, node_type)
            node_files = [f for f in os.listdir(node_files_path)
                          if os.path.isfile(os.path.join(node_files_path, f)) and f != "info.json"]
            for node in node_files:
                self.add_item([node, node_type], parent=node_name_item)
                self.final_path_dict[node] = node_files_path
        # pf.print_tree_items(self.tree_widget)

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

    def import_preset(self):
        info_json_path = os.path.join(self.preset_path, self.preset_name.split(' - ')[1], 'info.json')
        select_items = self.get_selected_items_text()
        total_steps = len(select_items)  # Calculate the total number of steps
        current_step = 0
        # Instantiate ProgressBarDialog
        progressBarDialog = ppb.ProgressBarDialog()
        progressBarDialog.show()

        if select_items != {}:
            node_dict = {}
            for node_type, file_list in select_items.items():
                for file in file_list:
                    path = self.final_path_dict[file]
                    final_path = os.path.join(path, file)
                    final_path = pf.normalize_path(final_path)
                    if os.path.isfile(final_path):
                        if pf.check_shot_asset() == 'Shot':
                            # with open(info_json_path, "r") as f:
                            #    info_data = json.load(f)
                            # name_base = info_data['character_name']
                            name_base = self.import_char_cb.currentText()
                        else:
                            name_base = ''
                        if node_type.endswith('_maps'):
                            node_name = file.split('.')[0]
                            pf.apply_map_type(node_name, final_path, node_type, lyr1_ns=name_base)
                        else:
                            node_name = file.split('.')[0]
                            # node_name_with_ns = pf.ns_depth_search(name_base, node_name)
                            node = name_base+':'+node_name
                            if not cmds.objExists(node):
                                node = pf.ns_abc_search(name_base, node_name)
                            if node:
                                # for node in node_name_with_ns:
                                if self.import_tree_attr_rbtn.isChecked():
                                    mel_content = pf.parse_mel_attributes(final_path)
                                    selected_attributes = preset_path_dailog(mel_content)
                                    final_mel_data = pf.modify_and_execute_script(selected_attributes, final_path)
                                    if self.import_override_switch.checked:
                                        pf.attr_connected_override(final_path, '{}.{}'.format(node,
                                                                                              selected_attributes),
                                                                                              single_attr=True)
                                    pf.remove_key_animation('{}.{}'.format(node, selected_attributes))
                                    pf.apply_single_attr_preset(node, final_mel_data)
                                    logger.info('{}.{} imported!'.format(node, selected_attributes))
                                else:
                                    if self.import_override_switch.checked:
                                        pf.attr_connected_override(final_path, node)
                                    pf.remove_key_animation(node)
                                    pf.apply_attr_preset(node, final_path)
                                    logger.info('{} imported!'.format(node))
                                node_dict[node] = final_path
                            else:
                                logger.warning('Looks like {}*:{} node is not in your scene, skipped...'
                                               .format(name_base, node_name))
                    # Update progress bar after processing each file
                    current_step += 1
                    progress_percentage = int((current_step / total_steps))
                    progressBarDialog.setProgress(progress_percentage)
                    QCoreApplication.processEvents()
            if pf.check_shot_asset() == 'Shot':
                pf.resolve_folder_errors(DATA_DUMP_PATH)
                imported_json_path = DATA_DUMP_PATH
                shot_name = os.environ.get('TT_ENTNAME')
                preset_name = self.preset_name.split(' - ')[0]
                # Save imported preset for edit.
                pf.create_imported_preset_json(imported_json_path, shot_name, preset_name, node_dict)
            # Ensure progress bar reaches 100% at the end
            progressBarDialog.setProgress(100)
            progressBarDialog.close()
            logger.info("Import preset done")

    def on_item_selected_hint(self):
        selected_items = self.tree_widget.selectedItems()
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


class PresetEditComboBox(QComboBox):
    def __init__(self, parent=None):
        super(PresetEditComboBox, self).__init__(parent)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        access_json = os.path.join(ACCESS_JSON_BASE, USER, 'preset_access.json')
        if pf.server_user_access(access_json):
            action1 = menu.addAction("Preset Manager")
            action1.triggered.connect(self.option1_triggered)
        if USER in pf.find_all_sup_user():
            action2 = menu.addAction("Preset Access Manager")
            action2.triggered.connect(self.option2_triggered)
        # action3 = menu.addAction("Publish")
        # action3.triggered.connect(self.option3_triggered)
        menu.exec_(event.globalPos())

    def option1_triggered(self):
        reload(preset_manager_ui)
        app = app_manager.get_app_instance()
        path = ""
        if CURRENT_PATH:
            path = CURRENT_PATH[-1]
            print(path)
        ex = preset_manager_ui.ManagerUI(current_path=path)
        ex.show()

    def option2_triggered(self):
        reload(preset_access_manager_ui)
        app = app_manager.get_app_instance()
        path = ""
        ex = preset_access_manager_ui.AccessManagerUI(current_path=path)
        ex.show()

    def option3_triggered(self):
        print("3")
