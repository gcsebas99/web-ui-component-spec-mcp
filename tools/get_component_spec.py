"""
tools/get_component_spec.py

Returns the full specification for a single component.
"""

from data.store import store


def get_component_spec(component: str | int) -> dict:
    """
    Return the full behavioral specification for one component.

    Args:
        component: Component name (e.g. "Modal", "Text Input", "Button")
                   or component id (e.g. 46, 19, 16).

    Returns:
        Full component spec dict, or an error dict if not found.
    """
    comp = store.resolve_component(component)

    if comp is None:
        return {
            "error": f"Component '{component}' not found.",
            "hint": "Call list_components() to see all available component names.",
        }

    return {
        "id": comp["id"],
        "name": comp["name"],
        "category": comp.get("category", ""),
        "tier": comp.get("tier", ""),
        "summary": comp.get("summary", ""),
        "specializations": comp.get("specializations", []),
        "description": comp.get("description", ""),
        "main_features": comp.get("main_features", []),
        "secondary_features": comp.get("secondary_features", {}),
        "notes": comp.get("notes", []),
    }
