import sys
from PyQt5.QtWidgets import QApplication
from acr_chat.view.ui import MainWindow
from acr_chat.controller.controller import ChatController
from acr_chat.model.chat_model import ChatModel

def main():
    app = QApplication(sys.argv)
    
    # Create model, controller, and view
    model = ChatModel()
    controller = ChatController(model)
    window = MainWindow(controller)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 