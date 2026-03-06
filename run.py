"""
Application entry point for development
For production, use: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""

from backend import create_app
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == "__main__":
    # Development server configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_ENV", "development") == "development"

    print("\n" + "=" * 60)
    print(
        f"Starting Disease Predictor - {os.getenv('FLASK_ENV', 'development').upper()}"
    )
    print("=" * 60)
    print(f"Server: http://{host}:{port}")
    print("=" * 60 + "\n")

    app.run(debug=debug, host=host, port=port, use_reloader=debug)
