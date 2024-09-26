from PySide2.QtWidgets import QApplication
import sys

def get_app_instance():
    if QApplication.instance():
        return QApplication.instance()
    else:
        return QApplication(sys.argv)

