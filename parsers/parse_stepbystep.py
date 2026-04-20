"""
parsers/parse_stepbystep.py

Parses Step_By_Step_Guide.md into individual steps for surgical retrieval.
"""

import re
from pathlib import Path
from typing import Optional


# Step number → title (for reference and validation)
STEP_TITLES = {
    1:  "Define Your Color Palette",
    2:  "Define Your Typography System",
    3:  "Define Spacing and Layout System",
    4:  "Define Look & Feel Decisions",
    5:  "Set Up Development Environment",
    6:  "Implement Design Tokens in Code",
    7:  "Build Foundational Components",
    8:  "Build Compound Components",
    9:  "Ensure Test Coverage and Quality",
    10: "Create Documentation and Usage Guidelines",
    11: "Gather Feedback and Iterate",
}


def parse_stepbystep(source_path: Optional[Path] = None) -> dict:
    """
    Parse the Step-by-Step Guide into individual steps.

    Returns:
        {
            "steps": { 1: {number, title, content}, ... },
            "titles": { 1: "Define Your Color Palette", ... },
            "all": "full document text"
        }
    """
    if source_path is None:
        source_path = Path(__file__).parent.parent / "source" / "Step_By_Step_Guide.md"

    text = source_path.read_text(encoding="utf-8")

    # Match "### Step N: Title" headings
    step_pattern = re.compile(
        r"^## Step (\d+):\s+(.+?)(?:\s*\{.*?\})?\s*$",
        re.MULTILINE,
    )
    matches = list(step_pattern.finditer(text))

    steps: dict[int, dict] = {}

    for i, match in enumerate(matches):
        step_num = int(match.group(1))
        title = match.group(2).strip()
        block_start = match.end()
        block_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[block_start:block_end].strip()

        steps[step_num] = {
            "number": step_num,
            "title": title,
            "content": f"### Step {step_num}: {title}\n\n{content}",
        }

    return {
        "steps": steps,
        "titles": {n: s["title"] for n, s in steps.items()},
        "all": text,
    }
