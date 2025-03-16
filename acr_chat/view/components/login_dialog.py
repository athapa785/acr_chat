from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                          QLabel, QLineEdit, QPushButton, QMessageBox)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Login - ACR Chat")
        layout = QVBoxLayout()
        
        # Username input
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username...")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add to main layout
        layout.addLayout(username_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to username input
        self.username_input.setFocus()
        
    def handle_login(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Username cannot be empty!")
            self.username_input.setFocus()
            return
            
        self.username = username
        self.accept()
        
    @staticmethod
    def get_username(parent=None):
        while True:  # Keep showing dialog until user cancels or successful login
            dialog = LoginDialog(parent)
            result = dialog.exec_()
            
            if result == QDialog.Accepted and dialog.username:
                return dialog.username
            elif result == QDialog.Rejected:
                return None  # User clicked Cancel
            
            # If we get here, there was an error but user hasn't cancelled 