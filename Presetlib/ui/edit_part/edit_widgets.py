from pynasty import *
# Built-in libraries
import os
import sys
import json
import maya.cmds as cmds
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from functools import partial
import random

# Ensure the script path is in sys.path
SCRIPT_PATH = 'G:/Tech_Animation/scripts'
if SCRIPT_PATH not in sys.path:
    sys.path.append(SCRIPT_PATH)

# Local modules
# from pynasty import *
import presetlib.functions.presetlib_func as pf
from presetlib.ui.import_part import preset_path_dailog
from presetlib.utils.preset_logger import PRESETLIBLogger
import presetlib.utils.qss_setting as qss_setting
import presetlib.icon.icon_path as icon_path
import presetlib.ui.all_parent_part.presetlib_frame_lay as presetlib_frame_lay
from presetlib.ui.all_parent_part.sortable_widgets import SortableListWidget
# Reloading modules to ensure the latest version is in use
reload(pf)
reload(preset_path_dailog)
reload(qss_setting)
reload(icon_path)
reload(presetlib_frame_lay)

# Global vars.
LOCAL_PRESET_BASE = pf.LOCAL_PRESET_BASE
SERVER_PRESET_BASE = pf.SERVER_PRESET_BASE
DATA_DUMP_PATH = pf.DATA_DUMP_PATH
preset_path_dailog = preset_path_dailog.preset_path_dailog
CURRENT_SHOT = os.environ.get('TT_ENTNAME')
USER = os.environ.get('TT_USER')

# Font.
FONT = QFont()
FONT.setPointSize(10)
FONT.setBold(True)

# Class.

# Ini.
"""
logger = PRESETLIBLogger().get_logger()
logger.info("This is an info message from PRESETLIB logger.")
logger.error("This is an error message from PRESETLIB logger.")
"""
logger = PRESETLIBLogger().get_logger()





class AnimationLayerEditor(QWidget):
    def __init__(self, TARIG=False):
        super(AnimationLayerEditor, self).__init__()
        self.setWindowTitle("Animation Layer Editor")
        self.setGeometry(100, 100, 400, 300)
        self.TARIG = TARIG
        self.initUI()
        self.init_preset_list()

    def initUI(self):
        layout = QVBoxLayout()
        self.preset_prebuild_list_clp_lay = presetlib_frame_lay.FrameLayout(title="List - ready to create preset layer")
        if self.preset_prebuild_list_clp_lay._is_collasped:
            self.preset_prebuild_list_clp_lay.toggleCollapsed()

        # "Refresh Selection" button
        self.refresh_btn = QPushButton("Refresh Imported Preset")
        self.refresh_btn.setStyleSheet(qss_setting.BUTTON_QSS)
        refresh_btn_icon = QIcon(icon_path.get_icon_path('refresh.png'))
        self.refresh_btn.setIcon(refresh_btn_icon)
        self.refresh_btn.setIconSize(QSize(32, 32))
        self.preset_prebuild_list_clp_lay.addWidget(self.refresh_btn)
        self.refresh_btn.clicked.connect(self.refresh_export_selection)

        self.preset_prebuild_list_widget = SortableListWidget(headers=['Preset', 'Nodes'], TARIG=self.TARIG)
        self.preset_prebuild_list_clp_lay.addWidget(self.preset_prebuild_list_widget)
        layout.addWidget(self.preset_prebuild_list_clp_lay)


        # create anim lay btn.
        create_anim_lay_button = QPushButton("Create Preset Layers")
        create_anim_lay_button.setStyleSheet(qss_setting.BUTTON_QSS)
        create_anim_lay_btn_icon = QIcon(icon_path.get_icon_path('create_lay.png'))
        create_anim_lay_button.setIcon(create_anim_lay_btn_icon)
        create_anim_lay_button.setIconSize(QSize(32, 32))
        layout.addWidget(create_anim_lay_button)
        create_anim_lay_button.clicked.connect(self.create_preset_anim_lay)

        # fill btn.
        fill_button = QPushButton("Fill Edit Layers List")
        fill_button.setStyleSheet(qss_setting.BUTTON_QSS)
        fill_button_icon = QIcon(icon_path.get_icon_path('fill_list.png'))
        fill_button.setIcon(fill_button_icon)
        fill_button.setIconSize(QSize(32, 32))
        layout.addWidget(fill_button)
        fill_button.clicked.connect(self.fillList)

        # list widget.
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(qss_setting.LISTWIDGET_QSS)
        self.list_widget.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def create_preset_anim_lay(self):
        imported_nodes_path = DATA_DUMP_PATH
        imported_nodes_path = os.path.join(imported_nodes_path, 'imported_preset_info.json')
        with open(imported_nodes_path, 'r') as f:
            json_data = json.load(f)

        preset_name = json_data[CURRENT_SHOT].keys()
        if len(preset_name) == 1:
            preset_name = preset_name[0]
        elif len(preset_name) > 1:
            preset_name = preset_path_dailog(preset_name)
        else:
            logger.error("Looks like you didn't select things when you import the preset... "
                         "\nCheck Line 77- edit_widgets.py")
        selected_objects = json_data[CURRENT_SHOT][preset_name].keys()
        char_name = selected_objects[0].split(':')[0]
        pf.create_anim_lay(selected_objects, char_name, preset_name)

    def create_layer_widget(self, layer):
        def show(arg):
            line_edit.setText(str(drag_widget.value() * 0.01))
            cmds.setAttr('{}.weight'.format(layer), drag_widget.value() * 0.01)

        def update_slider():
            try:
                value = float(line_edit.text()) * 100
                drag_widget.setValue(int(value))
                cmds.setAttr('{}.weight'.format(layer), value * 0.01)
            except ValueError:
                pass  # If the user enters an invalid value, just ignore

        def edit_set_key():
            try:
                cmds.setKeyframe('{}.weight'.format(layer))
                keyframes = cmds.currentTime(query=True)
                logger.info('{}.weight keyed at Frame {}'.format(layer, keyframes))
            except:
                pass  # If the user enters an invalid value, just ignore

        def edit_remove_key():
            try:
                before_keyframes = cmds.keyframe('{}.weight'.format(layer), query=True, timeChange=True)
                cmds.cutKey('{}.weight'.format(layer))
                logger.info('{}.weight Delete at Frame {}'.format(layer, str(before_keyframes)))
            except:
                pass  # If there's an error while trying to remove the key, just ignore

        def select_layer_node():
            if cmds.objExists('{}.weight'.format(layer)):
                cmds.select(layer, r=1, ne=1)

        text_color = QColor(0, 0, 0)
        edit_h_main_wid = QWidget()
        edit_h_widgetLayout = QHBoxLayout()
        edit_v_widgetLayout = QVBoxLayout()
        item = QListWidgetItem()
        item.setSizeHint(QSize(150, 100))
        random_color = list_item_color()
        apply_color_to_widget(edit_h_main_wid, random_color)
        item.setFont(FONT)
        preset_lay_lb = QLabel(layer)
        palette = preset_lay_lb.palette()
        palette.setColor(QPalette.WindowText, text_color)
        preset_lay_lb.setFont(FONT)
        edit_v_widgetLayout.addWidget(preset_lay_lb)
        edit_h_widgetLayout.addLayout(edit_v_widgetLayout)
        edit_h_main_wid.setLayout(edit_h_widgetLayout)

        widget = QWidget()
        # slider
        drag_widget = QSlider(Qt.Horizontal)
        drag_widget.setRange(0, 100)
        drag_widget.setValue(10)
        drag_widget.setStyleSheet(qss_setting.DRAG_QSS)

        # Line Edit
        line_edit = QLineEdit("0.0")
        palette = line_edit.palette()
        palette.setColor(QPalette.Text, text_color)
        line_edit.setFixedWidth(40)

        edit_key_btn = QPushButton('Key')
        edit_rkey_btn = QPushButton('Remove Key')
        edit_sel_ley_btn = QPushButton('Select Layer Node')

        edit_key_btn_icon = QIcon(icon_path.get_icon_path('key.png'))
        edit_key_btn.setIcon(edit_key_btn_icon)
        edit_key_btn.setIconSize(QSize(32, 32))

        edit_rkey_btn_icon = QIcon(icon_path.get_icon_path('remove_key.png'))
        edit_rkey_btn.setIcon(edit_rkey_btn_icon)
        edit_rkey_btn.setIconSize(QSize(32, 32))

        edit_sel_ley_btn_icon = QIcon(icon_path.get_icon_path('layer_icon.png'))
        edit_sel_ley_btn.setIcon(edit_sel_ley_btn_icon)
        edit_sel_ley_btn.setIconSize(QSize(32, 32))

        # edit_

        widgetLayout = QHBoxLayout()
        widgetLayout.addWidget(drag_widget)
        widgetLayout.addWidget(line_edit)

        widgetLayout.addStretch()

        widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
        widget.setLayout(widgetLayout)
        # item.setSizeHint(widget.sizeHint())

        edit_v_widgetLayout.addWidget(widget)
        edit_h_widgetLayout.addWidget(edit_key_btn)
        edit_h_widgetLayout.addWidget(edit_rkey_btn)
        edit_h_widgetLayout.addWidget(edit_sel_ley_btn)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, edit_h_main_wid)

        drag_widget.valueChanged.connect(show)
        line_edit.textEdited.connect(update_slider)
        edit_key_btn.clicked.connect(edit_set_key)
        edit_rkey_btn.clicked.connect(edit_remove_key)
        edit_sel_ley_btn.clicked.connect(select_layer_node)

    def fillList(self):
        # clear list widget.
        self.list_widget.clear()

        # find "PRESETLIB_" Animation Layer
        animation_layers = cmds.ls(type="animLayer") or []
        preset_layers = [layer for layer in animation_layers if layer.startswith("PRESETLIB_")]

        # create list widget
        for layer in preset_layers:
            self.create_layer_widget(layer)

    def init_preset_list(self):
        self.preset_prebuild_list_widget.tree_widget.clear()
        path = os.path.join(DATA_DUMP_PATH, 'imported_preset_info.json')
        try:
            with open(path, 'r') as f:
                json_data = json.load(f)
        except IOError:
            self.preset_prebuild_list_widget.add_item(["No Preset Imported Yet..."])
            return

        if not json_data or CURRENT_SHOT not in json_data:
            self.preset_prebuild_list_widget.add_item(["No Preset Imported Yet..."])
            return

        for preset_name in json_data[CURRENT_SHOT].keys():
            preset_name_item = self.preset_prebuild_list_widget.add_item([preset_name])
            preset_name_item.setFlags(preset_name_item.flags() & ~Qt.ItemIsSelectable)
            for node in json_data[CURRENT_SHOT][preset_name].keys():
                self.preset_prebuild_list_widget.add_item([node], parent=preset_name_item)

    def refresh_export_selection(self):
        """Refresh export selection."""
        self.init_preset_list()


color_rnum = ['#f0f8ff',
              '#f5f5dc',
              '#8a2be2',
              '#d2691e',
              '#00ffff',
              '#006400',
              '#556b2f',
              '#ff8c00',
              '#e9967a',
              '#483d8b',
              '#9400d3',
              '#ff1493',
              '#1e90ff',
              '#b22222',
              '#f8f8ff',
              '#adff2f',
              '#4b0082',
              '#7cfc00',
              '#fafad2',
              '#b0c4de',
              '#ff00ff']

alpha_value = 128

# Initialize a list of QColor objects with a specified transparency
colors_with_alpha = []
for color_code in color_rnum:
    color = QColor(color_code)
    color.setAlpha(alpha_value)
    colors_with_alpha.append(color)


def apply_color_to_widget(widget, color):
    color_style = "background-color: rgba({}, {}, {}, {});".format(color.red(), color.green(), color.blue(), color.alpha())
    widget.setStyleSheet(widget.styleSheet() + color_style)



def list_item_color():
    global colors_with_alpha

    # If the colors_with_alpha list is empty, reset the color list
    if not colors_with_alpha:
        colors_with_alpha = [QColor(color_code).setAlpha(alpha_value) for color_code in color_rnum]

    random_color = random.choice(colors_with_alpha)
    # Remove the selected color from the list to ensure uniqueness in subsequent selections
    colors_with_alpha.remove(random_color)
    return random_color
