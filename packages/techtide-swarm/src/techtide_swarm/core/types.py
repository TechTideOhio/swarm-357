"""Layer and shared enums."""

from __future__ import annotations

from enum import Enum


class LayerType(str, Enum):
    """Business layer for an agent."""

    SALES = "sales"
    SUPPORT = "support"
    MARKETING = "marketing"
    SEO = "seo"
    RESEARCH = "research"
    OPERATIONS = "operations"
    MANAGEMENT = "management"
