from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                          QLabel, QLineEdit, QPushButton, QMessageBox)

class AdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.passcode = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Admin Access")
        layout = QVBoxLayout()
        
        # Passcode input
        passcode_layout = QHBoxLayout()
        passcode_label = QLabel("Passcode:")
        self.passcode_input = QLineEdit()
        self.passcode_input.setEchoMode(QLineEdit.Password)
        self.passcode_input.setPlaceholderText("Enter admin passcode...")
        passcode_layout.addWidget(passcode_label)
        passcode_layout.addWidget(self.passcode_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.handle_submit)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add to main layout
        layout.addLayout(passcode_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to passcode input
        self.passcode_input.setFocus()
        
    def handle_submit(self):
        passcode = self.passcode_input.text().strip()
        if not passcode:
            QMessageBox.warning(self, "Error", "Passcode cannot be empty!")
            self.passcode_input.setFocus()
            return
            
        self.passcode = passcode
        self.accept()
        
    @staticmethod
    def get_passcode(parent=None):
        dialog = AdminDialog(parent)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return dialog.passcode
        return None 