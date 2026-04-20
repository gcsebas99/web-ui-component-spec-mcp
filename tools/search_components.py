"""
tools/search_components.py

Fuzzy search across component names, summaries, and feature text.
"""

from data.store import store

try:
    from thefuzz import fuzz
    _FUZZY_AVAILABLE = True
except ImportError:
    _FUZZY_AVAILABLE = False


def _simple_match(query: str, text: str) -> int:
    """Fallback scorer when thefuzz is not installed."""
    q = query.lower()
    t = text.lower()
    if q == t:
        return 100
    if q in t:
        return 80
    # Word overlap
    q_words = set(q.split())
    t_words = set(t.split())
    overlap = len(q_words & t_words)
    if overlap:
        return int(60 * overlap / max(len(q_words), 1))
    return 0


def _score(query: str, text: str) -> int:
    if not text:
        return 0
    if _FUZZY_AVAILABLE:
        return max(
            fuzz.partial_ratio(query.lower(), text.lower()),
            fuzz.token_set_ratio(query.lower(), text.lower()),
        )
    return _simple_match(query, text)


def search_components(query: str, limit: int = 8) -> dict:
    """
    Fuzzy search across component names, descriptions, and features.

    Args:
        query: Search string. e.g. "date range picker", "keyboard navigation",
               "file upload", "focus trap"
        limit: Maximum number of results (default 8).

    Returns:
        {
            "query": str,
            "results": [
                {
                    "id": int,
                    "name": str,
                    "category": str,
                    "tier": str,
                    "summary": str,
                    "relevance_score": int,
                    "matched_in": [str, ...]   # which fields matched
                },
                ...
            ]
        }
    """
    index = store.catalog.get("index", [])
    components = store.catalog.get("components", {})

    scored = []

    for entry in index:
        cid = entry.get("id")
        comp = components.get(cid, entry)

        scores = {}

        # Score against name
        name_score = _score(query, entry.get("name", ""))
        if name_score > 40:
            scores["name"] = name_score

        # Score against summary
        summary_score = _score(query, entry.get("summary", ""))
        if summary_score > 50:
            scores["summary"] = summary_score

        # Score against description
        desc_score = _score(query, comp.get("description", ""))
        if desc_score > 55:
            scores["description"] = desc_score

        # Score against main features (joined)
        features_text = " ".join(comp.get("main_features", []))
        features_score = _score(query, features_text)
        if features_score > 55:
            scores["main_features"] = features_score

        # Score against specialization names
        spec_text = " ".join(entry.get("specializations", []))
        spec_score = _score(query, spec_text)
        if spec_score > 60:
            scores["specializations"] = spec_score

        if scores:
            best_score = max(scores.values())
            scored.append({
                "id": entry.get("id"),
                "name": entry.get("name", ""),
                "category": entry.get("category", ""),
                "tier": entry.get("tier", ""),
                "summary": entry.get("summary", ""),
                "relevance_score": best_score,
                "matched_in": list(scores.keys()),
            })

    # Sort by score descending
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)

    return {
        "query": query,
        "results": scored[:limit],
        "total_matches": len(scored),
    }
