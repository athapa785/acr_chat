from typing import Optional, List
from ..model.chat_model import ChatModel, Message, SharedFile
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime

class ChatController(QObject):
    # Signals for view updates
    user_added = pyqtSignal(str)
    user_removed = pyqtSignal(str)
    message_received = pyqtSignal(str, str, datetime)  # sender, content, timestamp
    files_updated = pyqtSignal(list)  # List[SharedFile]
    login_failed = pyqtSignal(str)  # error message
    
    ADMIN_PASSWORD = "admin123"  # Hardcoded admin password
    
    def __init__(self):
        super().__init__()
        self.model = ChatModel()
        self.current_user: Optional[str] = None
        
    def attempt_login(self, username: str, password: str = None) -> bool:
        """Try to log in with the given username and optional admin password."""
        if not username.strip():
            self.login_failed.emit("Username cannot be empty")
            return False
            
        # Check for admin login
        if username.lower() == "admin":
            if password != self.ADMIN_PASSWORD:
                self.login_failed.emit("Invalid admin password")
                return False
                
        success, error_msg = self.model.add_user(username)
        if success:
            self.current_user = username
            self.user_added.emit(username)
            return True
        else:
            self.login_failed.emit(error_msg or "Login failed")
            return False
            
    def logout(self):
        """Log out the current user."""
        if self.current_user:
            success, _ = self.model.remove_user(self.current_user)
            if success:
                # Notify other instances about the user removal
                self.user_removed.emit(self.current_user)
            self.current_user = None
            
    def send_message(self, content: str):
        """Send a message from the current user."""
        if self.current_user and content.strip():
            timestamp = datetime.now()
            self.model.add_message(self.current_user, content, timestamp)
            # Notify all instances about the new message
            self.message_received.emit(self.current_user, content, timestamp)
            # Also notify about any user changes
            self.user_added.emit(self.current_user)
            
    def get_all_users(self) -> List[str]:
        """Get list of all active users."""
        return self.model.get_all_users()
        
    def get_chat_history(self) -> List[Message]:
        """Get all messages in the chat."""
        return self.model.get_all_messages()
        
    def get_shared_files(self) -> List[SharedFile]:
        """Get list of shared files."""
        return self.model.get_shared_files()
        
    def add_shared_file(self, filepath: str) -> bool:
        """Add a file to the shared files list."""
        if self.current_user:
            self.model.add_shared_file(filepath, self.current_user)
            # Notify about the new file
            self.files_updated.emit(self.model.get_shared_files())
            # Also notify about any user changes
            self.user_added.emit(self.current_user)
            return True
        return False
        
    def set_shared_directory(self, path: str):
        """Set and update the shared directory."""
        self.model.set_shared_directory(path)
        self.files_updated.emit(self.model.get_shared_files())
        
    def refresh_shared_files(self):
        """Refresh the list of shared files."""
        self.files_updated.emit(self.model.get_shared_files()) 