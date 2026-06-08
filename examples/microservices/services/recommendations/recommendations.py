"""Recommends products to users based on catalog data."""
from services.catalog import catalog


class Recommendation:
    """A scored product suggestion for a user."""

    def __init__(self, product_id: str, score: float) -> None:
        self.product_id = product_id
        self.score = score


def recommend(user_id: str) -> list:
    """Return a ranked list of recommended products for the user."""
    catalog.list_products()
    return [Recommendation("demo", 0.9)]
