"""
tools/get_related_components.py

Returns dependency and relationship information for a component.
Surfaces what a component needs, what needs it, and what it's
commonly confused with — so models don't have to infer these.
"""

from data.store import store


# Manually curated relationship map
# Format: component_id → { depends_on, used_by, alternatives, notes }
_RELATIONSHIPS: dict[int, dict] = {
    16: {  # Button
        "depends_on": [1],  # Icon
        "used_by": [18, 32, 37, 46, 47, 55],
        "alternatives": [],
        "notes": "Button is the most composed-from component in the system. Build it before any compound component.",
    },
    17: {  # Label
        "depends_on": [],
        "used_by": [18, 23, 24, 25],
        "alternatives": [],
        "notes": "Label should be built immediately before Form Field — they are always used together.",
    },
    18: {  # Form Field
        "depends_on": [16, 17],
        "used_by": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 40, 41, 49, 50, 51],
        "alternatives": [],
        "notes": "Form Field is the wrapper that gives every input its label, error message, and help text. Build this before any input component.",
    },
    19: {  # Text Input
        "depends_on": [17, 18],
        "used_by": [20, 21, 40, 41],
        "alternatives": [22],  # Textarea for multiline
        "notes": "Text Input specializations (Email, Number, Search) inherit from this base. Build the base first.",
    },
    40: {  # Select
        "depends_on": [1, 16, 17, 18],
        "used_by": [],
        "alternatives": [41],  # Combobox when search is needed
        "notes": "Use Select for fixed option lists. Use Combobox/Autocomplete (41) when users need to search or filter options.",
    },
    41: {  # Combobox
        "depends_on": [1, 16, 17, 18, 19],
        "used_by": [],
        "alternatives": [40],
        "notes": "Combobox composes Text Input internally. Build Text Input (19) first.",
    },
    42: {  # Dropdown Menu
        "depends_on": [1, 16],
        "used_by": [48],
        "alternatives": [44],  # Popover for non-menu content
        "notes": "Dropdown Menu is for action/navigation lists. Use Popover (44) for arbitrary floating content.",
    },
    43: {  # Tooltip
        "depends_on": [],
        "used_by": [],
        "alternatives": [44],  # Popover for richer content
        "notes": "Tooltip is for short, non-interactive labels only. If content needs to be clicked or contains links, use Popover (44).",
    },
    44: {  # Popover
        "depends_on": [16],
        "used_by": [],
        "alternatives": [42, 43, 46],
        "notes": "Popover sits between Tooltip (simple, no interaction) and Modal (full blocking overlay). Use for rich non-blocking content.",
    },
    46: {  # Modal
        "depends_on": [1, 16],
        "used_by": [],
        "alternatives": [47, 44],  # Drawer for side panels, Popover for non-blocking
        "notes": "Modal blocks all interaction — use only when user must respond before continuing. For side panels use Drawer (47).",
    },
    47: {  # Drawer
        "depends_on": [1, 16],
        "used_by": [48],
        "alternatives": [46],
        "notes": "Drawer slides in from an edge. Side Drawer for desktop navigation panels; Bottom Drawer for mobile action sheets.",
    },
    48: {  # Adaptive Menu
        "depends_on": [42, 47],
        "used_by": [],
        "alternatives": [],
        "notes": "Adaptive Menu composes Dropdown Menu (42) for desktop and Drawer (47) for mobile. Build both before building this.",
    },
    49: {  # Date Picker
        "depends_on": [1, 16, 17, 18, 19],
        "used_by": [51],
        "alternatives": [52],  # Calendar for display-only
        "notes": "Date Picker is an input component. Calendar (52) is a display component. Do not confuse them.",
    },
    51: {  # DateTime Picker
        "depends_on": [49, 50],
        "used_by": [],
        "alternatives": [],
        "notes": "DateTime Picker composes Date Picker (49) and Time Picker (50). Build both first.",
    },
    53: {  # Tabs
        "depends_on": [],
        "used_by": [],
        "alternatives": [26, 55],  # Segmented Control for small option sets, Stepper for sequential flows
        "notes": "Use Tabs for parallel content panels. Use Segmented Control (26) for 2-4 options that toggle a view. Use Stepper (55) for sequential multi-step flows.",
    },
    54: {  # Accordion
        "depends_on": [35],  # Collapsible
        "used_by": [],
        "alternatives": [53],
        "notes": "Accordion is built on the Collapsible (35) primitive. Collapsible handles single-item expand/collapse; Accordion manages a group.",
    },
    57: {  # Table
        "depends_on": [1, 16, 23, 33, 37, 56],
        "used_by": [],
        "alternatives": [],
        "notes": "Table is the most complex component in the system. Build all its dependencies — especially Checkbox (23), Progress (33), and Pagination (56) — before starting.",
    },
    63: {  # Navbar
        "depends_on": [1, 15, 16, 42, 47],
        "used_by": [],
        "alternatives": [64, 65],
        "notes": "Navbar is for page-level horizontal navigation. Sidebar (64) for vertical app navigation. Dock (65) for mobile bottom navigation.",
    },
    64: {  # Sidebar
        "depends_on": [1, 15, 16],
        "used_by": [],
        "alternatives": [63, 65],
        "notes": "Sidebar collapses to an icon rail on narrow viewports. Every icon must have an aria-label in collapsed state — not just a tooltip.",
    },
    65: {  # Dock
        "depends_on": [1, 10],
        "used_by": [],
        "alternatives": [63, 64, 53],
        "notes": "Dock is mobile-only bottom navigation. Hard constraint: 3–5 items maximum. Use Navbar (63) or Sidebar (64) on desktop.",
    },
}


def get_related_components(component: str | int) -> dict:
    """
    Return dependency and relationship information for a component.

    Args:
        component: Component name or id.

    Returns:
        {
            "component": {id, name},
            "depends_on": [ {id, name, summary}, ... ],
            "used_by": [ {id, name, summary}, ... ],
            "alternatives": [ {id, name, summary, when_to_use_instead}, ... ],
            "notes": str
        }
    """
    comp = store.resolve_component(component)
    if comp is None:
        return {
            "error": f"Component '{component}' not found.",
            "hint": "Call list_components() to see all available component names.",
        }

    cid = comp["id"]
    rel = _RELATIONSHIPS.get(cid, {})

    def _resolve_list(ids: list[int]) -> list[dict]:
        results = []
        for i in ids:
            c = store.resolve_component(i)
            if c:
                results.append({
                    "id": c["id"],
                    "name": c["name"],
                    "summary": c.get("summary", ""),
                })
        return results

    return {
        "component": {"id": comp["id"], "name": comp["name"]},
        "depends_on": _resolve_list(rel.get("depends_on", [])),
        "used_by": _resolve_list(rel.get("used_by", [])),
        "alternatives": _resolve_list(rel.get("alternatives", [])),
        "notes": rel.get("notes", "No specific relationship notes for this component."),
    }
