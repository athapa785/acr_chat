import sys
from PyQt5.QtWidgets import QApplication
from .view.ui import MainWindow
from .utils import load_env_vars

def main():
    # Load environment variables
    load_env_vars()
    
    # Create and run application
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Only proceed if login was successful (window is not closed)
    if window.isVisible():
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main() 