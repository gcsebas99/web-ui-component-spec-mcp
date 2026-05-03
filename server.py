"""
server.py

Web UI Component Specification — MCP Server
Entry point for both clone-and-run and uvx/pip installs.

Usage (clone and run):
    python server.py

Usage (after pip install):
    web-ui-component-spec-mcp

MCP client config:
    {
        "mcpServers": {
            "ui-spec": {
                "command": "web-ui-component-spec-mcp"
            }
        }
    }
"""

import sys
import json
from pathlib import Path

# Ensure project root is on the path when running directly
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

from data.store import store
from tools import (
    list_components,
    get_component_spec,
    get_component_tests,
    get_component_summary,
    get_components_by_scenario,
    get_core_principles,
    get_step_by_step,
    get_related_components,
    search_components,
    validate_component_checklist,
)

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

app = Server("web-ui-component-spec-mcp")

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    Tool(
        name="list_components",
        description=(
            "List all components in the Web UI Component Specification. "
            "Returns name, id, category, tier, and one-line summary for each. "
            "Always call this first in a new session to establish what exists. "
            "Optionally filter by category or tier."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "Filter by functional category (partial match, case-insensitive). "
                        "Options: 'Content & Typography', 'Layout & Structure', "
                        "'Identity & Status Indicators', 'Actions & Navigation Primitives', "
                        "'Form Inputs & Controls', 'Feedback & Communication', "
                        "'Overlays & Floating Elements', 'Adaptive Elements', "
                        "'Navigation & Wayfinding', 'Data Display & Visualization'"
                    ),
                    "default": "",
                },
                "tier": {
                    "type": "string",
                    "description": "Filter by complexity tier: 'Basic', 'Intermediate', or 'Advanced'",
                    "default": "",
                },
            },
        },
    ),
    Tool(
        name="get_component_spec",
        description=(
            "Return the full behavioral specification for a single component. "
            "Includes description, all main features, secondary features "
            "(accessibility, keyboard navigation, touch, responsive, i18n, etc.), "
            "and implementation notes. "
            "Use this when implementing a component from scratch."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "component": {
                    "type": "string",
                    "description": "Component name (e.g. 'Modal', 'Text Input', 'Button') or numeric id (e.g. '46', '19', '16')",
                },
            },
            "required": ["component"],
        },
    ),
    Tool(
        name="get_component_tests",
        description=(
            "Return only the Test Scenarios for one or more components. "
            "Use this when writing tests or reviewing an implementation against the spec. "
            "More token-efficient than get_component_spec when tests are all you need."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of component names or ids. e.g. ['Modal', 'Button'] or ['46', '16']",
                },
            },
            "required": ["components"],
        },
    ),
    Tool(
        name="get_component_summary",
        description=(
            "Return a lightweight summary for one or more components — "
            "description and main features only, no secondary features or test scenarios. "
            "Use this for planning and surveying before deep implementation work."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of component names or ids.",
                },
            },
            "required": ["components"],
        },
    ),
    Tool(
        name="get_components_by_scenario",
        description=(
            "Return a curated component list and recommended build order for a project type. "
            "Use this when starting a library from scratch to get a sensible scope and sequence. "
            "Pass 'list' as scenario to see all available options."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "description": (
                        "Project type. e.g. 'saas_dashboard', 'ecommerce', 'forms_heavy', "
                        "'content_site', 'mobile_web', 'minimal'. "
                        "Pass 'list' to see all options."
                    ),
                },
            },
            "required": ["scenario"],
        },
    ),
    Tool(
        name="get_core_principles",
        description=(
            "Return content from the Core Principles section of the spec. "
            "Fetch only the section you need to minimize context usage. "
            "Use 'philosophy' when starting any component work. "
            "Use 'design_tokens' when reviewing token definitions. "
            "Use 'all' sparingly."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": (
                        "Section to retrieve. Options: "
                        "'philosophy', 'design_tokens', 'interaction_principles', "
                        "'consistency_patterns', 'all'"
                    ),
                    "default": "philosophy",
                },
            },
        },
    ),
    Tool(
        name="get_step_by_step",
        description=(
            "Return one or more steps from the Step-by-Step Build Guide. "
            "Fetch only the steps relevant to the current phase of work. "
            "e.g. pass [1, 2, 3] when defining design tokens, [7, 8] when building components."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "steps": {
                    "description": (
                        "Step number(s) to retrieve, or 'all'. "
                        "Steps: 1=Color, 2=Typography, 3=Spacing, 4=Look&Feel, "
                        "5=DevEnv, 6=Tokens, 7=Foundational Components, "
                        "8=Compound Components, 9=Testing, 10=Documentation, 11=Iterate"
                    ),
                    "oneOf": [
                        {"type": "integer"},
                        {"type": "array", "items": {"type": "integer"}},
                        {"type": "string", "enum": ["all"]},
                    ],
                },
            },
            "required": ["steps"],
        },
    ),
    Tool(
        name="get_related_components",
        description=(
            "Return dependency and relationship information for a component: "
            "what it depends on, what depends on it, and what it's commonly confused with. "
            "Call this before implementing to understand what needs to be built first."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "component": {
                    "type": "string",
                    "description": "Component name or id.",
                },
            },
            "required": ["component"],
        },
    ),
    Tool(
        name="search_components",
        description=(
            "Fuzzy search across component names, descriptions, and features. "
            "Use this when you know what behavior you need but not which component provides it. "
            "e.g. 'focus trap', 'date range', 'file upload', 'keyboard navigation'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search string describing the behavior or component you're looking for.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 8).",
                    "default": 8,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="validate_component_checklist",
        description=(
            "Compare an implementation against the spec's Main Features and Test Scenarios. "
            "Returns a coverage report showing what's covered, what's missing, and an overall status. "
            "Use this to QA a component before marking it done."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "component": {
                    "type": "string",
                    "description": "Component name or id.",
                },
                "implemented_features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "List of strings describing what has been implemented. "
                        "Be specific: e.g. ['closes on Escape key', 'traps focus within modal', "
                        "'has aria-modal attribute', 'backdrop click dismisses modal']"
                    ),
                },
                "check_tests": {
                    "type": "boolean",
                    "description": "Also check against Test Scenarios (default true).",
                    "default": True,
                },
            },
            "required": ["component", "implemented_features"],
        },
    ),
]

# ---------------------------------------------------------------------------
# Handler: list tools
# ---------------------------------------------------------------------------

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return TOOLS

# ---------------------------------------------------------------------------
# Handler: call tool
# ---------------------------------------------------------------------------

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = _dispatch(name, arguments)
    except Exception as exc:
        result = {"error": str(exc), "tool": name}

    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


def _dispatch(name: str, args: dict):
    """Route tool calls to their handler functions."""
    match name:
        case "list_components":
            return list_components(
                category=args.get("category", ""),
                tier=args.get("tier", ""),
            )
        case "get_component_spec":
            return get_component_spec(args["component"])

        case "get_component_tests":
            return get_component_tests(args["components"])

        case "get_component_summary":
            return get_component_summary(args["components"])

        case "get_components_by_scenario":
            return get_components_by_scenario(args["scenario"])

        case "get_core_principles":
            return get_core_principles(args.get("section", "philosophy"))

        case "get_step_by_step":
            return get_step_by_step(args["steps"])

        case "get_related_components":
            return get_related_components(args["component"])

        case "search_components":
            return search_components(
                query=args["query"],
                limit=args.get("limit", 8),
            )
        case "validate_component_checklist":
            return validate_component_checklist(
                component=args["component"],
                implemented_features=args["implemented_features"],
                check_tests=args.get("check_tests", True),
            )
        case _:
            return {"error": f"Unknown tool: {name}"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    import asyncio

    # Load all spec data before starting the server
    store.load()

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )

    asyncio.run(_run())


if __name__ == "__main__":
    main()
