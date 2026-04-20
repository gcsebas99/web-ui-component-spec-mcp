"""
tools/validate_component_checklist.py

Given a component name and a description of what has been implemented,
returns a coverage report against the spec's Main Features and Test Scenarios.

This is the MCP's highest-leverage tool — it actively participates in QA
rather than just serving reference data.
"""

from data.store import store

try:
    from thefuzz import fuzz
    _FUZZY_AVAILABLE = True
except ImportError:
    _FUZZY_AVAILABLE = False


_MATCH_THRESHOLD = 55  # minimum score to consider a feature "covered"


def _coverage_score(implemented_text: str, spec_item: str) -> int:
    """Score how well an implemented description covers a spec requirement."""
    if not implemented_text or not spec_item:
        return 0
    impl_lower = implemented_text.lower()
    spec_lower = spec_item.lower()

    # Direct substring
    if spec_lower in impl_lower or impl_lower in spec_lower:
        return 90

    if _FUZZY_AVAILABLE:
        return max(
            fuzz.partial_ratio(impl_lower, spec_lower),
            fuzz.token_set_ratio(impl_lower, spec_lower),
        )

    # Word overlap fallback
    impl_words = set(impl_lower.split())
    spec_words = set(spec_lower.split())
    overlap = len(impl_words & spec_words)
    if overlap:
        return int(70 * overlap / max(len(spec_words), 1))
    return 0


def _check_coverage(
    spec_items: list[str],
    implemented_features: list[str],
) -> tuple[list[dict], list[str], list[str]]:
    """
    Returns (detailed_results, covered_items, missing_items)
    """
    impl_joined = " ".join(implemented_features)
    detailed = []
    covered = []
    missing = []

    for spec_item in spec_items:
        # Check each implemented feature individually and also the joined string
        best_score = _coverage_score(impl_joined, spec_item)
        best_match = None

        for impl_item in implemented_features:
            s = _coverage_score(impl_item, spec_item)
            if s > best_score:
                best_score = s
                best_match = impl_item

        is_covered = best_score >= _MATCH_THRESHOLD

        detailed.append({
            "spec_item": spec_item,
            "covered": is_covered,
            "confidence": best_score,
            "matched_by": best_match if is_covered else None,
        })

        if is_covered:
            covered.append(spec_item)
        else:
            missing.append(spec_item)

    return detailed, covered, missing


def validate_component_checklist(
    component: str | int,
    implemented_features: list[str],
    check_tests: bool = True,
) -> dict:
    """
    Compare an implementation description against the spec's requirements.

    Args:
        component:             Component name or id.
        implemented_features:  List of strings describing what has been implemented.
                               Be specific — e.g. ["closes on Escape key press",
                               "traps focus within modal", "has aria-modal attribute"]
        check_tests:           Also check against Test Scenarios (default True).
                               Set False to check Main Features only.

    Returns:
        {
            "component": {id, name},
            "summary": {
                "main_features_covered": int,
                "main_features_total": int,
                "main_features_pct": float,
                "tests_covered": int,         # if check_tests=True
                "tests_total": int,
                "tests_pct": float,
                "overall_status": "PASS" | "PARTIAL" | "FAIL"
            },
            "main_features": {
                "covered": [str, ...],
                "missing": [str, ...],
                "detail": [{spec_item, covered, confidence, matched_by}, ...]
            },
            "test_scenarios": {              # if check_tests=True
                "covered": [str, ...],
                "missing": [str, ...],
                "detail": [...]
            },
            "recommendation": str
        }
    """
    comp = store.resolve_component(component)
    if comp is None:
        return {
            "error": f"Component '{component}' not found.",
            "hint": "Call list_components() to see available component names.",
        }

    main_features = comp.get("main_features", [])
    test_scenarios = comp.get("test_scenarios", [])

    # Check main features
    mf_detail, mf_covered, mf_missing = _check_coverage(main_features, implemented_features)
    mf_pct = len(mf_covered) / len(main_features) * 100 if main_features else 100.0

    result: dict = {
        "component": {"id": comp["id"], "name": comp["name"]},
        "main_features": {
            "covered": mf_covered,
            "missing": mf_missing,
            "detail": mf_detail,
        },
    }

    # Check test scenarios
    ts_pct = 100.0
    ts_covered: list = []
    ts_missing: list = []

    if check_tests and test_scenarios:
        ts_detail, ts_covered, ts_missing = _check_coverage(test_scenarios, implemented_features)
        ts_pct = len(ts_covered) / len(test_scenarios) * 100 if test_scenarios else 100.0
        result["test_scenarios"] = {
            "covered": ts_covered,
            "missing": ts_missing,
            "detail": ts_detail,
        }

    # Determine overall status
    if mf_pct >= 90 and ts_pct >= 75:
        status = "PASS"
        recommendation = (
            "Implementation covers the essential spec requirements. "
            "Review any missing test scenarios and add coverage before shipping."
        )
    elif mf_pct >= 60:
        status = "PARTIAL"
        recommendation = (
            f"Main features are {mf_pct:.0f}% covered. "
            f"The following are missing and should be implemented before this "
            f"component is considered production-ready: "
            + ", ".join(mf_missing[:3])
            + ("..." if len(mf_missing) > 3 else ".")
        )
    else:
        status = "FAIL"
        recommendation = (
            f"Only {mf_pct:.0f}% of main features are covered. "
            "Main Features are non-negotiable — every implementation must include all of them. "
            "Call get_component_spec() to review the full requirements."
        )

    result["summary"] = {
        "main_features_covered": len(mf_covered),
        "main_features_total": len(main_features),
        "main_features_pct": round(mf_pct, 1),
        "tests_covered": len(ts_covered),
        "tests_total": len(test_scenarios),
        "tests_pct": round(ts_pct, 1),
        "overall_status": status,
    }
    result["recommendation"] = recommendation

    return result
