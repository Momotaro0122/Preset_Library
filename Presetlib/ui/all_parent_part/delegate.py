from PySide2.QtWidgets import QWidget, QVBoxLayout, QComboBox, QApplication, QStyledItemDelegate, QListView, QStyle
from PySide2.QtGui import QPainter, QColor
from PySide2.QtCore import Qt

class PresetDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Draw selection highlight
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor("#DAA520"))  # Use yellow for the highlight
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())

        # Retrieve the item text and split it
        texts = index.data().split(' - ')
        if len(texts) != 3:
            super().paint(painter, option, index)
            return

        width = option.rect.width() // 3
        for i, text in enumerate(texts):
            painter.drawText(option.rect.x() + i * width, option.rect.y(), width, option.rect.height(), Qt.AlignCenter, text)