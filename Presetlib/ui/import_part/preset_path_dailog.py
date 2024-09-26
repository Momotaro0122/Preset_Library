from pynasty import *
import sys

from PySide2.QtGui import *
from PySide2.QtWidgets import *

# Ensure the script path is in sys.path
SCRIPT_PATH = 'G:/Tech_Animation/scripts'
if SCRIPT_PATH not in sys.path:
    sys.path.append(SCRIPT_PATH)

# Local modules
import presetlib.ui.all_parent_part.list_dialog as list_dialog

# Reloading modules to ensure the latest version is in use
reload(list_dialog)


# Class.
DirSelectDialog = list_dialog.DirSelectDialog


def preset_path_dailog(options_list):
    dialog = DirSelectDialog(options_list)
    result = dialog.exec_()  # This will block until the dialog is closed
    # If the user pressed OK, then we get the selected item
    if result == QDialog.Accepted:
        return dialog.get_selected_item()
    else:  # If the user canceled, you might want to handle this scenario too
        return