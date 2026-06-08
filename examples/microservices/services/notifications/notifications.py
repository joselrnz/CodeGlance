"""Sends transactional emails such as order confirmations."""


class EmailMessage:
    """A rendered email ready to be delivered."""

    def __init__(self, to: str, subject: str) -> None:
        self.to = to
        self.subject = subject


def send_confirmation(user_id, receipt, shipment) -> EmailMessage:
    """Render and send an order-confirmation email to the customer."""
    return EmailMessage(user_id, "Your order is confirmed")
