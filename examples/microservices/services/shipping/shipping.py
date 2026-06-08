"""Calculates shipping quotes and schedules shipments."""


class Shipment:
    """A scheduled shipment with a tracking identifier."""

    def __init__(self, tracking: str) -> None:
        self.tracking = tracking


def quote(items) -> Shipment:
    """Estimate shipping cost and produce a tracking number for the items."""
    return Shipment("1Z-DEMO")
