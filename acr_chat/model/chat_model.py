import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple, Optional

from .entities import Message, SharedFile
from .file_lock import FileLock
from ..utils import get_admin_passcode

class ChatModel:
    _instance = None
    HISTORY_FILE = os.path.join(os.path.expanduser('~'), '.acr_chat', 'chat_history.json')
    USERS_FILE = os.path.join(os.path.expanduser('~'), '.acr_chat', 'active_users.json')
    FILES_FILE = os.path.join(os.path.expanduser('~'), '.acr_chat', 'shared_files.json')
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        # Initialize empty collections first
        self.active_users: Set[str] = set()
        self.messages: List[Message] = []
        self.shared_files: List[SharedFile] = []
        
        # Create directory and files if they don't exist
        self._ensure_files_exist()
        
        # Load data from files
        self.load_chat_history()
        self.load_active_users()
        self.load_shared_files()
        
    def _ensure_files_exist(self):
        """Ensure that all required files exist."""
        try:
            os.makedirs(os.path.dirname(self.HISTORY_FILE), exist_ok=True)
            
            if not os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, 'w') as f:
                    with FileLock(f):
                        json.dump([], f, indent=2)
                
            if not os.path.exists(self.USERS_FILE):
                with open(self.USERS_FILE, 'w') as f:
                    with FileLock(f):
                        json.dump([], f, indent=2)
                
            if not os.path.exists(self.FILES_FILE):
                with open(self.FILES_FILE, 'w') as f:
                    with FileLock(f):
                        json.dump([], f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to create necessary files: {str(e)}")
    
    def add_message(self, sender: str, content: str, timestamp: datetime = None) -> None:
        if timestamp is None:
            timestamp = datetime.now()
        message = Message(sender=sender, content=content, timestamp=timestamp)
        self.messages.append(message)
        self.save_chat_history()
        
    def add_shared_file(self, filepath: str, shared_by: str) -> None:
        shared_file = SharedFile(
            filepath=filepath,
            shared_by=shared_by,
            timestamp=datetime.now()
        )
        self.shared_files.append(shared_file)
        self.save_shared_files()
        
    def add_user(self, username: str) -> Tuple[bool, Optional[str]]:
        """Add a user if not already present.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            # Always reload to get fresh state
            self.load_active_users()
            
            if not username or not username.strip():
                return False, "Username cannot be empty"
                
            if username in self.active_users:
                return False, "Username already taken"
                
            self.active_users.add(username)
            self.save_active_users()
            return True, None
        except Exception as e:
            return False, f"Failed to add user: {str(e)}"
        
    def remove_user(self, username: str) -> Tuple[bool, Optional[str]]:
        """Remove a user from active users.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            # Always reload to get fresh state
            self.load_active_users()
            
            if username in self.active_users:
                self.active_users.remove(username)
                self.save_active_users()
                return True, None
            return False, "User not found"
        except Exception as e:
            return False, f"Failed to remove user: {str(e)}"
            
    def get_all_users(self) -> List[str]:
        try:
            self.load_active_users()  # Always reload to get fresh state
            return sorted(list(self.active_users))
        except Exception:
            return []
        
    def get_all_messages(self) -> List[Message]:
        try:
            # Always reload to get fresh state
            self.load_chat_history()
            return sorted(self.messages, key=lambda m: m.timestamp)
        except Exception:
            return []
        
    def get_shared_files(self) -> List[SharedFile]:
        try:
            # Always reload to get fresh state
            self.load_shared_files()
            # Filter out files that no longer exist
            self.shared_files = [f for f in self.shared_files if Path(f.filepath).exists()]
            self.save_shared_files()
            return sorted(self.shared_files, key=lambda f: f.timestamp, reverse=True)
        except Exception:
            return []
        
    def load_chat_history(self) -> None:
        try:
            with open(self.HISTORY_FILE, 'r') as f:
                with FileLock(f):
                    data = json.load(f)
                    self.messages = [Message.from_dict(msg) for msg in data]
        except Exception:
            self.messages = []
            
    def save_chat_history(self) -> None:
        try:
            with open(self.HISTORY_FILE, 'w') as f:
                with FileLock(f):
                    json.dump([msg.to_dict() for msg in self.messages], f, indent=2)
        except Exception as e:
            print(f"Failed to save chat history: {e}")
            
    def load_active_users(self) -> None:
        try:
            with open(self.USERS_FILE, 'r') as f:
                with FileLock(f):
                    data = json.load(f)
                    self.active_users = set(data)
        except Exception:
            self.active_users = set()
            
    def save_active_users(self) -> None:
        try:
            with open(self.USERS_FILE, 'w') as f:
                with FileLock(f):
                    json.dump(list(self.active_users), f, indent=2)
        except Exception as e:
            print(f"Failed to save active users: {e}")
            
    def load_shared_files(self) -> None:
        try:
            with open(self.FILES_FILE, 'r') as f:
                with FileLock(f):
                    data = json.load(f)
                    self.shared_files = [SharedFile.from_dict(file) for file in data]
        except Exception:
            self.shared_files = []
            
    def save_shared_files(self) -> None:
        try:
            with open(self.FILES_FILE, 'w') as f:
                with FileLock(f):
                    json.dump([file.to_dict() for file in self.shared_files], f, indent=2)
        except Exception as e:
            print(f"Failed to save shared files: {e}")
            
    def clear_all_users(self) -> None:
        """Admin function to log out all users."""
        try:
            self.active_users.clear()
            self.save_active_users()
        except Exception as e:
            print(f"Failed to clear users: {e}")
            
    def archive_chat_history(self) -> Tuple[bool, Optional[str]]:
        """Admin function to archive current chat and start fresh.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_or_archive_path)
        """
        try:
            # Create archives directory if it doesn't exist
            archives_dir = os.path.join(os.path.dirname(self.HISTORY_FILE), 'archives')
            os.makedirs(archives_dir, exist_ok=True)
            
            # Generate archive filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_path = os.path.join(archives_dir, f'chat_history_{timestamp}.json')
            
            # Copy current history to archive
            shutil.copy2(self.HISTORY_FILE, archive_path)
            
            # Clear current history
            self.messages.clear()
            self.save_chat_history()
            
            return True, archive_path
        except Exception as e:
            return False, f"Failed to archive chat: {str(e)}"
            
    def archive_shared_files(self) -> Tuple[bool, Optional[str]]:
        """Admin function to archive current shared files list and start fresh.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_or_archive_path)
        """
        try:
            # Create archives directory if it doesn't exist
            archives_dir = os.path.join(os.path.dirname(self.FILES_FILE), 'archives')
            os.makedirs(archives_dir, exist_ok=True)
            
            # Generate archive filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_path = os.path.join(archives_dir, f'shared_files_{timestamp}.json')
            
            # Copy current shared files to archive
            shutil.copy2(self.FILES_FILE, archive_path)
            
            # Clear current shared files
            self.shared_files.clear()
            self.save_shared_files()
            
            return True, archive_path
        except Exception as e:
            return False, f"Failed to archive shared files: {str(e)}"
            
    @classmethod
    def verify_admin_passcode(cls, passcode: str) -> bool:
        """Verify if the provided passcode matches the admin passcode."""
        return passcode == get_admin_passcode() 