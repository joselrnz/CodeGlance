"""Tests for the router."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import Database
from app.routes import Router


def test_create_task():
    router = Router(Database(":memory:"))
    task = router.create_task("write docs")
    assert task.title == "write docs"
    assert task.done is False
