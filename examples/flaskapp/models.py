"""Database models for users and blog posts."""
from extensions import db


class User(db.Model):
    """A registered user who can author posts."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(255))

    def check_password(self, password):
        """Return True if the given password matches this user's hash."""
        return self.password_hash == password


class Post(db.Model):
    """A blog post authored by a user."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def summary(self):
        """Return a short preview of the post body."""
        return (self.body or "")[:140]
