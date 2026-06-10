"""Named colors for the example canvas renderer."""

DEFAULT_PALETTE: dict[str, str] = {
    "ink": "#0b0f14",
    "paper": "#f8fafc",
    "blue": "#5ba4cf",
    "green": "#63c18f",
    "gold": "#e6b450",
    "rose": "#cf7a8a",
}


def resolve_color(name: str, palette: dict[str, str] | None = None) -> str:
    """Return a hex color for a named color or pass through literal hex values."""
    colors = palette or DEFAULT_PALETTE
    if name.startswith("#"):
        return name
    try:
        return colors[name]
    except KeyError as exc:
        available = ", ".join(sorted(colors))
        raise ValueError(f"unknown color '{name}'. Available: {available}") from exc
