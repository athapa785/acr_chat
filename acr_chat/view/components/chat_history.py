from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from datetime import datetime

class ChatHistory(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space
        
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        
        # Set improved styling
        self.messages.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 12pt;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(self.messages)
        self.setLayout(layout)
        
    def clear(self):
        """Clear all messages from the chat history."""
        self.messages.clear()
        
    def add_message(self, sender: str, content: str, timestamp: datetime = None):
        """Add a message to the chat history and scroll to it."""
        if timestamp is None:
            timestamp = datetime.now()
            
        # Format the timestamp
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Format the message with timestamp
        formatted_message = f'[{time_str}] <b>{sender}:</b> {content}'
        
        # Add the message
        self.messages.append(formatted_message)
        
        # Scroll to the bottom
        scrollbar = self.messages.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum()) 