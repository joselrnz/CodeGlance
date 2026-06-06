"""A tiny in-memory database."""

from app.models import Task, User


class Database:
    """Stores tasks and users in memory."""

    def __init__(self, path: str):
        self.path = path
        self._tasks: list[Task] = []
        self._users: list[User] = []

    def save(self, task: Task) -> None:
        self._tasks.append(task)

    def save_user(self, user: User) -> None:
        self._users.append(user)

    def all_tasks(self) -> list[Task]:
        return list(self._tasks)
