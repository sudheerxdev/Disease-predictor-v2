"""
Flask Configuration for different environments
Supports: development, testing, production
"""

import os
from datetime import timedelta


class Config:
    """Base configuration for all environments"""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False
    ENV = "production"

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # API Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100/hour"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

    # AI/Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_TIMEOUT = 30

    # File Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    @staticmethod
    def init_app(app):
        """Initialize app-specific settings"""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration"""

    DEBUG = True
    TESTING = False
    ENV = "development"
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = "DEBUG"

    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///site.db")


class TestingConfig(Config):
    """Testing environment configuration"""

    TESTING = True
    DEBUG = True
    ENV = "testing"
    SESSION_COOKIE_SECURE = False

    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False
    ENV = "production"

    # Enforce secure settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Database - use environment variable if set
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost/disease_db"
    )

    # Secret key from environment
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # Logging to file in production
    LOG_LEVEL = "WARNING"

    @staticmethod
    def init_app(app):
        """Production-specific initialization"""
        import logging
        from logging.handlers import RotatingFileHandler

        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # Set up file logging
        file_handler = RotatingFileHandler(
            "logs/disease_predictor.log", maxBytes=10485760, backupCount=10  # 10MB
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.WARNING)
        app.logger.info("Disease Predictor startup in production environment")


# Configuration dictionary for easy access
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
