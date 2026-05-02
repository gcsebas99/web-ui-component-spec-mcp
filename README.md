# Web UI Component Specification — MCP Server

An MCP (Model Context Protocol) server that gives AI coding assistants
direct access to the [Web UI Component Specification](https://github.com/yourname/web-ui-component-spec) —
a comprehensive behavioral reference for web UI component libraries covering
component specs, test scenarios, accessibility requirements, and a step-by-step build guide.

---

## What this does

Instead of pasting spec content into prompts manually, this server lets your
AI assistant query exactly what it needs, when it needs it:

- **Building a component?** → Fetch its full spec on demand
- **Writing tests?** → Get just the test scenarios
- **Starting a library?** → Get a curated component list for your project type
- **Reviewing an implementation?** → Validate it against the spec automatically

---

## Read the specification

Prefer the human-readable version? Download the full spec as a PDF:

**[Web UI Component Specification (v1.0) — PDF](https://github.com/gcsebas99/web-ui-component-spec-mcp/raw/main/exports/v1.0/Web_UI_Component_Specification_v1.0.pdf)**

All exported versions live under [`exports/`](exports/).

---

## Installation

### Option 1 — uvx (recommended, no install required)

```bash
uvx web-ui-component-spec-mcp
```

### Option 2 — pip

```bash
pip install web-ui-component-spec-mcp
web-ui-spec-mcp
```

### Option 3 — Clone and run

```bash
git clone https://github.com/gcsebas99/web-ui-component-spec-mcp.git
cd web-ui-component-spec-mcp
pip install -r requirements.txt
```

Then execute `server.py`.

```bash
python server.py
```

---

## MCP Client Configuration

Add to your MCP client config (Claude Desktop, Cursor, etc.):

**uvx:**
```json
{
  "mcpServers": {
    "ui-spec": {
      "command": "uvx",
      "args": ["web-ui-component-spec-mcp"]
    }
  }
}
```

**pip install:**
```json
{
  "mcpServers": {
    "ui-spec": {
      "command": "web-ui-spec-mcp"
    }
  }
}
```

**Clone and run:**
```json
{
  "mcpServers": {
    "ui-spec": {
      "command": "python",
      "args": ["/absolute/path/to/web-ui-component-spec-mcp/server.py"]
    }
  }
}
```

---

## Source files

The spec content (Markdown files) are included in the `source/` directory (latest version available):

| File | Description |
|---|---|
| `source/Core_Principles.md` | Component philosophy, design tokens, interaction principles |
| `source/Component_Catalog.md` | Full catalog of all components with specs and tests |
| `source/Step_By_Step_Guide.md` | Step-by-step build guide |

---

## Available tools

| Tool | Description |
|---|---|
| `list_components` | Full component index with optional category/tier filtering |
| `get_component_spec` | Full spec for one component |
| `get_component_tests` | Test scenarios only for one or more components |
| `get_component_summary` | Lightweight summary (description + main features) |
| `get_components_by_scenario` | Curated component list for a project type |
| `get_core_principles` | Core Principles by section |
| `get_step_by_step` | Step-by-step guide by step number |
| `get_related_components` | Dependencies, dependents, and alternatives |
| `search_components` | Fuzzy search by behavior or description |
| `validate_component_checklist` | Coverage report against spec requirements |

---

## Using the skill

For best results, load the skill file into your AI assistant's system prompt
before starting a component build session.

**Full skill** (recommended for new sessions):
[`skill/skill-full.md`](skill/skill-full.md)

**Compact skill** (for mid-session use when context is limited):
[`skill/skill-compact.md`](skill/skill-compact.md)

---

## Example prompts

See [`examples/example-prompts.md`](examples/example-prompts.md) for
ready-to-use prompts covering common scenarios:
building a component, starting a library, reviewing code, writing tests.

---

## Project structure

```
web-ui-component-spec-mcp/
├── server.py              # MCP server entry point
├── pyproject.toml         # PyPI packaging (pip + uvx)
├── requirements.txt       # Direct install dependencies
│
├── tools/                 # One file per MCP tool
├── parsers/               # MD parsing logic
├── data/                  # In-memory store (loaded at startup)
│
├── source/                # Spec MD files (bundled; VERSION.md pins the revision)
├── exports/                # Human-readable PDF exports of the spec
├── skill/                 # Skill files for AI assistants
└── examples/              # Example prompts
```

---

## Spec version

This server is built for **Web UI Component Specification v1.0**.

| Spec version | Server version |
|---|---|
| v1.0 | 1.0.x |

---

## License

MIT
