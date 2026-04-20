"""
tools/get_component_summary.py

Returns a lightweight summary for one or more components —
description and main features only.
Useful for planning and surveying before deep implementation work.
"""

from data.store import store


def get_component_summary(components: list[str | int] | str | int) -> dict:
    """
    Return a condensed summary for one or more components.
    Includes description and main features only — no secondary features,
    no test scenarios, no notes.

    Args:
        components: A single component name/id, or a list of them.

    Returns:
        {
            "results": [
                {
                    "id": int,
                    "name": str,
                    "category": str,
                    "tier": str,
                    "summary": str,
                    "specializations": [str, ...],
                    "description": str,
                    "main_features": [str, ...]
                },
                ...
            ],
            "not_found": [str, ...]
        }
    """
    if not isinstance(components, list):
        components = [components]

    results = []
    not_found = []

    for ref in components:
        comp = store.resolve_component(ref)
        if comp is None:
            not_found.append(str(ref))
            continue

        results.append({
            "id": comp["id"],
            "name": comp["name"],
            "category": comp.get("category", ""),
            "tier": comp.get("tier", ""),
            "summary": comp.get("summary", ""),
            "specializations": comp.get("specializations", []),
            "description": comp.get("description", ""),
            "main_features": comp.get("main_features", []),
        })

    return {
        "results": results,
        "not_found": not_found,
    }
