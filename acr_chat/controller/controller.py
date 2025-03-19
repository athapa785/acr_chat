from typing import Optional, List
from ..model.chat_model import ChatModel, Message, SharedFile
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
import os

class ChatController(QObject):
    # Signals for view updates
    user_added = pyqtSignal(str)
    user_removed = pyqtSignal(str)
    message_received = pyqtSignal(str, str, datetime)  # sender, content, timestamp
    files_updated = pyqtSignal(list)  # List[SharedFile]
    login_failed = pyqtSignal(str)  # error message
    
    ADMIN_PASSWORD = "admin123"  # Hardcoded admin password
    
    def __init__(self, model=None):
        super().__init__()
        self.model = model or ChatModel()
        self.current_user: Optional[str] = None
        
    def attempt_login(self, username: str, password: str) -> bool:
        """Attempt to log in with the given credentials."""
        try:
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
        except Exception as e:
            self.login_failed.emit(str(e))
            return False
            
    def logout(self):
        """Log out the current user."""
        if self.current_user:
            success, _ = self.model.remove_user(self.current_user)
            if success:
                self.user_removed.emit(self.current_user)
                self.current_user = None
            
    def send_message(self, message):
        """Send a message to the chat."""
        try:
            # Check if it's a GIF message
            if message.startswith('GIF: '):
                gif_path = message[5:]  # Remove 'GIF: ' prefix
                # Verify the GIF file exists
                if not os.path.exists(gif_path):
                    raise FileNotFoundError(f"GIF file not found: {gif_path}")
                message = f"GIF: {gif_path}"
            
            # Add the message using the model's method
            self.model.add_message(self.current_user, message)
            
        except Exception as e:
            print(f"Error sending message: {e}")
            
    def get_all_users(self) -> List[str]:
        """Get a list of all active users."""
        return self.model.get_all_users()
        
    def get_chat_history(self) -> List[Message]:
        """Get all messages in the chat."""
        return self.model.get_all_messages()
        
    def get_shared_files(self) -> List[SharedFile]:
        """Get list of shared files."""
        return self.model.get_shared_files()
        
    def add_shared_file(self, filepath: str) -> bool:
        """Add a file to the shared files list."""
        try:
            if self.model.add_shared_file(filepath):
                self.files_updated.emit(self.model.get_shared_files())
                return True
            return False
        except Exception as e:
            print(f"Error adding shared file: {e}")
            return False
        
    def set_shared_directory(self, path: str):
        """Set and update the shared directory."""
        self.model.set_shared_directory(path)
        self.files_updated.emit(self.model.get_shared_files())
        
    def refresh_shared_files(self):
        """Refresh the list of shared files."""
        self.files_updated.emit(self.model.get_shared_files()) 