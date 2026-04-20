"""
tools/get_components_by_scenario.py

Given a project type or use case, returns a curated component list
with recommended build order. Encodes the judgment of "what to build
for this kind of project" so models don't have to derive it each time.
"""

from data.store import store


# Curated scenario → component id lists
# Components ordered by recommended build sequence (tier-aware)
_SCENARIOS: dict[str, dict] = {
    "saas_dashboard": {
        "label": "SaaS Dashboard / Admin Panel",
        "description": "Data-dense application with tables, forms, and navigation.",
        "component_ids": [
            1, 2, 5, 9, 10, 15, 16,        # Tier 1 foundations
            17, 18, 19, 22, 23, 24, 25,     # Form inputs
            31, 32, 33, 34, 37,             # Layout and feedback
            38, 39,                          # Navigation primitives
            40, 42, 43, 45, 46,             # Overlays
            53, 55, 56, 57, 63, 64,         # Nav and data
        ],
        "notes": "Prioritize Table (57), Form Field (18), and Modal (46) — these are the highest-use components in admin interfaces.",
    },
    "ecommerce": {
        "label": "E-commerce / Shopping",
        "description": "Product browsing, cart, checkout flows.",
        "component_ids": [
            1, 2, 8, 10, 11, 15, 16,        # Foundations + product display
            17, 18, 19, 20, 23, 24, 25,     # Checkout form layer
            27, 28, 31, 32, 33, 37,         # Product controls + feedback
            38, 43, 44, 45, 46,             # Overlays and tooltips
            53, 56, 60, 63,                  # Navigation and carousel
        ],
        "notes": "Rating (28), Carousel (60), and Badge (10) are especially important for product display. Stepper (55) is useful for multi-step checkout.",
    },
    "forms_heavy": {
        "label": "Forms-Heavy Application",
        "description": "Data entry, multi-step forms, validation-intensive flows.",
        "component_ids": [
            1, 2, 15, 16,                   # Foundations
            17, 18, 19, 20, 21, 22,         # All text inputs
            23, 24, 25, 26, 27, 29, 30,     # All selection controls
            31, 32, 37,                      # Layout and feedback
            40, 41, 46, 49, 50, 51,         # Advanced inputs + modal
            55,                              # Stepper for multi-step forms
        ],
        "notes": "Form Field (18) is the most critical component here — build it well before any other form input. DateTime Picker (51) composes Date (49) and Time (50) Pickers.",
    },
    "content_site": {
        "label": "Content / Marketing Site",
        "description": "Editorial content, landing pages, minimal interactivity.",
        "component_ids": [
            1, 2, 3, 4, 5, 6, 7, 8,        # All content and layout basics
            9, 10, 11, 15, 16,              # Identity and actions
            31, 32, 37,                      # Cards and feedback
            38, 43, 44, 53, 54, 62, 63,     # Navigation, accordion, timeline
        ],
        "notes": "Typography (2), Image (8), and Card (31) are your workhorses. Accordion (54) is useful for FAQs. Timeline (62) for history/roadmap sections.",
    },
    "mobile_web": {
        "label": "Mobile-First Web Application",
        "description": "Responsive or mobile-only app with touch-optimized interactions.",
        "component_ids": [
            1, 2, 9, 10, 11, 15, 16,        # Foundations
            17, 18, 19, 22, 23, 24, 25,     # Form layer
            31, 32, 33, 37,                  # Layout and feedback
            45, 46, 47, 48,                  # Overlays — Drawer especially important
            53, 60, 63, 65,                  # Navigation: Tabs, Carousel, Dock
        ],
        "notes": "Drawer (47) and Dock (65) are mobile-critical. Adaptive Menu (48) handles the desktop/mobile navigation switch. Ensure all components meet 44×44px touch target minimums.",
    },
    "minimal": {
        "label": "Minimal / Starter Library",
        "description": "The smallest useful component set to get a project running.",
        "component_ids": [
            1, 2, 5, 9, 10, 15, 16,         # Tier 1 essentials
            17, 18, 19, 22, 23, 24, 25,     # Core form inputs
            31, 32, 37, 43, 45, 46,         # Feedback and overlays
        ],
        "notes": "Build all Tier 1 components before starting Tier 2. This set covers ~80% of everyday UI needs.",
    },
}

# Aliases for fuzzy matching
_ALIASES: dict[str, str] = {
    "dashboard": "saas_dashboard",
    "admin": "saas_dashboard",
    "saas": "saas_dashboard",
    "shop": "ecommerce",
    "shopping": "ecommerce",
    "store": "ecommerce",
    "checkout": "ecommerce",
    "form": "forms_heavy",
    "forms": "forms_heavy",
    "data entry": "forms_heavy",
    "content": "content_site",
    "marketing": "content_site",
    "landing": "content_site",
    "blog": "content_site",
    "mobile": "mobile_web",
    "app": "mobile_web",
    "starter": "minimal",
    "basic": "minimal",
    "minimum": "minimal",
}


def get_components_by_scenario(scenario: str) -> dict:
    """
    Return a curated component list and build order for a given project scenario.

    Args:
        scenario: Project type description.
                  e.g. "SaaS dashboard", "e-commerce", "forms-heavy app", "mobile"
                  Use list_scenarios=True to see all available options.

    Returns:
        {
            "scenario": str,
            "description": str,
            "notes": str,
            "component_count": int,
            "components": [ {id, name, category, tier, summary}, ... ],
            "build_order": [ {tier, components: [{id, name}]} ]
        }
    """
    # List all scenarios if requested
    if scenario.lower() in ("list", "help", "options", "?"):
        return {
            "available_scenarios": [
                {"key": k, "label": v["label"], "description": v["description"]}
                for k, v in _SCENARIOS.items()
            ]
        }

    # Resolve scenario key
    norm = scenario.lower().strip()
    key = _ALIASES.get(norm) or norm.replace(" ", "_").replace("-", "_")

    if key not in _SCENARIOS:
        # Try partial match
        for k in _SCENARIOS:
            if norm in k or k in norm:
                key = k
                break
        else:
            return {
                "error": f"Scenario '{scenario}' not recognized.",
                "available_scenarios": list(_SCENARIOS.keys()),
                "hint": "Pass 'list' as scenario to see all options with descriptions.",
            }

    scenario_data = _SCENARIOS[key]
    component_ids = scenario_data["component_ids"]

    # Resolve component details
    components = []
    for cid in component_ids:
        comp = store.resolve_component(cid)
        if comp:
            components.append({
                "id": comp["id"],
                "name": comp["name"],
                "category": comp.get("category", ""),
                "tier": comp.get("tier", ""),
                "summary": comp.get("summary", ""),
            })

    # Group into build order by tier
    tier_order = ["Basic", "Intermediate", "Advanced"]
    build_order = []
    for tier in tier_order:
        tier_components = [c for c in components if c["tier"] == tier]
        if tier_components:
            build_order.append({
                "tier": tier,
                "build_first": tier == "Basic",
                "components": [{"id": c["id"], "name": c["name"]} for c in tier_components],
            })

    return {
        "scenario": scenario_data["label"],
        "description": scenario_data["description"],
        "notes": scenario_data["notes"],
        "component_count": len(components),
        "components": components,
        "build_order": build_order,
    }
