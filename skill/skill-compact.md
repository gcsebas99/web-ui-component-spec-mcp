# UI Spec Skill — Compact

Use the Web UI Component Specification MCP when building, reviewing, or testing web UI components.

## Core constraints (always apply)
- Components receive state, emit events, contain no business logic
- All Main Features are required — no exceptions
- Accessibility secondary features are non-negotiable
- Test Scenarios = definition of done
- `prefers-reduced-motion` must always be respected

## Tool reference
| Tool | Use when |
|---|---|
| `list_components()` | Need to know what exists |
| `get_component_spec(name)` | Implementing a component |
| `get_component_tests(names)` | Writing or reviewing tests |
| `get_component_summary(names)` | Planning only |
| `get_related_components(name)` | Check dependencies first |
| `search_components(query)` | Find component by behavior |
| `validate_component_checklist(name, features)` | QA before marking done |
| `get_core_principles(section)` | Token or philosophy reference |
| `get_step_by_step([n])` | Build process reference |
| `get_components_by_scenario(type)` | Scoping a new library |

## Build order (always)
1. Dependencies first → `get_related_components`
2. Full spec → `get_component_spec`
3. Main Features → then Accessibility → then other secondary features
4. Tests → `get_component_tests`
5. Validate → `validate_component_checklist`
