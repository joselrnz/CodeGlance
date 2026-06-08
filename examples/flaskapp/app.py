"""Application factory: wires config, extensions, and blueprints together."""
from flask import Flask

from config import Config
from extensions import db
from blueprints.auth import auth_bp
from blueprints.blog import blog_bp

DEFAULT_PORT = 5000


def create_app(config_class=Config):
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    return app


if __name__ == "__main__":
    create_app().run(port=DEFAULT_PORT, debug=True)
