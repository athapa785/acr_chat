from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                         QSplitter, QLabel, QMessageBox, QApplication, QPushButton)
from PyQt5.QtCore import Qt, QFileSystemWatcher
from .components import ChatInput, ChatHistory, UsersList, DirectoryView, LoginDialog, AdminDialog
from ..controller.controller import ChatController
from datetime import datetime
import os
import subprocess
import platform

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = ChatController()
        self.setup_controller_connections()
        
        # Initialize UI components to None
        self.users_list = None
        self.chat_history = None
        self.chat_input = None
        self.directory_view = None
        
        # Set up file watchers
        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath(self.controller.model.HISTORY_FILE)
        self.watcher.addPath(self.controller.model.USERS_FILE)
        self.watcher.fileChanged.connect(self.on_file_changed)
        
        self.init_login()
        
    def setup_controller_connections(self):
        """Set up signal connections from controller."""
        self.controller.user_added.connect(self.on_user_added)
        self.controller.user_removed.connect(self.on_user_removed)
        self.controller.message_received.connect(self.on_message_received)
        self.controller.files_updated.connect(self.on_files_updated)
        self.controller.login_failed.connect(self.on_login_failed)
        
    def init_login(self):
        """Initialize login dialog."""
        username = LoginDialog.get_username(self)
        if username and self.controller.attempt_login(username):
            self.setWindowTitle(f"ACR Chat - {username}")
            self.init_ui()
            # Load existing data after UI is initialized
            self.update_users_list(self.controller.get_all_users())
            # Load chat history with timestamps
            messages = self.controller.get_chat_history()
            for msg in messages:
                self.chat_history.add_message(
                    msg.sender,
                    msg.content,
                    msg.timestamp
                )
        else:
            self.close()
            
    def init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding around the edges
        main_widget.setLayout(main_layout)
        
        # Create left panel for users list and admin button
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header with admin button and "Online Users" label
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add admin button (small and discrete)
        admin_button = QPushButton("⚙")  # Gear emoji as icon
        admin_button.setFixedSize(24, 24)
        admin_button.setToolTip("Admin Functions")
        admin_button.clicked.connect(self.show_admin_dialog)
        admin_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Add "Online Users" label
        users_label = QLabel("Online Users")
        users_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #2196F3;
            }
        """)
        
        header_layout.addWidget(admin_button)
        header_layout.addWidget(users_label)
        header_layout.addStretch()
        header_widget.setLayout(header_layout)
        
        left_layout.addWidget(header_widget)
        self.users_list = UsersList()
        left_layout.addWidget(self.users_list)
        left_panel.setLayout(left_layout)
        
        # Create center panel for chat
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize chat space
        center_widget.setLayout(center_layout)
        
        # Add username display
        username_label = QLabel(f"Logged in as: {self.controller.current_user}")
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #2196F3;
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
        """)
        center_layout.addWidget(username_label)
        
        self.chat_history = ChatHistory()
        self.chat_input = ChatInput()
        
        center_layout.addWidget(self.chat_history, stretch=1)  # Give chat history all available vertical space
        center_layout.addWidget(self.chat_input)
        
        # Create right panel for directory view
        self.directory_view = DirectoryView()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_widget)
        splitter.addWidget(self.directory_view)
        
        # Set initial sizes (users:chat:files ratio of 1:3:1.5)
        total_width = 1000  # Use a base width for proportions
        users_width = total_width // 6     # ~17%
        files_width = total_width // 4     # 25%
        chat_width = total_width - users_width - files_width  # Remaining space
        splitter.setSizes([users_width, chat_width, files_width])
        
        main_layout.addWidget(splitter)
        
        # Connect signals
        self.chat_input.message_sent.connect(self.handle_message_sent)
        self.users_list.user_selected.connect(self.handle_user_selected)
        self.directory_view.file_selected.connect(self.handle_file_selected)
        self.directory_view.file_added.connect(self.handle_file_added)
        
        # Set up file watcher for shared files
        self.watcher.addPath(self.controller.model.FILES_FILE)
        
        # Load initial shared files
        self.directory_view.update_files(self.controller.get_shared_files())
        
        # Set window size and position
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() // 6,      # X position
            screen.height() // 6,     # Y position
            (screen.width() * 2) // 3,  # Width (2/3 of screen width)
            (screen.height() * 2) // 3  # Height (2/3 of screen height)
        )
        
        # Make window visible
        self.show()
        
    def closeEvent(self, event):
        """Handle window close event."""
        self.controller.logout()
        event.accept()
        
    # Signal handlers
    def handle_message_sent(self, message: str):
        """Handle when a message is sent from this instance."""
        self.controller.send_message(message)
        # Update users list in case it changed
        self.update_users_list(self.controller.get_all_users())
        
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
            
    def on_user_added(self, username: str):
        """Handle when a new user joins."""
        if self.users_list:
            self.update_users_list(self.controller.get_all_users())
        
    def on_user_removed(self, username: str):
        """Handle when a user leaves."""
        if self.users_list:
            self.update_users_list(self.controller.get_all_users())
        
    def on_message_received(self, sender: str, content: str, timestamp: datetime):
        """Handle when a new message is received from any instance."""
        if self.chat_history:
            self.chat_history.add_message(sender, content, timestamp)
            # Update users list in case it changed
            self.update_users_list(self.controller.get_all_users())
        
    def on_files_updated(self, files: list):
        if self.directory_view:
            self.directory_view.update_files(files)
        
    def on_login_failed(self, error_msg: str):
        QMessageBox.warning(self, "Login Error", error_msg)
        
    def update_users_list(self, users: list):
        if self.users_list:
            self.users_list.update_users(users)
        
    def on_file_changed(self, path: str):
        """Handle when any watched file changes."""
        if path == self.controller.model.FILES_FILE:
            # Reload shared files
            self.directory_view.update_files(self.controller.get_shared_files())
        elif path == self.controller.model.HISTORY_FILE:
            # Reload messages
            messages = self.controller.get_chat_history()
            if self.chat_history:
                # Clear current messages
                self.chat_history.clear()
                # Add all messages
                for msg in messages:
                    self.chat_history.add_message(
                        msg.sender,
                        msg.content,
                        msg.timestamp
                    )
        elif path == self.controller.model.USERS_FILE:
            # Reload users
            if self.users_list:
                self.update_users_list(self.controller.get_all_users())
                
        # Re-add the path to the watcher
        self.watcher.addPath(path)

    def show_admin_dialog(self):
        """Show the admin dialog and handle admin functions."""
        passcode = AdminDialog.get_passcode(self)
        if passcode and self.controller.model.verify_admin_passcode(passcode):
            # Create admin actions dialog with separate buttons
            admin_dialog = QMessageBox(self)
            admin_dialog.setWindowTitle("Admin Actions")
            admin_dialog.setText("Choose an administrative action:")
            
            # Add custom buttons
            clear_users = admin_dialog.addButton("Clear Online Users", QMessageBox.ActionRole)
            archive_chat = admin_dialog.addButton("Archive Chat History", QMessageBox.ActionRole)
            archive_files = admin_dialog.addButton("Archive Shared Files", QMessageBox.ActionRole)
            cancel = admin_dialog.addButton(QMessageBox.Cancel)
            
            admin_dialog.exec_()
            clicked_button = admin_dialog.clickedButton()
            
            if clicked_button == clear_users:
                self.controller.model.clear_all_users()
                QMessageBox.information(self, "Success", "All users have been logged out.")
                self.close()  # Close this instance too
                
            elif clicked_button == archive_chat:
                success, result = self.controller.model.archive_chat_history()
                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Chat history has been archived to:\n{result}\n\nA new chat has been started."
                    )
                    # Refresh the chat history display
                    self.chat_history.clear()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to archive chat: {result}")
                    
            elif clicked_button == archive_files:
                success, result = self.controller.model.archive_shared_files()
                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Shared files list has been archived to:\n{result}\n\nShared files list has been cleared."
                    )
                    # Refresh the files display
                    self.directory_view.update_files([])
                else:
                    QMessageBox.warning(self, "Error", f"Failed to archive shared files: {result}")
        
        elif passcode:  # Wrong passcode
            QMessageBox.warning(self, "Error", "Invalid admin passcode!")
