"""HTTP API gateway that routes requests to the cart, catalog, and order services."""
from services.orders import orders
from services.cart import cart
from services.catalog import catalog


class ApiGateway:
    """Front door for all client requests; maps routes to downstream services."""

    def __init__(self) -> None:
        self.routes: dict[str, str] = {}


def handle_checkout(user_id: str) -> str:
    """Build an order from the user's cart and place it through the order service."""
    user_cart = cart.Cart(user_id)
    cart.add_item(user_cart, "demo", 1)
    catalog.list_products()
    order = orders.Order(user_id)
    for item in user_cart.items:
        order.items.append(orders.OrderItem(item.product_id, item.qty))
    return orders.place_order(order)
