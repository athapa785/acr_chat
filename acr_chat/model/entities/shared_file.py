from dataclasses import dataclass
from datetime import datetime

@dataclass
class SharedFile:
    filepath: str
    shared_by: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            'filepath': self.filepath,
            'shared_by': self.shared_by,
            'timestamp': self.timestamp.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        return SharedFile(
            filepath=data['filepath'],
            shared_by=data['shared_by'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        ) 