import os
from pathlib import Path
from dotenv import load_dotenv

def load_env_vars():
    """Load environment variables from .env file."""
    # Get the project root directory (where .env should be)
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    
    # Load environment variables from .env file
    load_dotenv(env_path)
    
def get_admin_passcode() -> str:
    """Get the admin passcode from environment variables.
    
    Returns:
        str: The admin passcode or a default if not set
    """
    return os.getenv('ADMIN_PASSCODE', 'admin123')  # Fallback to a default if not set 