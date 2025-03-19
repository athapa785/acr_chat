from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QMovie
import re
import os
from datetime import datetime
import logging
from .media_picker import MediaPicker

logger = logging.getLogger(__name__)

class ChatHistory(QWidget):
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Initializing ChatHistory")
        self.current_username = None
        self.setup_ui()
        
        # Initialize MediaPicker with the gif directory
        self.media_picker = MediaPicker(self)
        self.media_picker.emoji_selected.connect(self.handle_emoji_selection)
        self.media_picker.gif_selected.connect(self.handle_gif_selection)
        logger.debug("MediaPicker initialized and signals connected")
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create a scroll area to contain messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: white; }")
        
        # Create a container widget and a vertical layout for messages
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(5)
        self.scroll_area.setWidget(self.messages_widget)
        
        layout.addWidget(self.scroll_area)
        
        # Bottom bar: username label and scroll button
        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(5, 2, 5, 2)
        
        self.username_label = QLabel()
        self.username_label.setStyleSheet("QLabel { color: #666; font-size: 10pt; }")
        bottom_layout.addWidget(self.username_label)
        
        self.scroll_button = QPushButton("⬇")
        self.scroll_button.setFixedSize(30, 30)
        self.scroll_button.setToolTip("Scroll to bottom")
        self.scroll_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.scroll_button.clicked.connect(self.scroll_to_bottom)
        bottom_layout.addWidget(self.scroll_button)
        
        layout.addWidget(bottom_bar)
        
    def set_username(self, username: str):
        self.current_username = username
        self.username_label.setText(f"Logged in as: {username}")
        
    def add_text_message(self, sender: str, content: str, timestamp: datetime):
        # Create a QLabel to display the text message with rich HTML
        label = QLabel()
        label.setOpenExternalLinks(True)
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        # Escape HTML-sensitive characters
        content_escaped = (content.replace("&", "&amp;")
                                   .replace("<", "&lt;")
                                   .replace(">", "&gt;"))
        # Convert URLs into clickable links
        url_pattern = r'(https?://[^\s]+)'
        content_with_links = re.sub(url_pattern, r'<a href="\1">\1</a>', content_escaped)
        formatted_message = (
            f'<span style="color:#666;font-size:12px;">[{timestamp.strftime("%H:%M:%S")}]</span> '
            f'<span style="color:{"#2196F3" if sender==self.current_username else "#212121"};font-weight:bold;">{sender}:</span> '
            f'<span style="color:#333;font-size:12px">{content_with_links}</span>'
        )
        label.setText(formatted_message)
        label.setStyleSheet("QLabel { padding: 5px; }")
        self.messages_layout.addWidget(label)
        self.scroll_to_bottom()
        
    def add_gif_message(self, sender: str, gif_path: str, timestamp: datetime):
        if os.path.exists(gif_path):
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(2)
            
            header_label = QLabel()
            header_label.setText(
                f'<span style="color:#666;font-size:10px;">[{timestamp.strftime("%H:%M:%S")}]</span> '
                f'<span style="color:{"#2196F3" if sender==self.current_username else "#212121"};font-weight:bold;">{sender}:</span>'
            )
            container_layout.addWidget(header_label)
            
            gif_label = QLabel()
            gif_movie = QMovie(gif_path)
            gif_movie.setScaledSize(QSize(200, 200))
            gif_label.setMovie(gif_movie)
            gif_movie.start()
            container_layout.addWidget(gif_label)
            
            self.messages_layout.addWidget(container)
            self.scroll_to_bottom()
        else:
            self.add_text_message(sender, "[GIF not found]", timestamp)
            
    def add_message(self, sender: str, content: str, timestamp: datetime):
        if content.startswith("GIF: "):
            gif_path = content[5:].strip()
            self.add_gif_message(sender, gif_path, timestamp)
        else:
            self.add_text_message(sender, content, timestamp)

    def scroll_to_bottom(self):
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
            
    def clear(self):
        for i in reversed(range(self.messages_layout.count())):
            widget = self.messages_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
    def show_media_picker(self, pos):
        logger.debug(f"Showing media picker at position: {pos}")
        self.media_picker.move(pos.x(), pos.y() - self.media_picker.height() - 5)
        self.media_picker.show()
        self.media_picker.setFocus()
        logger.debug("Media picker shown and focus set")
        
    def handle_emoji_selection(self, emoji: str):
        logger.debug(f"Emoji selected: {emoji}")
        self.message_sent.emit(emoji)
        
    def handle_gif_selection(self, gif_path: str):
        logger.debug(f"GIF selected: {gif_path}")
        self.message_sent.emit(f"GIF: {gif_path}")

    