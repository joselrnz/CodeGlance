"""Authentication routes: login and register."""
from flask import Blueprint, request, redirect

from models import User
from extensions import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user from posted credentials."""
    user = User.query.filter_by(username=request.form["username"]).first()
    if user and user.check_password(request.form["password"]):
        return redirect("/")
    return "Invalid credentials", 401


@auth_bp.route("/register", methods=["POST"])
def register():
    """Create a new user account and redirect to login."""
    user = User(username=request.form["username"])
    db.session.add(user)
    db.session.commit()
    return redirect("/auth/login")
