"""Configuration loading."""

from dataclasses import dataclass


@dataclass
class Config:
    db_path: str


def load_config() -> Config:
    return Config(db_path=":memory:")
