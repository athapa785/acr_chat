import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple, Optional

from .entities import Message, SharedFile
from .file_lock import FileLock

class ChatModel:
    _instance = None
    HISTORY_FILE = os.path.join(os.path.expanduser('~'), '.acr_chat', 'chat_history.json')
    USERS_FILE = os.path.join(os.path.expanduser('~'), '.acr_chat', 'active_users.json')
    FILES_FILE = os.path.join(os.path.expanduser('~'), '.acr_chat', 'shared_files.json')
    ADMIN_PASSCODE = "acr2024"  # Hardcoded admin passcode
    
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
                with FileLock(self.HISTORY_FILE) as f:
                    f.seek(0)
                    json.dump([], f, indent=2)
                
            if not os.path.exists(self.USERS_FILE):
                with FileLock(self.USERS_FILE) as f:
                    f.seek(0)
                    json.dump([], f, indent=2)
                
            if not os.path.exists(self.FILES_FILE):
                with FileLock(self.FILES_FILE) as f:
                    f.seek(0)
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
                # Don't merge with existing users when removing
                with FileLock(self.USERS_FILE) as f:
                    f.seek(0)
                    f.truncate()
                    json.dump(list(self.active_users), f, indent=2)
                return True, None
            return False, "User not found"
        except Exception as e:
            return False, f"Failed to remove user: {str(e)}"
            
    def get_all_users(self) -> List[str]:
        """Get list of all active users."""
        try:
            self.load_active_users()  # Always reload to get fresh state
            return sorted(list(self.active_users))
        except Exception:
            return []
        
    def get_all_messages(self) -> List[Message]:
        """Get list of all messages."""
        try:
            self.load_chat_history()  # Always reload to get fresh state
            return sorted(self.messages, key=lambda m: m.timestamp)
        except Exception:
            return []
        
    def get_shared_files(self) -> List[SharedFile]:
        """Get list of shared files."""
        try:
            self.load_shared_files()  # Always reload to get fresh state
            # Filter out files that no longer exist
            self.shared_files = [f for f in self.shared_files if Path(f.filepath).exists()]
            return sorted(self.shared_files, key=lambda f: f.timestamp, reverse=True)
        except Exception:
            return []
        
    def load_chat_history(self) -> None:
        """Load chat history from file."""
        try:
            with FileLock(self.HISTORY_FILE) as f:
                try:
                    data = json.load(f)
                    self.messages = [Message.from_dict(msg) for msg in data]
                except json.JSONDecodeError:
                    self.messages = []
        except Exception:
            self.messages = []
            
    def save_chat_history(self) -> None:
        """Save chat history to file."""
        try:
            with FileLock(self.HISTORY_FILE) as f:
                f.seek(0)
                f.truncate()
                json.dump([msg.to_dict() for msg in self.messages], f, indent=2)
        except Exception:
            pass
            
    def load_active_users(self) -> None:
        """Load active users from file."""
        try:
            with FileLock(self.USERS_FILE) as f:
                try:
                    data = json.load(f)
                    self.active_users = set(data)
                except json.JSONDecodeError:
                    self.active_users = set()
        except Exception:
            self.active_users = set()
            
    def save_active_users(self) -> None:
        """Save active users to file."""
        try:
            with FileLock(self.USERS_FILE) as f:
                # Read existing users first
                try:
                    f.seek(0)
                    existing_users = set(json.load(f))
                except json.JSONDecodeError:
                    existing_users = set()
                
                # Merge with current users
                all_users = existing_users | self.active_users
                
                # Write back all users
                f.seek(0)
                f.truncate()
                json.dump(list(all_users), f, indent=2)
        except Exception:
            pass
            
    def load_shared_files(self) -> None:
        """Load shared files from file."""
        try:
            with FileLock(self.FILES_FILE) as f:
                try:
                    data = json.load(f)
                    self.shared_files = [SharedFile.from_dict(file) for file in data]
                except json.JSONDecodeError:
                    self.shared_files = []
        except Exception:
            self.shared_files = []
            
    def save_shared_files(self) -> None:
        """Save shared files to file."""
        try:
            with FileLock(self.FILES_FILE) as f:
                f.seek(0)
                f.truncate()
                json.dump([file.to_dict() for file in self.shared_files], f, indent=2)
        except Exception:
            pass

    def clear_active_users(self):
        """Clear all active users (admin function)."""
        with FileLock(self.USERS_FILE):
            with open(self.USERS_FILE, 'w') as f:
                json.dump([], f)
        self.active_users.clear() 