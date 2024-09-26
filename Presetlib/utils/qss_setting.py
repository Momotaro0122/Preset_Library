from pynasty import *
import presetlib.icon.icon_path as icon_path
import presetlib.functions.presetlib_func as pf
reload(pf)
reload(icon_path)

cb_box_icon_filepath = icon_path.get_icon_path('combobox_down.png')


# Define style variables
DARK_BG_COLOR = "#2D2D2D"
LIGHT_BG_COLOR = "#3E3E3E"
BLUE_BG_COLOR = "#1F2D3C"
TEXT_COLOR = "#FFFFFF"
BTN_COLOR = "#3A76AC"
HOVER_BTN_COLOR = "#4A86BC"
CHECKED_BTN_COLOR = "#2A66AC"

MAIN_LITTLE_WINDOW_QSS = """
    QWidget {{
        background-color: {0};
        color: {1};
        font-family: Titillium;
        font-size: 12px;
    }}
""".format(BLUE_BG_COLOR, TEXT_COLOR)


MAIN_WINDOW_QSS = """
    QWidget {{
        background-color: {0};
        color: {1};
        font-family: Titillium;
        font-size: 18px;
    }}
""".format(BLUE_BG_COLOR, TEXT_COLOR)

# Set QTreeWidget style
TREEWIDGET_QSS = """
    /* Main QTreeWidget style */
    QTreeWidget {{
        border: 2px solid {2};
        border-radius: 5px;
        background-color: {0};
        color: {1};
        font-size: 12pt;
    }}

    /* QTreeWidget items (rows) */
    QTreeWidget::item {{
        padding: 5px;
        border-bottom: 1px solid #3A3A3A;  /* Separator line between items */
    }}

    /* Hover effect for items */
    QTreeWidget::item:hover {{
        background-color: {3};
    }}

    /* Selected item style */
    QTreeWidget::item:selected {{
        background-color: {4};
        color: {1};
    }}
    QTreeWidget::item[parent-selected="true"] {{
    background-color: #FFD700;  
    }}
""".format(DARK_BG_COLOR, TEXT_COLOR, BTN_COLOR, HOVER_BTN_COLOR, CHECKED_BTN_COLOR)

# Set QTreeWidget style
TREEWIDGET_LITTLE_QSS = """
    /* Main QTreeWidget style */
    QTreeWidget {{
        border: 2px solid {2};
        border-radius: 5px;
        background-color: {0};
        color: {1};
        font-size: 12px;
    }}

    /* QTreeWidget items (rows) */
    QTreeWidget::item {{
        padding: 5px;
        border-bottom: 1px solid #3A3A3A;  /* Separator line between items */
    }}

    /* Hover effect for items */
    QTreeWidget::item:hover {{
        background-color: {3};
    }}

    /* Selected item style */
    QTreeWidget::item:selected {{
        background-color: {4};
        color: {1};
    }}
    QTreeWidget::item[parent-selected="true"] {{
    background-color: #FFD700;  
    }}
""".format(DARK_BG_COLOR, TEXT_COLOR, BTN_COLOR, HOVER_BTN_COLOR, CHECKED_BTN_COLOR)

# Set QTreeWidget style
TREEWIDGET_TEST_QSS = """
    /* Main QTreeWidget style */
    QTreeWidget {{
        border: 2px solid {2};
        border-radius: 5px;
        background-color: {0};
        color: {1};
        font-size: 12pt;
    }}

    /* QTreeWidget items (rows) */
    QTreeWidget::item {{
        padding: 5px;
        border-bottom: 1px solid #3A3A3A;  /* Separator line between items */
    }}

    /* Hover effect for items */
    QTreeWidget::item:hover {{
        background-color: {3};
    }}

    /* Selected item style */
    QTreeWidget::item:selected {{
        background-color: {4};
        color: {1};
    }}
""".format("#FFD700", TEXT_COLOR, BTN_COLOR, HOVER_BTN_COLOR, "#FFD700")



# Set button style
BUTTON_QSS = """
    QPushButton {{
        background-color: {0};
        border: none;
        padding: 5px;
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: {1};
    }}
    QPushButton:pressed {{
        background-color: {2};
    }}
""".format(BTN_COLOR, HOVER_BTN_COLOR, CHECKED_BTN_COLOR)

DIALOG_QSS = """
    QDialog {{
        background-color: {0};
        border: 2px solid {1};
        border-radius: 5px;
    }}
""".format(BLUE_BG_COLOR, BTN_COLOR)


DRAG_QSS = '''
            QSlider {
                border-radius: 10px;
            }
            QSlider::groove:horizontal {
                height: 5px;
                background: #000;
            }
            QSlider::handle:horizontal{
                background: #f00;
                width: 16px;
                height: 16px;
                margin:-6px 0;
                border-radius:8px;
            }
            QSlider::sub-page:horizontal{
                background:#f90;
            }
        '''

# Set ComboBox style
COMBOBOX_QSS = """
    /* QComboBox main style */
    QComboBox {{
        border: 2px solid {2};
        border-radius: 5px;
        padding: 5px;
        background-color: {0};
        color: #FFFFFF;
        min-width: 150px;
    }}
    
    /* Drop down arrow style */   
    QComboBox::down-arrow {{
        /* Replace with your icon path */
        image: url({3}); 
        width: 16px;
        height: 20px;
    }}
    
    /* Drop down menu (popup list) style */
    QComboBox QAbstractItemView {{
        border: 2px solid ;
        background-color: {4};
        selection-background-color: #3A76AC;
    }}
    
    /* Hover effect */
    QComboBox:hover {{
        border-color: {1};
    }}
""".format(DARK_BG_COLOR, HOVER_BTN_COLOR, BTN_COLOR, cb_box_icon_filepath, DARK_BG_COLOR)


# Set LineEdit style
LINE_EDIT_QSS = """
    QLineEdit {{
        background-color: {0};
        border: none;
        padding-left: 5px;
    }}
""".format(DARK_BG_COLOR)

# Set RadioButton style
RADIOBUTTON_QSS = """
    QRadioButton {{
        color: {0};
        width: 20px;     /* Adjust width */
        height: 20px;    /* Adjust height */
        border-radius: 10px; /* Makes the indicator circular */

    }}
    QRadioButton::indicator {{
        width: 20px;
        height: 20px;
    }}
""".format(TEXT_COLOR)

# Set QListWidget style
COLLAPS_LAY_QSS = """
    /* Main QListWidget style */
    QWidget {{
        border: 2px solid {2};
        border-radius: 5px;
        background-color: {0};
        color: {1};
    }}

    /* QListWidget items (rows) */
    QWidget::item {{
        padding: 5px;
        border-bottom: 1px solid #3A3A3A;  /* Separator line between items */
    }}

    /* Hover effect for items */
    QWidget::item:hover {{
        background-color: {3};
    }}

    /* Selected item style */
    QWidget::item:selected {{
        background-color: {4};
        color: {1};
    }}
""".format(DARK_BG_COLOR, TEXT_COLOR, BTN_COLOR, HOVER_BTN_COLOR, CHECKED_BTN_COLOR)


# Set QListWidget style
LISTWIDGET_QSS = """
    /* Main QListWidget style */
    QListWidget {{
        border: 2px solid {2};
        border-radius: 5px;
        background-color: {0};
        color: {1};
        font-size: 12pt;
    }}

    /* QListWidget items (rows) */
    QListWidget::item {{
        padding: 5px;
        border-bottom: 1px solid #3A3A3A;  /* Separator line between items */
    }}

    /* Hover effect for items */
    QListWidget::item:hover {{
        background-color: {3};
    }}

    /* Selected item style */
    QListWidget::item:selected {{
        background-color: {4};
        color: {1};
    }}
""".format(DARK_BG_COLOR, TEXT_COLOR, BTN_COLOR, HOVER_BTN_COLOR, CHECKED_BTN_COLOR)

# Set QListWidget style
CHECKBOX_QSS = """
    QCheckBox {{
        spacing: 5px;
    }}
    
    QCheckBox::indicator {{
        width: 13px;
        height: 13px;
    }}
    
    QCheckBox::indicator:unchecked {{
        image: url(:/images/checkbox_unchecked.png);
    }}
    
    QCheckBox::indicator:unchecked:hover {{
        image: url(:/images/checkbox_unchecked_hover.png);
    }}
    
    QCheckBox::indicator:unchecked:pressed {{
        image: url(:/images/checkbox_unchecked_pressed.png);
    }}
    
    QCheckBox::indicator:checked {{
        image: url(:/images/checkbox_checked.png);
    }}
    
    QCheckBox::indicator:checked:hover {{
        image: url(:/images/checkbox_checked_hover.png);
    }}
    
    QCheckBox::indicator:checked:pressed {{
        image: url(:/images/checkbox_checked_pressed.png);
    }}
    
    QCheckBox::indicator:indeterminate:hover {{
        image: url(:/images/checkbox_indeterminate_hover.png);
    }}
    
    QCheckBox::indicator:indeterminate:pressed {{
        image: url(:/images/checkbox_indeterminate_pressed.png);
    }}
""".format(DARK_BG_COLOR, TEXT_COLOR, BTN_COLOR, HOVER_BTN_COLOR, CHECKED_BTN_COLOR)

# Set QListWidget style
PROGRESSBOX_QSS = """
QProgressBar {{
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: #CD96CD;
    width: 10px;
    margin: 0.5px;
}}
""".format(DARK_BG_COLOR)




# Apply the above styles to the corresponding components
"""
qss_setting.MAIN_WINDOW_QSS = MAIN_WINDOW_QSS
qss_setting.BUTTON_QSS = BUTTON_QSS
qss_setting.COMBOBOX_QSS = COMBOBOX_QSS
qss_setting.LINE_EDIT_QSS = LINE_EDIT_QSS
qss_setting.RADIOBUTTON_QSS = RADIOBUTTON_QSS
qss_setting.LISTWIDGET_QSS = LISTWIDGET_QSS
"""