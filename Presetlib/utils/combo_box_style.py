from PySide2.QtWidgets import QProxyStyle, QStyle, QComboBox, QApplication
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect


class CustomComboBoxStyle(QProxyStyle):

    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PE_IndicatorArrowDown:
            # Get the standard icon
            icon = self.standardIcon(QStyle.SP_ToolBarVerticalExtensionButton, option, widget)
            pixmap = icon.pixmap(16, 16)

            # Draw the icon
            rect = QRect((option.rect.width() - 16) // 2, (option.rect.height() - 16) // 2, 16, 16)
            painter.drawPixmap(rect, pixmap)
        else:
            super(CustomComboBoxStyle, self).drawPrimitive(element, option, painter, widget)
