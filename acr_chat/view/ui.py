from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QSplitter, QLabel, QMessageBox, QApplication, QDialog, QPushButton, QFrame, QMenu,
    QLineEdit, QDialogButtonBox, QVBoxLayout
)
from PyQt5.QtCore import Qt, QFileSystemWatcher, QTimer, QPoint
from PyQt5.QtGui import QCursor, QIcon, QTextCursor, QMovie
from .components import ChatHistory, UsersList, DirectoryView, LoginDialog
from ..controller.controller import ChatController
from ..model.chat_model import SharedFile
from datetime import datetime
import os
import subprocess
import platform
import json
from typing import List
import sys
import re
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        # Initialize instance variables
        self.controller = controller or ChatController()
        self.users_list = None
        self.chat_history = None
        self.directory_view = None
        
        # Initialize timers for file checking
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_files)
        
        # Set up signal connections before login
        self.setup_signals()
        
        # Initialize login
        self.init_login()

        self.last_modified_times = {
        'chat': None,
        'users': None,
        'files': None
    }
        
    def setup_signals(self):
        """Set up signal connections."""
        self.controller.message_received.connect(self.handle_message_received)
        self.controller.user_added.connect(self.handle_user_added)
        self.controller.user_removed.connect(self.handle_user_removed)
        self.controller.files_updated.connect(self.handle_files_updated)
        self.controller.login_failed.connect(self.handle_login_failed)
        
    def init_login(self):
        """Initialize login dialog."""
        dialog = LoginDialog(self)
        while True:
            if dialog.exec_() == QDialog.Accepted:
                username, password = dialog.get_credentials()
                if self.controller.attempt_login(username, password):
                    self.setWindowTitle(f"ACR Chat - {username}")
                    self.init_ui()
                    self.setup_file_checking()  # Set up periodic file checking
                    self.load_initial_data()
                    break
            else:
                sys.exit()
            
    def setup_file_checking(self):
        """Set up periodic file checking."""
        # Ensure the directory exists
        data_dir = os.path.dirname(self.controller.model.HISTORY_FILE)
        os.makedirs(data_dir, exist_ok=True)
        
        # Create empty files if they don't exist
        for file_path in [
            self.controller.model.HISTORY_FILE,
            self.controller.model.USERS_FILE,
            self.controller.model.FILES_FILE
        ]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)

        # Start the timer to check files every 100ms
        self.update_timer.start(400)
        
    def check_files(self):
        """Check files for changes and update UI accordingly (efficient)."""
        files = {
            'chat': self.controller.model.HISTORY_FILE,
            'users': self.controller.model.USERS_FILE,
            'files': self.controller.model.FILES_FILE
        }

        for key, path in files.items():
            try:
                modified_time = os.path.getmtime(path)
                if self.last_modified_times[key] != modified_time:
                    self.last_modified_times[key] = modified_time
                    self.update_gui_element(key)
            except Exception as e:
                logger.debug(f"Error checking {key} file: {e}")

    def update_gui_element(self, element):
        if element == 'chat':
            messages = self.controller.model.get_all_messages()
            self.update_chat_history(messages)
        elif element == 'users':
            users = self.controller.get_all_users()
            self.users_list.update_users(users)
        elif element == 'files':
            files = self.controller.model.get_shared_files()
            self.directory_view.update_files(files)

    def update_chat_history(self, messages):
        if self.chat_history:
            self.chat_history.clear()  # Clears the messages layout
            for msg in messages:
                self.chat_history.add_message(msg.sender, msg.content, msg.timestamp)
            self.chat_history.scroll_to_bottom()
            
    def init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # Reduced from 10 to 5
        main_layout.setSpacing(2)  # Add minimal spacing between elements
        main_widget.setLayout(main_layout)
        
        # Create left panel for users list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        left_layout.setSpacing(2)  # Minimal spacing
        left_panel.setLayout(left_layout)
        
        # Add header with admin button and "Online Users" label
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        header_layout.setSpacing(4)  # Slightly larger spacing for header items
        header_widget.setLayout(header_layout)
        
        # Admin button
        admin_button = QPushButton("⚙")  # Gear emoji as icon 
        admin_button.setFixedSize(24, 24)
        admin_button.setToolTip("Admin Settings")
        admin_button.clicked.connect(self.show_admin_dialog)
        header_layout.addWidget(admin_button)
        
        # Online Users label
        online_label = QLabel("Online Users")
        online_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #2196F3;
                padding: 2px;
            }
        """)
        header_layout.addWidget(online_label)
        header_layout.addStretch()
        
        left_layout.addWidget(header_widget)
        
        # Add users list below header
        self.users_list = UsersList()
        left_layout.addWidget(self.users_list)
        
        # Create center panel for chat
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(2, 0, 2, 0)  # Minimal left/right margins
        center_layout.setSpacing(2)  # Minimal spacing
        center_widget.setLayout(center_layout)
        
        # Add a thinner separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setMaximumHeight(1)  # Make the line thinner
        separator.setStyleSheet("background-color: #E0E0E0;")  # Lighter color
        center_layout.addWidget(separator)
        
        # Chat history
        self.chat_history = ChatHistory()
        self.chat_history.set_username(self.controller.current_user)
        self.chat_history.message_sent.connect(self.handle_media_message)
        center_layout.addWidget(self.chat_history, stretch=1)
        
        # Message input area
        input_layout = QHBoxLayout()
        
        # Emoji/GIF button
        self.media_button = QPushButton("😊")
        self.media_button.setObjectName("media_button")  # Set object name for event filter
        self.media_button.setFixedSize(40, 40)
        self.media_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 20px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.media_button.clicked.connect(self.show_media_picker)
        input_layout.addWidget(self.media_button)
        
        # Message input
        self.message_input = QLineEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 20px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        input_layout.addWidget(self.message_input)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        center_layout.addLayout(input_layout)
        
        # Create right panel for directory view
        self.directory_view = DirectoryView()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_widget)
        splitter.addWidget(self.directory_view)
        
        # Set initial sizes (users:chat:files ratio of 1:3:1.5)
        total_width = 1000
        users_width = total_width // 6
        files_width = total_width // 4
        chat_width = total_width - users_width - files_width
        splitter.setSizes([users_width, chat_width, files_width])
        
        main_layout.addWidget(splitter)
        
        # Connect signals
        self.users_list.user_selected.connect(self.handle_user_selected)
        self.directory_view.file_selected.connect(self.handle_file_selected)
        self.directory_view.file_added.connect(self.handle_file_added)
        
        # Set window size and position
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() // 6,
            screen.height() // 6,
            (screen.width() * 2) // 3,
            (screen.height() * 2) // 3
        )
        
        self.show()
        
    def closeEvent(self, event):
        """Handle window close event."""
        if self.controller.current_user:
            self.controller.logout()
            self.update_timer.stop()
            users = self.controller.get_all_users()
            if self.users_list:
                self.users_list.update_users(users)
        event.accept()
        
    # Signal handlers
    def handle_message_received(self, sender: str, content: str, timestamp: datetime):
        """Handle a new message being received."""
        if self.chat_history:
            self.chat_history.add_message(sender, content, timestamp)
            
    def handle_user_selected(self, username: str):
        # TODO: Implement private messaging or user info display
        pass
        
    def handle_file_added(self, filepath: str):
        """Handle when a new file is added to share."""
        if self.controller.add_shared_file(filepath):
            self.directory_view.update_files(self.controller.get_shared_files())
            
    def handle_file_selected(self, filepath: str):
        """Handle when a file is selected for opening."""
        try:
            if not os.path.exists(filepath):
                QMessageBox.warning(self, "Error", "File no longer exists at this location.")
                return
                
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            elif platform.system() == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {e}")
            
    def handle_user_added(self, username: str):
        """Handle a user being added."""
        if self.users_list:
            users = self.controller.get_all_users()
            self.users_list.update_users(users)
        
    def handle_user_removed(self, username: str):
        """Handle a user being removed."""
        if self.users_list:
            users = self.controller.get_all_users()
            self.users_list.update_users(users)
        
    def handle_files_updated(self, files: List[SharedFile]):
        """Handle shared files being updated."""
        if self.directory_view:
            self.directory_view.update_files(files)
        
    def handle_login_failed(self, error_msg: str):
        """Handle a failed login attempt."""
        QMessageBox.warning(self, "Login Failed", error_msg)
        
    def update_users_list(self, users: list):
        if self.users_list:
            self.users_list.update_users(users)

    def load_initial_data(self):
        """Load initial data after successful login."""
        # Load and display active users
        users = self.controller.get_all_users()
        if self.users_list:
            self.users_list.update_users(users)
        
        # Load and display chat history
        messages = self.controller.model.get_all_messages()
        if self.chat_history:
            for msg in messages:
                self.chat_history.add_message(msg.sender, msg.content, msg.timestamp)
            
        # Load and display shared files
        files = self.controller.model.get_shared_files()
        if self.directory_view:
            self.directory_view.update_files(files)

    def show_admin_dialog(self):
        """Show the admin dialog with passcode and action buttons."""
        dialog = AdminDialog(self)
        
        # Connect admin action buttons
        dialog.logout_all_btn.clicked.connect(lambda: self.handle_admin_action(dialog, self.admin_logout_all))
        dialog.archive_chat_btn.clicked.connect(lambda: self.handle_admin_action(dialog, self.admin_archive_chat))
        dialog.archive_files_btn.clicked.connect(lambda: self.handle_admin_action(dialog, self.admin_archive_files))
        
        dialog.exec_()
        
    def handle_admin_action(self, dialog, action_func):
        """Handle admin action button clicks."""
        if dialog.passcode_input.text() == "admin123":  # You can change this passcode
            action_func()
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid admin passcode")

    def admin_logout_all(self):
        """Admin action to log out all users."""
        try:
            self.controller.model.clear_active_users()
            QMessageBox.information(self, "Success", "All users have been logged out")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to log out users: {e}")

    def admin_archive_chat(self):
        """Admin action to archive chat history."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = os.path.join(
                os.path.dirname(self.controller.model.HISTORY_FILE),
                f"chat_history_archive_{timestamp}.json"
            )
            with open(self.controller.model.HISTORY_FILE, 'r') as src, open(archive_file, 'w') as dst:
                dst.write(src.read())
            # Clear current chat history
            with open(self.controller.model.HISTORY_FILE, 'w') as f:
                json.dump([], f)
            QMessageBox.information(self, "Success", f"Chat history archived to {archive_file}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to archive chat: {e}")

    def admin_archive_files(self):
        """Admin action to archive shared files list."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = os.path.join(
                os.path.dirname(self.controller.model.FILES_FILE),
                f"shared_files_archive_{timestamp}.json"
            )
            with open(self.controller.model.FILES_FILE, 'r') as src, open(archive_file, 'w') as dst:
                dst.write(src.read())
            # Clear current shared files
            with open(self.controller.model.FILES_FILE, 'w') as f:
                json.dump([], f)
            QMessageBox.information(self, "Success", f"Shared files list archived to {archive_file}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to archive files: {e}")

    def show_media_picker(self):
        """Show the media picker above the emoji button."""
        logger.debug("Media picker button clicked")
        # Get the global position of the media button
        button_pos = self.media_button.mapToGlobal(self.media_button.rect().topLeft())
        logger.debug(f"Button position: {button_pos}")
        # Position the media picker above the button
        self.chat_history.show_media_picker(button_pos)
        logger.debug("show_media_picker called on chat_history")
        
    def handle_media_message(self, message):
        """Handle messages from the media picker (emojis and GIFs)."""
        if message.startswith('GIF: '):
            # For GIFs, send the message directly
            self.handle_message_sent(message)
        else:
            # For emojis, append to the current input
            current_text = self.message_input.text()
            self.message_input.setText(current_text + message)
            self.message_input.setFocus()

    def handle_message_sent(self, message: str):
        """Handle when a message is sent from this instance."""
        if message:
            self.controller.send_message(message)
            # The message will be added to chat history through handle_message_received
            # when the controller emits the message_received signal
            
    def send_message(self):
        """Send the current message from the input field."""
        message = self.message_input.text().strip()
        if message:
            self.handle_message_sent(message)
            self.message_input.clear()

class AdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Actions")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Passcode input
        self.passcode_input = QLineEdit()
        self.passcode_input.setEchoMode(QLineEdit.Password)
        self.passcode_input.setPlaceholderText("Enter admin passcode")
        layout.addWidget(self.passcode_input)
        
        # Action buttons
        self.button_box = QDialogButtonBox()
        self.logout_all_btn = self.button_box.addButton("Log Out All Users", QDialogButtonBox.ActionRole)
        self.archive_chat_btn = self.button_box.addButton("Archive Chat History", QDialogButtonBox.ActionRole)
        self.archive_files_btn = self.button_box.addButton("Archive Shared Files", QDialogButtonBox.ActionRole)
        self.cancel_btn = self.button_box.addButton(QDialogButtonBox.Cancel)
        
        # Initially disable action buttons
        self.logout_all_btn.setEnabled(False)
        self.archive_chat_btn.setEnabled(False)
        self.archive_files_btn.setEnabled(False)
        
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        
        # Connect signals
        self.passcode_input.textChanged.connect(self.validate_passcode)
        self.cancel_btn.clicked.connect(self.reject)
        
    def validate_passcode(self, text):
        # Enable buttons if passcode is correct
        is_valid = (text == "admin123")  # You can change this passcode
        self.logout_all_btn.setEnabled(is_valid)
        self.archive_chat_btn.setEnabled(is_valid)
        self.archive_files_btn.setEnabled(is_valid)
