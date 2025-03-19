from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QScrollArea, QLabel, QGridLayout, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent
from PyQt5.QtGui import QIcon, QMovie, QKeyEvent
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MediaPicker(QWidget):
    emoji_selected = pyqtSignal(str)
    gif_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Initializing MediaPicker")
        # Set window flags to make it a popup that stays on top
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(237, 247, 255, 0.95);
                border: 1px solid #666;
                border-radius: 5px;
            }
            QLabel {
                color: white;
            }
            QScrollArea {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #666;
                border-radius: 5px;
            }
        """)
        self.setup_ui()
        
        # Set the GIF directory relative to the project root
        self.gif_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'gifs')
        os.makedirs(self.gif_dir, exist_ok=True)
        logger.debug(f"GIF directory set to: {self.gif_dir}")
        
        self.load_gifs()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Emoji section
        # Emoji section with pagination
        emoji_label = QLabel("Emojis")
        emoji_label.setStyleSheet("font-weight: bold; color: navy blue;")
        layout.addWidget(emoji_label)
        
        from PyQt5.QtWidgets import QStackedWidget, QHBoxLayout
        
        self.emoji_pages = QStackedWidget()
        self.emoji_pages.setFixedHeight(100)  # Allocate 100px height for emojis
        
        # Full list of 100 emojis (curated for work if needed; modify here if desired)
        emojis = [
            "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
            "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚",
            "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🥳",
            "🤩", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "⌛", "😣",
            "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬",
            "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗",
            "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯",
            "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐",
            "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "⏰",
            "✅", "⚠️", "📞", "🤡", "🔑", "👻", "💵", "💰", "👽", "🔔"
        ]
        
        # Split the 100 emojis into 3 pages:
        page1 = emojis[0:34]      # 34 emojis
        page2 = emojis[34:67]     # 33 emojis
        page3 = emojis[67:100]    # 33 emojis
        
        def create_emoji_page(emoji_list):
            page = QWidget()
            grid = QGridLayout(page)
            grid.setSpacing(3)
            cols = 8  # adjust the number of columns per page if desired
            for i, emoji in enumerate(emoji_list):
                btn = self.create_emoji_button(emoji)
                grid.addWidget(btn, i // cols, i % cols)
            return page
        
        self.emoji_pages.addWidget(create_emoji_page(page1))
        self.emoji_pages.addWidget(create_emoji_page(page2))
        self.emoji_pages.addWidget(create_emoji_page(page3))
        
        layout.addWidget(self.emoji_pages)
        
        # Add navigation buttons for emoji pages
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Prev")
        next_btn = QPushButton("Next")
        prev_btn.setFixedWidth(60)
        next_btn.setFixedWidth(60)
        prev_btn.clicked.connect(lambda: self.change_emoji_page(-1))
        next_btn.clicked.connect(lambda: self.change_emoji_page(1))
        nav_layout.addWidget(prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)
        layout.addLayout(nav_layout)
        
        # GIF section
        gif_label = QLabel("GIFs")
        gif_label.setStyleSheet("font-weight: bold; color: navy blue;")
        layout.addWidget(gif_label)
        
        self.gif_scroll = QScrollArea()
        self.gif_scroll.setWidgetResizable(True)
        self.gif_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #666;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        self.gif_container = QWidget()
        self.gif_layout = QGridLayout(self.gif_container)
        self.gif_layout.setSpacing(3)
        self.gif_scroll.setWidget(self.gif_container)
        
        layout.addWidget(self.gif_scroll)
        
        # Set a fixed size for the popup
        self.setFixedSize(300, 400)
        
    def create_emoji_button(self, emoji: str) -> QPushButton:
        """Create a button for an emoji."""
        logger.debug(f"Creating emoji button for: {emoji}")
        button = QPushButton(emoji)
        button.setFixedSize(30, 30)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
            }
        """)
        button.clicked.connect(lambda: self.emoji_selected.emit(emoji))
        return button

    def create_gif_button(self, gif_path: str) -> QPushButton:
        logger.debug(f"Creating animated GIF button for: {gif_path}")
        button = QPushButton()
        button.setFixedSize(80, 80)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
            }
        """)

        label = QLabel(button)
        label.setFixedSize(70, 70)
        label.setAlignment(Qt.AlignCenter)

        movie = QMovie(gif_path)
        movie.setScaledSize(label.size())
        label.setMovie(movie)
        movie.start()

        button.clicked.connect(lambda: self.gif_selected.emit(gif_path))
        return button

    def load_gifs(self):
        """Load GIFs from the resources directory."""
        try:
            if not os.path.exists(self.gif_dir):
                print(f"GIF directory not found: {self.gif_dir}")
                return
                
            gif_files = [f for f in os.listdir(self.gif_dir) if f.lower().endswith(('.gif', '.png', '.jpg', '.jpeg'))]
            
            for i, gif_file in enumerate(gif_files):
                gif_path = os.path.join(self.gif_dir, gif_file)
                btn = self.create_gif_button(gif_path)
                self.gif_layout.addWidget(btn, i // 3, i % 3)
                
        except Exception as e:
            print(f"Error loading GIFs: {e}") 


    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Hide the media picker immediately.
            self.hide()
            # Find the QLineEdit with objectName "message_input" and trigger its returnPressed signal.
            for widget in QApplication.allWidgets():
                if isinstance(widget, QLineEdit) and widget.objectName() == "message_input":
                    widget.setFocus()
                    widget.returnPressed.emit()
                    break
            event.accept()
        else:
            super().keyPressEvent(event)


    def change_emoji_page(self, delta):
        current_index = self.emoji_pages.currentIndex()
        count = self.emoji_pages.count()
        new_index = (current_index + delta) % count
        self.emoji_pages.setCurrentIndex(new_index)