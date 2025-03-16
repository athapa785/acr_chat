# ACR Chat Application

A real-time chat application built with Python and PyQt5, supporting multiple instances and file sharing.

## Features

- **Real-time Multi-instance Chat**: Multiple users can chat simultaneously with automatic synchronization
- **File Sharing**: Share files between users with easy access to shared files
- **User Management**: Track online users and their status
- **Admin Controls**: Secure admin functions for user management and chat moderation
- **Chat History**: Persistent chat history with automatic archiving
- **Modern UI**: Clean and intuitive interface built with PyQt5

## Requirements

- Python 3.6+
- PyQt5 >= 5.15.0
- python-dotenv >= 0.19.0

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/acr_chat.git
   cd acr_chat
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your admin passcode:
   ```
   ADMIN_PASSCODE=your_admin_passcode
   ```

## Usage

Run the application:
```bash
python -m acr_chat
```

Multiple instances can be started to simulate different users.

## Admin Features

- Clear online users list
- Archive and clear chat history
- Archive and clear shared files list

Access admin features by clicking the gear icon (⚙) in the top-left corner.

## Data Storage

The application stores its data in the following locations:
- Chat history: `~/.acr_chat/chat_history.json`
- Active users: `~/.acr_chat/active_users.json`
- Shared files: `~/.acr_chat/shared_files.json`
- Archives: `~/.acr_chat/archives/` 