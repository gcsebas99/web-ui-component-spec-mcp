"""
tools/get_component_tests.py

Returns only the Test Scenarios for one or more components.
Separated from get_component_spec to minimize context cost when
the task is writing or reviewing tests rather than implementing.
"""

from data.store import store


def get_component_tests(components: list[str | int] | str | int) -> dict:
    """
    Return test scenarios for one or more components.

    Args:
        components: A single component name/id, or a list of them.
                    e.g. "Modal", ["Button", "Text Input"], [16, 19, 46]

    Returns:
        {
            "results": [
                {
                    "id": int,
                    "name": str,
                    "test_scenarios": [ str, ... ],
                    "test_count": int
                },
                ...
            ],
            "not_found": [ str, ... ]   # names/ids that couldn't be resolved
        }
    """
    # Normalize to list
    if not isinstance(components, list):
        components = [components]

    results = []
    not_found = []

    for ref in components:
        comp = store.resolve_component(ref)
        if comp is None:
            not_found.append(str(ref))
            continue

        scenarios = comp.get("test_scenarios", [])
        results.append({
            "id": comp["id"],
            "name": comp["name"],
            "test_scenarios": scenarios,
            "test_count": len(scenarios),
        })

    return {
        "results": results,
        "not_found": not_found,
    }
