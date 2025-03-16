from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                          QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                          QFileDialog, QMenu, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path

class DirectoryView(QWidget):
    file_selected = pyqtSignal(str)
    file_added = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        
        title = QLabel("Shared Files")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 12pt; font-weight: bold; padding: 5px;")
        
        # Add file controls
        controls_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Add File")
        self.add_file_button.setStyleSheet("""
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
        self.add_file_button.clicked.connect(self.browse_file)
        controls_layout.addWidget(self.add_file_button)
        
        # Create table for files
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["File Name", "Shared By", "Time"])
        self.files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_table.customContextMenuRequested.connect(self.show_context_menu)
        self.files_table.itemDoubleClicked.connect(self.handle_double_click)
        
        # Style the table
        self.files_table.setStyleSheet("""
            QTableWidget {
                font-size: 12pt;
                gridline-color: #ddd;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                font-size: 12pt;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        # Set column widths
        header = self.files_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # File name takes remaining space
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Shared by
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Time
        
        layout.addWidget(title)
        layout.addLayout(controls_layout)
        layout.addWidget(self.files_table)
        
        self.setLayout(layout)
        self.setMinimumWidth(450)  # Slightly wider for better readability
        
    def browse_file(self):
        """Open file selection dialog."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Share",
            str(Path.home()),
            "All Files (*.*)"
        )
        
        if filepath:
            self.file_added.emit(filepath)
            
    def show_context_menu(self, position):
        """Show context menu for file operations."""
        menu = QMenu()
        selected_items = self.files_table.selectedItems()
        
        if selected_items:
            row = selected_items[0].row()
            file_path = self.files_table.item(row, 0).data(Qt.UserRole)  # Get full path from data
            menu.addAction("Open", lambda: self.handle_file_action(file_path, "open"))
            menu.addAction("Copy Path", lambda: self.handle_file_action(file_path, "copy"))
            
        menu.exec_(self.files_table.mapToGlobal(position))
        
    def handle_double_click(self, item):
        """Handle double click on table item."""
        row = item.row()
        file_path = self.files_table.item(row, 0).data(Qt.UserRole)  # Get full path from data
        self.handle_file_action(file_path, "open")
        
    def handle_file_action(self, file_path: str, action: str):
        """Handle file actions (open/copy)."""
        if action == "open":
            self.file_selected.emit(file_path)
        elif action == "copy":
            QApplication.clipboard().setText(file_path)
        
    def update_files(self, shared_files: list):
        """Update the table with shared files."""
        self.files_table.setRowCount(0)  # Clear table
        
        for shared_file in shared_files:
            row = self.files_table.rowCount()
            self.files_table.insertRow(row)
            
            # File name (store full path in UserRole)
            name_item = QTableWidgetItem(Path(shared_file.filepath).name)
            name_item.setData(Qt.UserRole, shared_file.filepath)
            self.files_table.setItem(row, 0, name_item)
            
            # Shared by
            self.files_table.setItem(row, 1, QTableWidgetItem(shared_file.shared_by))
            
            # Time (format nicely)
            time_str = shared_file.timestamp.strftime("%Y-%m-%d %H:%M")
            self.files_table.setItem(row, 2, QTableWidgetItem(time_str))
            
        self.files_table.sortItems(2, Qt.DescendingOrder)  # Sort by time, newest first 