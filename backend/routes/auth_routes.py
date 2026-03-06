from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
from backend import db, bcrypt
from backend.models.user import User
from flask import session
import os
from authlib.integrations.flask_client import OAuth

# Initialize OAuth
oauth = OAuth()

auth_bp = Blueprint("auth", __name__)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@auth_bp.route("/auth", methods=["GET"])
def auth():
    # Deprecated: Redirect to login or profile
    if current_user.is_authenticated:
        return redirect(url_for("auth.profile"))
    return redirect(url_for("auth.login", tab=request.args.get("tab", "signin")))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            next_page = request.args.get("next")
            if not next_page or not is_safe_url(next_page):
                next_page = url_for("auth.profile")
            return redirect(next_page)
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login", tab="signin"))  # Keep on login page

    # GET request: render auth template
    active_tab = request.args.get("tab", "signin")
    return render_template("auth.html", active_tab=active_tab)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # 1. Reject empty fields
    if not username or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for("auth.login", tab="register"))

    # 2. Check for existing user (split for better internal logging if needed, but flash user-friendly)
    if User.query.filter_by(email=email).first():
        flash("Email already registered.", "danger")
        return redirect(url_for("auth.login", tab="register"))

    if User.query.filter_by(username=username).first():
        flash("Username already taken.", "danger")
        return redirect(url_for("auth.login", tab="register"))

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash("Account Created Successfully. Please Sign In.", "success")
    # Redirect to signin tab after successful registration
    return redirect(url_for("auth.login", tab="signin"))


@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@auth_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    # handle form update logic here
    return redirect(url_for("auth.profile"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ========== GOOGLE OAUTH ROUTES ==========


@auth_bp.route("/auth/google")
def google_login():
    """Initiate Google OAuth flow"""
    # Register Google OAuth if not already done
    if "google" not in oauth._clients:
        oauth.register(
            "google",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid profile email"},
        )

    google = oauth.create_client("google")
    redirect_uri = url_for("auth.google_callback", _external=True)

    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/auth/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Register client if needed
        if "google" not in oauth._clients:
            oauth.register(
                "google",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={"scope": "openid profile email"},
            )

        google = oauth.create_client("google")
        token = google.authorize_access_token()

        # Get user info from Google
        user_info = token.get("userinfo")

        if not user_info:
            flash("Failed to get user information from Google", "danger")
            return redirect(url_for("auth.login"))

        google_id = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name")

        # Find or create user
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            # Check if email exists
            user = User.query.filter_by(email=email).first()

            if user:
                # Link Google account to existing user
                user.google_id = google_id
                user.auth_provider = "google"
            else:
                # Create new user
                username = (
                    name.replace(" ", "_").lower() if name else email.split("@")[0]
                )

                # Ensure username is unique
                counter = 1
                original_username = username
                while User.query.filter_by(username=username).first():
                    username = f"{original_username}{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=email,
                    google_id=google_id,
                    auth_provider="google",
                )
                db.session.add(user)

        db.session.commit()

        # Log in the user
        login_user(user)
        flash(f"Successfully logged in with Google as {email}!", "success")

        next_page = request.args.get("next")
        if not next_page or not is_safe_url(next_page):
            next_page = url_for("auth.profile")

        return redirect(next_page)

    except Exception as e:
        flash(f"Error during Google login: {str(e)}", "danger")
        return redirect(url_for("auth.login"))
