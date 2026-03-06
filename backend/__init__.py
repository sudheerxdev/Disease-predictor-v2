from flask import Flask, render_template
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour"])

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    from backend.models.user import User

    return User.query.get(int(user_id))


from datetime import datetime, timezone


def create_app(config_name=None):
    """Factory function to create Flask application"""
    # Get the backend directory (where this __init__.py file is)
    backend_root = os.path.dirname(os.path.abspath(__file__))

    # Initialize Flask app with correct paths
    app = Flask(
        __name__,
        static_folder=os.path.join(backend_root, "static"),
        template_folder=os.path.join(backend_root, "templates"),
    )

    # Load configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    try:
        from config import config

        app.config.from_object(config.get(config_name, config["development"]))
    except ImportError:
        # Fallback if config.py doesn't exist
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "DATABASE_URL", "sqlite:///" + os.path.join(backend_root, "site.db")
        )
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Setup logging
    setup_logging(app)

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Enable CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("CORS_ORIGINS", ["http://localhost:3000"]),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    register_blueprints(app)

    # Register context processors
    @app.context_processor
    def inject_current_year():
        return {"current_year": datetime.now(timezone.utc).year}

    # Health check endpoint
    @app.route("/health")
    def health_check():
        from datetime import timezone as tz

        return {"status": "healthy", "timestamp": datetime.now(tz.utc).isoformat()}, 200

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


def setup_logging(app):
    """Configure logging for the application"""
    if not app.debug and not app.testing:
        # File logging for production
        if not os.path.exists("logs"):
            os.mkdir("logs")

        from logging.handlers import RotatingFileHandler

        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )

        # Application logger
        file_handler = RotatingFileHandler(
            "logs/disease_predictor.log", maxBytes=10485760, backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Disease Predictor startup")


def register_error_handlers(app):
    """Register error handlers for common exceptions"""

    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad Request", "message": str(error), "status": 400}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {
            "error": "Unauthorized",
            "message": "Authentication required",
            "status": 401,
        }, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {
            "error": "Forbidden",
            "message": "You do not have permission to access this resource",
            "status": 403,
        }, 403

    @app.errorhandler(404)
    def not_found(error):
        return {
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status": 404,
        }, 404

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return {
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please try again later.",
            "status": 429,
        }, 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal Server Error: {error}")
        return {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status": 500,
        }, 500

    @app.errorhandler(503)
    def service_unavailable(error):
        return {
            "error": "Service Unavailable",
            "message": "Service is temporarily unavailable",
            "status": 503,
        }, 503


def register_blueprints(app):
    """Register all route blueprints"""
    from backend.routes.disease_routes import disease_bp

    app.register_blueprint(disease_bp)
    app.logger.info("'disease_routes' blueprint registered")

    # Register ML Routes Blueprint
    try:
        from backend.routes.ml_routes import ml_bp

        app.register_blueprint(ml_bp)
        app.logger.info("'ml_routes' blueprint registered")
    except ImportError as e:
        app.logger.warning(f"Could not import 'ml_routes': {e}")

    # Register Auth Routes Blueprint
    from backend.routes.auth_routes import auth_bp

    app.register_blueprint(auth_bp)
    app.logger.info("'auth_routes' blueprint registered")

    # Register Doctor Dashboard Routes Blueprint
    try:
        from backend.routes.doctor_routes import doctor_bp

        app.register_blueprint(doctor_bp)
        app.logger.info("'doctor_routes' blueprint registered")
    except ImportError as e:
        app.logger.warning(f"Could not import 'doctor_routes': {e}")

    # Register other blueprints
    try:
        from backend.routes.history_routes import history_bp

        app.register_blueprint(history_bp)
        app.logger.info("'history_routes' blueprint registered")
    except ImportError as e:
        app.logger.debug(f"Could not import 'history_routes': {e}")

    try:
        from backend.routes.predict_disease_type_routes import predict_disease_type_bp

        app.register_blueprint(predict_disease_type_bp)
        app.logger.info("'predict_disease_type_bp_routes' blueprint registered")
    except ImportError as e:
        app.logger.debug(f"Could not import 'predict_disease_type_bp_routes': {e}")

    try:
        from backend.routes.general_routes import general_bp

        app.register_blueprint(general_bp)
        app.logger.info("'general_routes' blueprint registered")
    except ImportError as e:
        app.logger.debug(f"Could not import 'general_routes': {e}")

    try:
        from backend.routes.scalability_routes import scalability_bp

        app.register_blueprint(scalability_bp)
        app.logger.info("'scalability_routes' blueprint registered")
    except ImportError as e:
        app.logger.debug(f"Could not import 'scalability_routes': {e}")

    try:
        from backend.routes.chat_routes import chat_bp

        app.register_blueprint(chat_bp)
        app.logger.info("'chat_routes' blueprint registered")
    except ImportError as e:
        app.logger.debug(f"Could not import 'chat_routes': {e}")
