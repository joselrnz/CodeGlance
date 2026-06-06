"""HTTP-style routes for the task manager."""

from app.db import Database
from app.models import Task, User


class Router:
    """Dispatches task operations to the database."""

    def __init__(self, db: Database):
        self.db = db

    def serve(self) -> None:
        print("serving on :8080")

    def list_tasks(self) -> list:
        return self.db.all_tasks()

    def create_task(self, title: str) -> Task:
        task = Task(title)
        self.db.save(task)
        return task

    def add_user(self, name: str) -> User:
        user = User(name)
        self.db.save_user(user)
        return user
