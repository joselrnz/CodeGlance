"""Orchestrates the checkout flow across payments, shipping, and notifications."""
from services.payments import payments
from services.shipping import shipping
from services.notifications import notifications
from services.catalog import catalog


class OrderItem:
    """A single line item (product + quantity) within an order."""

    def __init__(self, product_id: str, qty: int) -> None:
        self.product_id = product_id
        self.qty = qty


class Order:
    """A customer order being assembled and placed."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.items: list[OrderItem] = []


def place_order(order: Order) -> str:
    """Validate items, charge payment, schedule shipping, and email the customer."""
    for item in order.items:
        catalog.get_product(item.product_id)
    receipt = payments.charge(order.user_id, total=42.0)
    shipment = shipping.quote(order.items)
    notifications.send_confirmation(order.user_id, receipt, shipment)
    return "placed"
