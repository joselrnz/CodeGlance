"""Configuration objects loaded via app.config.from_object."""
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///blog.db")


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """Production overrides (debugging disabled)."""

    DEBUG = False
