from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QEvent

class ChatInput(QWidget):
    message_sent = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(60)  # Increased height
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                font-family: Arial, sans-serif;
                font-size: 12pt;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        
        # Install event filter to capture key events
        self.message_input.installEventFilter(self)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(80)  # Slightly wider
        self.send_button.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                padding: 8px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        
        self.setLayout(layout)
        
    def eventFilter(self, obj, event):
        """Handle key events in the message input."""
        if obj == self.message_input and event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # Check for Return/Enter key
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                # If Shift is pressed, allow new line
                if modifiers & Qt.ShiftModifier:
                    return False  # Let the event be handled normally (new line)
                else:
                    # Send message and prevent default handling
                    self.send_message()
                    return True  # Event handled, don't propagate
                    
        return super().eventFilter(obj, event)
        
    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.message_input.clear() 