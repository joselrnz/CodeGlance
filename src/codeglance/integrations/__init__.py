"""Agent and editor integration install planning for Codeglance."""

from .install import apply_install_plan, create_install_plan, validate_installation
from .models import (
    FileAction,
    GuidanceFile,
    InstallConflictError,
    InstallPlan,
    Platform,
    ValidationFinding,
    ValidationReport,
)
from .registry import DEFAULT_PLATFORM_IDS, default_platforms, get_platform, list_platforms, parse_platforms

__all__ = [
    "DEFAULT_PLATFORM_IDS",
    "FileAction",
    "GuidanceFile",
    "InstallConflictError",
    "InstallPlan",
    "Platform",
    "ValidationFinding",
    "ValidationReport",
    "apply_install_plan",
    "create_install_plan",
    "default_platforms",
    "get_platform",
    "list_platforms",
    "parse_platforms",
    "validate_installation",
]
