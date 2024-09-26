from pynasty import *
import maya.OpenMayaUI
import shiboken2
import PySide2.QtWidgets as qt
import sys


def get_main_window():
    main_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    if sys.executable.split('Maya')[-1].split('\\')[0].strip() > '2022':
        parent = shiboken2.wrapInstance(int(main_window_ptr), qt.QWidget)
    else:
        parent = shiboken2.wrapInstance(long(main_window_ptr), qt.QWidget)
    return parent

