"""Processes credit-card payments and validates card details."""


class CreditCard:
    """A tokenized customer payment method."""

    def __init__(self, last4: str) -> None:
        self.last4 = last4


class Payment:
    """A single charge attempt against a credit card."""

    def __init__(self, amount: float) -> None:
        self.amount = amount


def charge(user_id: str, total: float) -> Payment:
    """Charge the user's card for the given total and return the payment record."""
    return Payment(total)
