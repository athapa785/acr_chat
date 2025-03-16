import fcntl

class FileLock:
    def __init__(self, file):
        self.file = file
        
    def __enter__(self):
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        return self.file
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.flock(self.file.fileno(), fcntl.LOCK_UN) 