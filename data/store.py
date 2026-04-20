"""
data/store.py

Loads and caches all parsed spec data at server startup.
All tools import from here — single source of truth, parsed once.
"""

from pathlib import Path
from typing import Optional
import sys
import os

# Allow running from any working directory
_ROOT = Path(__file__).parent.parent


def _find_source_dir() -> Path:
    """
    Locate the source/ directory.
    Works for:
      - clone-and-run (source/ relative to project root)
      - pip/uvx install (source/ bundled alongside server.py)
    """
    candidates = [
        _ROOT / "source",
        Path(sys.argv[0]).parent / "source",
        Path(__file__).parent.parent / "source",
    ]
    # Allow env var override for custom source locations
    env_source = os.environ.get("UI_SPEC_SOURCE_DIR")
    if env_source:
        candidates.insert(0, Path(env_source))

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Cannot find source/ directory containing spec MD files. "
        "Set UI_SPEC_SOURCE_DIR environment variable to specify location."
    )


class SpecStore:
    """
    In-memory store for all parsed spec data.
    Initialized once at startup via SpecStore.load().
    """

    def __init__(self):
        self.catalog: dict = {}       # from parse_catalog()
        self.principles: dict = {}    # from parse_principles()
        self.stepbystep: dict = {}    # from parse_stepbystep()
        self._loaded = False

    def load(self, source_dir: Optional[Path] = None) -> None:
        if self._loaded:
            return

        from parsers.parse_catalog import parse_catalog
        from parsers.parse_principles import parse_principles
        from parsers.parse_stepbystep import parse_stepbystep

        if source_dir is None:
            source_dir = _find_source_dir()

        print(f"[ui-spec-mcp] Loading spec data from {source_dir}", file=sys.stderr, flush=True)

        self.catalog = parse_catalog(source_dir / "Component_Catalog.md")
        self.principles = parse_principles(source_dir / "Core_Principles.md")
        self.stepbystep = parse_stepbystep(source_dir / "Step_By_Step_Guide.md")

        component_count = len(self.catalog.get("components", {}))
        step_count = len(self.stepbystep.get("steps", {}))
        print(
            f"[ui-spec-mcp] Loaded {component_count} components, "
            f"{step_count} steps, principles OK",
            file=sys.stderr,
            flush=True,
        )
        self._loaded = True

    # ------------------------------------------------------------------
    # Component lookup helpers (used by multiple tools)
    # ------------------------------------------------------------------

    def resolve_component(self, name_or_id: str | int) -> Optional[dict]:
        """
        Resolve a component by name (string) or id (int).
        Returns the component dict or None if not found.
        """
        components = self.catalog.get("components", {})

        # Integer id
        if isinstance(name_or_id, int):
            return components.get(name_or_id)

        # Try as integer string
        try:
            cid = int(name_or_id)
            return components.get(cid)
        except (ValueError, TypeError):
            pass

        # Normalize name and look up
        by_name = self.catalog.get("by_name", {})
        norm = str(name_or_id).lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        cid = by_name.get(norm)
        if cid:
            return components.get(cid)

        # Partial match fallback
        for key, cid in by_name.items():
            if norm in key or key in norm:
                return components.get(cid)

        return None


# Singleton — imported by all tools
store = SpecStore()
