"""
parsers/parse_principles.py

Parses Core_Principles.md into named sections for surgical retrieval.
"""

import re
from pathlib import Path
from typing import Optional


# The named sections we expose via get_core_principles
SECTION_KEYS = {
    "philosophy":            "Component Philosophy",
    "design_tokens":         "Design Tokens",
    "interaction_principles":"Interaction Principles",
    "consistency_patterns":  "Consistency Patterns",
}


def parse_principles(source_path: Optional[Path] = None) -> dict[str, str]:
    """
    Parse Core Principles into a dict of section_key → raw markdown text.

    Returns:
        {
            "philosophy": "...",
            "design_tokens": "...",
            "interaction_principles": "...",
            "consistency_patterns": "...",
            "all": "..."   # full document text
        }
    """
    if source_path is None:
        source_path = Path(__file__).parent.parent / "source" / "Core_Principles.md"

    text = source_path.read_text(encoding="utf-8")

    # Build a reverse map: heading text → section key
    heading_to_key = {v: k for k, v in SECTION_KEYS.items()}

    # Find all h2 headings
    h2_pattern = re.compile(r"^## (.+?)(?:\s*\{.*?\})?\s*$", re.MULTILINE)
    matches = list(h2_pattern.finditer(text))

    sections: dict[str, str] = {"all": text}

    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        block_start = match.end()
        block_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[block_start:block_end].strip()

        key = heading_to_key.get(heading)
        if key:
            sections[key] = f"## {heading}\n\n{block}"

    return sections
