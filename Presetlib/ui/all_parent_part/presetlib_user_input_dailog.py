from PySide2.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton, QApplication, QWidget, QComboBox

class UserInputDialog(QDialog):
    def __init__(self, parent=None):
        super(UserInputDialog, self).__init__(parent)
        self.setWindowTitle("Export Info Dialog")
        self.layout = QVBoxLayout(self)
        self.resize(230, 200)

        # ComboBox for preset selection
        self.preset_combo = QComboBox(self)
        self.preset_combo.addItem('Name as "default"')
        self.preset_combo.addItem("create new preset")
        self.layout.addWidget(self.preset_combo)

        # Line Edit for preset name
        self.preset_name_label = QLabel("Enter preset name:", self)
        self.preset_name_edit = QLineEdit(self)
        self.layout.addWidget(self.preset_name_label)
        self.layout.addWidget(self.preset_name_edit)

        # Initially hide the preset name fields
        self.preset_name_label.hide()
        self.preset_name_edit.hide()

        # Update UI based on combo box selection
        self.preset_combo.currentIndexChanged.connect(self.update_ui)

        # # Line Edit for description
        # self.description_label = QLabel("Type in description:", self)
        # self.description_edit = QLineEdit(self)
        # self.description_edit.setPlaceholderText("Leave it blank if you don't need this.")
        # # self.layout.addWidget(self.description_label)
        # # self.layout.addWidget(self.description_edit)

        # OK and Cancel buttons
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.ok_button)
        self.layout.addWidget(self.cancel_button)

        self.preset_name = None

    def update_ui(self):
        # Show/hide preset name fields based on combo box selection
        if self.preset_combo.currentText() == "create new preset":
            self.preset_name_label.show()
            self.preset_name_edit.show()
        else:
            self.preset_name_label.hide()
            self.preset_name_edit.hide()

    def get_input(self):
        if self.preset_combo.currentText() == "create new preset":
            self.preset_name = self.preset_name_edit.text()
        else:
            self.preset_name = "default"
        return self.preset_name
