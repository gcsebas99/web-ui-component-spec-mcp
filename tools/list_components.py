"""
tools/list_components.py

Returns the full component index, optionally filtered by category or tier.
Always the first call in any session — establishes what exists.
"""

from data.store import store


def list_components(category: str = "", tier: str = "") -> dict:
    """
    List all components in the spec, with optional filtering.

    Args:
        category: Filter by functional category (partial match, case-insensitive).
                  Options: "Content & Typography", "Layout & Structure",
                  "Identity & Status Indicators", "Actions & Navigation Primitives",
                  "Form Inputs & Controls", "Feedback & Communication",
                  "Overlays & Floating Elements", "Adaptive Elements",
                  "Navigation & Wayfinding", "Data Display & Visualization"
        tier:     Filter by complexity tier (case-insensitive).
                  Options: "Basic", "Intermediate", "Advanced"

    Returns:
        {
            "total": int,
            "filters_applied": {...},
            "components": [ {id, name, category, tier, summary, specializations}, ... ]
        }
    """
    index = store.catalog.get("index", [])

    filtered = index

    if category:
        cat_lower = category.lower()
        filtered = [c for c in filtered if cat_lower in c.get("category", "").lower()]

    if tier:
        tier_lower = tier.lower()
        filtered = [c for c in filtered if tier_lower in c.get("tier", "").lower()]

    return {
        "total": len(filtered),
        "filters_applied": {
            "category": category or None,
            "tier": tier or None,
        },
        "components": filtered,
    }
