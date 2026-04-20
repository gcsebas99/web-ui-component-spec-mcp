"""
tools/get_step_by_step.py
"""

from data.store import store


def get_step_by_step(steps: list[int] | int | str = "all") -> dict:
    """
    Return one or more steps from the Step-by-Step Build Guide.
    Fetch only the steps relevant to your current phase.

    Args:
        steps: A single step number, a list of step numbers, or "all".
               e.g. 1, [1, 2, 3], "all"

    Available steps:
        1  — Define Your Color Palette
        2  — Define Your Typography System
        3  — Define Spacing and Layout System
        4  — Define Look & Feel Decisions
        5  — Set Up Development Environment
        6  — Implement Design Tokens in Code
        7  — Build Foundational Components
        8  — Build Compound Components
        9  — Ensure Test Coverage and Quality
        10 — Create Documentation and Usage Guidelines
        11 — Gather Feedback and Iterate

    Returns:
        {
            "results": [ {number, title, content}, ... ],
            "not_found": [int, ...]
        }
    """
    all_steps = store.stepbystep.get("steps", {})

    if steps == "all" or steps == ["all"]:
        return {
            "results": list(all_steps.values()),
            "not_found": [],
        }

    if not isinstance(steps, list):
        steps = [steps]

    results = []
    not_found = []

    for s in steps:
        try:
            num = int(s)
        except (ValueError, TypeError):
            not_found.append(str(s))
            continue

        step_data = all_steps.get(num)
        if step_data is None:
            not_found.append(num)
        else:
            results.append(step_data)

    return {
        "results": sorted(results, key=lambda x: x["number"]),
        "not_found": not_found,
        "available_steps": store.stepbystep.get("titles", {}),
    }
