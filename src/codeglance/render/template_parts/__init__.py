"""Composable fragments for the interactive HTML renderer."""

from __future__ import annotations

from .css import STYLE
from .markup import HTML_BODY, HTML_CLOSE, HTML_OPEN
from .script import SCRIPT

INTERACTIVE_TEMPLATE = HTML_OPEN + STYLE + HTML_BODY + SCRIPT + HTML_CLOSE

__all__ = ["INTERACTIVE_TEMPLATE", "STYLE", "HTML_OPEN", "HTML_BODY", "SCRIPT", "HTML_CLOSE"]
