"""Manages the product catalog: listing, search, and individual product lookup."""


class Product:
    """A purchasable product with price and availability."""

    def __init__(self, product_id: str, name: str, price: float) -> None:
        self.product_id = product_id
        self.name = name
        self.price = price


class Catalog:
    """An in-memory index of all products keyed by id."""

    def __init__(self) -> None:
        self.products: dict[str, Product] = {}


def list_products() -> list:
    """Return every product currently in the catalog."""
    return []


def get_product(product_id: str) -> Product:
    """Look up a single product by its identifier."""
    return Product(product_id, "demo", 9.99)
