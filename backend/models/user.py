from backend import db

# from backend import login_manager # moved to init
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(
        db.String(60), nullable=True
    )  # Nullable for Google OAuth users
    google_id = db.Column(db.String(255), unique=True, nullable=True)  # Google OAuth ID
    auth_provider = db.Column(db.String(20), default="email")  # 'email' or 'google'

    def __repr__(self):
        return (
            f"User('{self.username}', '{self.email}', provider='{self.auth_provider}')"
        )

    @classmethod
    def from_google(cls, google_id, email, name):
        """Create or update user from Google OAuth data"""
        user = cls.query.filter_by(google_id=google_id).first()

        if user:
            # Update existing Google user
            return user

        # Check if email already exists
        user = cls.query.filter_by(email=email).first()
        if user:
            # Link Google account to existing email user
            user.google_id = google_id
            user.auth_provider = "google"
            return user

        # Create new user from Google data
        new_user = cls(
            username=name or email.split("@")[0],
            email=email,
            google_id=google_id,
            auth_provider="google",
        )
        return new_user
