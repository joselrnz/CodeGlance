"""Application entry point: wires the task-manager API together and starts it."""

from app.config import load_config
from app.db import Database
from app.routes import Router


def main() -> None:
    config = load_config()
    db = Database(config.db_path)
    router = Router(db)
    router.serve()


if __name__ == "__main__":
    main()
