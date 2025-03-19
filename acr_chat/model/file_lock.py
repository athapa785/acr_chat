import fcntl
import os

class FileLock:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock_file = None
        
    def __enter__(self):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # If the file doesn't exist, create it in write mode
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                f.write('[]')  # Initialize with empty JSON array
                
        # Open the file in read-write mode
        self.lock_file = open(self.file_path, 'r+')
        
        # Acquire an exclusive lock
        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX)
        
        # Seek to beginning of file
        self.lock_file.seek(0)
        
        return self.lock_file
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_file:
            # Release the lock
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close() 