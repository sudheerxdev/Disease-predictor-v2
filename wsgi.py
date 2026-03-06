"""
WSGI entry point for production servers (Gunicorn, uWSGI, etc.)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Flask environment
os.environ.setdefault("FLASK_ENV", os.getenv("FLASK_ENV", "production"))

from backend import create_app
from config import get_config

# Create the Flask app
app = create_app()

# Apply production configuration
config = get_config()
app.config.from_object(config)
config.init_app(app)

if __name__ == "__main__":
    app.run()
