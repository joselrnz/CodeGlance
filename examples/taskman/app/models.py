"""Domain models for the task manager."""


class Task:
    """A single to-do item."""

    def __init__(self, title: str):
        self.title = title
        self.done = False

    def complete(self) -> None:
        self.done = True


class User:
    """An account that owns tasks."""

    def __init__(self, name: str):
        self.name = name
