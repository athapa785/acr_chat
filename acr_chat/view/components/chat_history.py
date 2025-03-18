from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
import re
from datetime import datetime

class ChatHistory(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space
        
        self.messages = QTextBrowser()  # Changed from QTextEdit to QTextBrowser
        self.messages.setOpenExternalLinks(True)  # Allow opening links in browser
        self.messages.anchorClicked.connect(self.handle_link_click)
        
        # Set improved styling
        self.messages.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 12pt;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        
        # Create bottom bar with username and scroll button
        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        bottom_layout.setSpacing(5)
        
        # Username label
        self.username_label = QLabel()
        self.username_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #2196F3;
                padding: 2px;
            }
        """)
        
        # Scroll to bottom button
        self.scroll_button = QPushButton("↓")
        self.scroll_button.setFixedSize(30, 30)
        self.scroll_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.scroll_button.clicked.connect(self.scroll_to_bottom)
        self.scroll_button.setToolTip("Scroll to bottom")
        
        bottom_layout.addWidget(self.username_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.scroll_button)
        bottom_bar.setLayout(bottom_layout)
        
        layout.addWidget(self.messages)
        layout.addWidget(bottom_bar)
        self.setLayout(layout)
        
    def set_username(self, username: str):
        """Set the username display."""
        self.username_label.setText(f"Logged in as: {username}")
        
    def scroll_to_bottom(self):
        """Scroll the chat to the bottom."""
        scrollbar = self.messages.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear(self):
        """Clear all messages from the chat history."""
        self.messages.clear()
        
    def handle_link_click(self, url):
        """Handle clicking on links in the chat."""
        QDesktopServices.openUrl(url)
        
    def format_urls(self, text):
        """Convert URLs in text to HTML links."""
        # URL pattern matching http(s), ftp, file protocols and common TLDs
        url_pattern = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
        
        def replace_url(match):
            url = match.group(0)
            display_url = url[:50] + '...' if len(url) > 50 else url
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            return f'<a href="{url}" style="color: #2196F3; text-decoration: none;">{display_url}</a>'
            
        return re.sub(url_pattern, replace_url, text)
        
    def add_message(self, sender: str, content: str, timestamp: datetime = None):
        """Add a message to the chat history."""
        if timestamp is None:
            timestamp = datetime.now()
            
        # Format the timestamp
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Format URLs in the content
        formatted_content = self.format_urls(content)
        
        # Format the message with timestamp and convert URLs to links
        formatted_message = f'[{time_str}] <b>{sender}:</b> {formatted_content}'
        
        # Add the message
        self.messages.append(formatted_message) 