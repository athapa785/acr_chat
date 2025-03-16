from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PyQt5.QtCore import Qt, pyqtSignal

class UsersList(QWidget):
    user_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        
        #title = QLabel("Online Users")
        #title.setAlignment(Qt.AlignCenter)
        #title.setStyleSheet("font-size: 12pt; font-weight: bold; padding: 5px;")
        
        self.users_list = QListWidget()
        self.users_list.setStyleSheet("""
            QListWidget {
                font-size: 12pt;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        self.users_list.itemClicked.connect(
            lambda item: self.user_selected.emit(item.text())
        )
        
        #layout.addWidget(title)
        layout.addWidget(self.users_list)
        
        self.setLayout(layout)
        self.setFixedWidth(220)  # Slightly wider for better readability
        
    def update_users(self, users: list):
        self.users_list.clear()
        self.users_list.addItems(users) 