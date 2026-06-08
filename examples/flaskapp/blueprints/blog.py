"""Blog routes: list posts and view a single post."""
from flask import Blueprint, render_template

from models import Post

blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/")
def index():
    """Render the list of recent posts."""
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("index.html", posts=posts)


@blog_bp.route("/post/<int:post_id>")
def view_post(post_id):
    """Render a single post by its id."""
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)
