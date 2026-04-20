"""
parsers/parse_catalog.py

Parses Component_Catalog.md into structured component data.
Called once at server startup; results cached in memory.
"""

import re
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

def empty_component() -> dict:
    return {
        "id": None,
        "name": "",
        "category": "",
        "tier": "",
        "summary": "",          # one-line description from component list
        "description": "",      # full Description section
        "main_features": [],
        "secondary_features": {},   # key: section name, value: list of strings
        "test_scenarios": [],
        "notes": [],
        "specializations": [],      # list of specialization names
    }


# ---------------------------------------------------------------------------
# Tier and category index helpers (parsed from the list sections)
# ---------------------------------------------------------------------------

# Maps component number → tier (populated from "Components Listed by Complexity Tier")
_TIER_MAP = {
    range(1, 17): "Basic",
    range(17, 40): "Intermediate",
    range(40, 66): "Advanced",
}

def _tier_for_id(component_id: int) -> str:
    for r, tier in _TIER_MAP.items():
        if component_id in r:
            return tier
    return "Unknown"


# Category descriptions — populated during parse
CATEGORIES = {
    "Content & Typography": [],
    "Layout & Structure": [],
    "Identity & Status Indicators": [],
    "Actions & Navigation Primitives": [],
    "Form Inputs & Controls": [],
    "Feedback & Communication": [],
    "Overlays & Floating Elements": [],
    "Adaptive Elements": [],
    "Navigation & Wayfinding": [],
    "Data Display & Visualization": [],
}

# Component number → category (built during parse)
_CATEGORY_MAP: dict[int, str] = {}


# ---------------------------------------------------------------------------
# Summary checklist parser
# (The "Component Summary Checklist" table at the end of the catalog
#  gives us id, name, category, tier cleanly in one place)
# ---------------------------------------------------------------------------

def _parse_summary_table(text: str) -> dict[int, dict]:
    """
    Parse the summary checklist table into a dict keyed by component id.
    Returns: { 1: {id, name, category, tier}, ... }
    """
    index: dict[int, dict] = {}
    in_table = False

    for line in text.splitlines():
        line = line.strip()
        if "| # |" in line and "Component" in line:
            in_table = True
            continue
        if in_table:
            if not line.startswith("|") or line.startswith("|---"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) < 4:
                continue
            try:
                cid = int(parts[0])
                name = parts[1]
                category = parts[2]
                tier = parts[3]
                index[cid] = {
                    "id": cid,
                    "name": name,
                    "category": category,
                    "tier": tier,
                }
            except (ValueError, IndexError):
                continue

    return index


# ---------------------------------------------------------------------------
# Per-component spec parser
# ---------------------------------------------------------------------------

# Matches heading like: ### #1 Icon {-}
_COMPONENT_HEADING_RE = re.compile(
    r"^#{2,4}\s+#(\d+)\s+(.+?)(?:\s*\{.*?\})?\s*$",
    re.MULTILINE,
)

# Matches section headings inside a component spec
_SECTION_HEADING_RE = re.compile(
    r"^#{4,5}\s+(.+?)(?:\s*\{.*?\})?\s*$",
    re.MULTILINE,
)

# Matches specialization note: *(Heading, Body Text, ...)*
_SPEC_SUMMARY_RE = re.compile(r":::\s*component-summary\s*(.*?)\s*:::", re.DOTALL)


def _extract_bullets(text: str) -> list[str]:
    """Extract bullet list items from a text block."""
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            items.append(line[2:].strip())
        elif re.match(r"^\d+\.\s", line):
            items.append(re.sub(r"^\d+\.\s", "", line).strip())
    return items


def _parse_component_block(component_id: int, name: str, block: str) -> dict:
    """
    Parse a single component's markdown block into a structured dict.
    block: everything between this component heading and the next.
    """
    comp = empty_component()
    comp["id"] = component_id
    comp["name"] = name.strip()

    # Extract one-line summary from ::: component-summary ::: block
    summary_match = _SPEC_SUMMARY_RE.search(block)
    if summary_match:
        comp["summary"] = summary_match.group(1).strip()

    # Split block into named sections
    sections: dict[str, str] = {}
    current_section = "__preamble__"
    current_lines: list[str] = []

    for line in block.splitlines():
        section_match = _SECTION_HEADING_RE.match(line)
        if section_match:
            sections[current_section] = "\n".join(current_lines).strip()
            current_section = section_match.group(1).strip()
            # Normalize section names
            current_section = re.sub(r"\s*\{.*?\}", "", current_section).strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_section] = "\n".join(current_lines).strip()

    # Map sections to component fields
    for section_name, content in sections.items():
        key = section_name.lower()

        if key in ("description", "purpose/description", "purpose"):
            comp["description"] = content.strip()

        elif key == "main features":
            comp["main_features"] = _extract_bullets(content)

        elif key == "test scenarios":
            comp["test_scenarios"] = _extract_bullets(content)

        elif key == "notes":
            comp["notes"] = _extract_bullets(content)

        elif key == "secondary features":
            # Secondary features contain sub-sections
            pass  # handled below via nested parsing

        else:
            # Any other named section under secondary features
            # (Accessibility, Keyboard Navigation, Touch-screen, etc.)
            bullets = _extract_bullets(content)
            if bullets:
                comp["secondary_features"][section_name] = bullets

    # Extract specializations from name line or preamble
    spec_match = re.search(r"\*\((.+?)\)\*", block[:500])
    if spec_match:
        comp["specializations"] = [
            s.strip() for s in spec_match.group(1).split(",")
        ]

    return comp


# ---------------------------------------------------------------------------
# Main parse function
# ---------------------------------------------------------------------------

def parse_catalog(source_path: Optional[Path] = None) -> dict:
    """
    Parse the Component Catalog MD file.

    Returns:
        {
            "components": { id: component_dict, ... },
            "by_name":    { normalized_name: id, ... },
            "by_category": { category: [id, ...], ... },
            "by_tier":    { tier: [id, ...], ... },
            "index":      [ {id, name, category, tier, summary}, ... ]  # for list_components
        }
    """
    if source_path is None:
        source_path = Path(__file__).parent.parent / "source" / "Component_Catalog.md"

    text = source_path.read_text(encoding="utf-8")

    # Step 1 — build id→{name, category, tier} from the summary table
    summary_index = _parse_summary_table(text)

    # Step 2 — find all component heading positions
    heading_matches = list(_COMPONENT_HEADING_RE.finditer(text))

    components: dict[int, dict] = {}

    for i, match in enumerate(heading_matches):
        component_id = int(match.group(1))
        component_name = match.group(2).strip()

        # Block = text from after this heading to before the next heading
        block_start = match.end()
        block_end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(text)
        block = text[block_start:block_end]

        comp = _parse_component_block(component_id, component_name, block)

        # Enrich with category and tier from summary table
        if component_id in summary_index:
            comp["category"] = summary_index[component_id]["category"]
            comp["tier"] = summary_index[component_id]["tier"]
        else:
            comp["tier"] = _tier_for_id(component_id)

        # Use summary from index if not found in spec block
        if not comp["summary"] and component_id in summary_index:
            comp["summary"] = summary_index[component_id].get("name", "")

        components[component_id] = comp

    # For any component in the summary table but not found as a spec block
    # (shouldn't happen but handles edge cases)
    for cid, info in summary_index.items():
        if cid not in components:
            comp = empty_component()
            comp.update(info)
            components[cid] = comp

    # Build lookup indexes
    by_name: dict[str, int] = {}
    by_category: dict[str, list[int]] = {}
    by_tier: dict[str, list[int]] = {}

    for cid, comp in components.items():
        # Normalize name for lookup
        norm = comp["name"].lower().replace(" ", "_").replace("/", "_")
        by_name[norm] = cid
        # Also index by just the primary name before any slash
        primary = comp["name"].split("/")[0].strip().lower().replace(" ", "_")
        by_name[primary] = cid

        cat = comp.get("category", "Unknown")
        by_category.setdefault(cat, []).append(cid)

        tier = comp.get("tier", "Unknown")
        by_tier.setdefault(tier, []).append(cid)

    # Build the flat index list (used by list_components tool)
    index_list = [
        {
            "id": comp["id"],
            "name": comp["name"],
            "category": comp.get("category", ""),
            "tier": comp.get("tier", ""),
            "summary": comp.get("summary", ""),
            "specializations": comp.get("specializations", []),
        }
        for comp in sorted(components.values(), key=lambda c: c["id"] or 0)
    ]

    return {
        "components": components,
        "by_name": by_name,
        "by_category": by_category,
        "by_tier": by_tier,
        "index": index_list,
    }
