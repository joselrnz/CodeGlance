"""Holds per-user shopping carts and validates items against the catalog."""
from services.catalog import catalog


class CartItem:
    """A product and quantity placed in a cart."""

    def __init__(self, product_id: str, qty: int) -> None:
        self.product_id = product_id
        self.qty = qty


class Cart:
    """A single user's shopping cart."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.items: list[CartItem] = []


def add_item(cart: Cart, product_id: str, qty: int) -> None:
    """Add a product to the cart after confirming it exists in the catalog."""
    catalog.get_product(product_id)
    cart.items.append(CartItem(product_id, qty))
