"""
tools/get_core_principles.py
"""

from data.store import store
from parsers.parse_principles import SECTION_KEYS


def get_core_principles(section: str = "all") -> dict:
    """
    Return Core Principles content. Fetch only what you need.

    Args:
        section: One of:
                 "philosophy"             — Component Philosophy
                 "design_tokens"          — Design Tokens
                 "interaction_principles" — Interaction Principles
                 "consistency_patterns"   — Consistency Patterns
                 "all"                    — Full document (use sparingly)

    Returns:
        { "section": str, "title": str, "content": str }
    """
    norm = section.lower().strip()

    if norm == "all":
        return {
            "section": "all",
            "title": "Core Principles",
            "content": store.principles.get("all", ""),
        }

    if norm not in SECTION_KEYS:
        return {
            "error": f"Section '{section}' not found.",
            "available_sections": list(SECTION_KEYS.keys()) + ["all"],
        }

    content = store.principles.get(norm, "")
    return {
        "section": norm,
        "title": SECTION_KEYS[norm],
        "content": content,
    }
