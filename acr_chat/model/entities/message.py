from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    sender: str
    content: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        return Message(
            sender=data['sender'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        ) 