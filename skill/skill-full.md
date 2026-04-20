# Web UI Component Specification — Agent Skill

## When to use this skill

Activate this skill whenever you are:
- Building, scaffolding, or implementing web UI components
- Reviewing existing component code against a specification
- Writing or auditing tests for UI components
- Defining or reviewing design tokens, spacing, or look & feel decisions
- Planning a UI library build from scratch

This skill works in conjunction with the **Web UI Component Specification MCP server**, which provides on-demand access to the full spec data. The skill encodes *how to work*; the MCP provides *what the spec says*.

---

## Component Philosophy

All components in this specification follow a **presentational** approach. Hold these constraints in working memory for every component you build or review:

- **State receivers, not calculators** — components accept state from outside (`hasError`, `isDisabled`, `value`) and display it. They do not determine what state they should be in.
- **Event emitters, not decision-makers** — components fire events (`onChange`, `onBlur`, `onClick`) and report what the user did. They do not decide what happens next.
- **No business logic inside components** — validation, data fetching, and application decisions belong to the layer above.
- **Composable** — base components are extended by specializations. A specialization inherits everything from its base and only documents what is added or different.
- **Flexible but protected** — visual properties (margin, max-width) can be overridden; behavioral and accessibility properties must not be.

---

## Non-Negotiables

These apply to every component, every time, without exception:

1. **All Main Features are required.** They are not a menu to pick from — every implementation must include all of them.
2. **Accessibility secondary features are non-negotiable.** Keyboard accessibility, ARIA roles/states, focus management, and label associations are part of the definition of done, not optional polish.
3. **Test Scenarios are the definition of done.** A component is not complete until it passes all its test scenarios. They are not suggestions.
4. **Color is never the only signal.** Every color-based state (error, success, disabled) must also have a text label, icon, or pattern.
5. **`prefers-reduced-motion` must always be respected.** No exceptions.

---

## Working Process by Scenario

### Building a component from scratch
1. Call `get_related_components(name)` — understand what this component depends on and build dependencies first
2. Call `get_component_spec(name)` — load the full spec
3. Implement all **Main Features** before any Secondary Features
4. Implement **Accessibility** secondary features next — they are non-negotiable
5. Implement remaining secondary features based on project requirements
6. Call `get_component_tests(name)` — use test scenarios as your test suite
7. Call `validate_component_checklist(name, implemented_features)` before marking done

### Building a library from scratch
1. Call `get_components_by_scenario(project_type)` — get a curated component list and build order
2. Call `get_core_principles("philosophy")` — load the component philosophy
3. Call `get_step_by_step([1,2,3,4])` — define design tokens before writing any component code
4. Call `get_step_by_step([5,6])` — set up the dev environment and implement tokens
5. Build Tier 1 (Basic) components first — call `list_components(tier="Basic")`
6. Progress to Tier 2, then Tier 3

### Reviewing a component against the spec
1. Call `get_component_tests(name)` — get the test scenarios
2. Call `validate_component_checklist(name, implemented_features)` — get a gap report
3. Call `get_component_spec(name)` only if gaps need deeper investigation

### Writing tests for a component
1. Call `get_component_tests(name)` — the test scenarios are your test specification
2. Each scenario describes one interaction and its expected outcome — map each directly to a test case
3. Accessibility test scenarios require both automated tooling (axe-core) and manual keyboard/screen reader verification

### Reviewing or adjusting design tokens
1. Call `get_core_principles("design_tokens")` — load the full token reference
2. Call `get_step_by_step([1,2,3,4])` — review the definition steps

---

## MCP Tool Reference

| Tool | When to call it |
|---|---|
| `list_components()` | Start of any session — establishes what exists |
| `get_component_spec(name)` | Implementing a component |
| `get_component_tests(names)` | Writing or reviewing tests |
| `get_component_summary(names)` | Planning, surveying scope |
| `get_components_by_scenario(type)` | Starting a library from scratch |
| `get_core_principles(section)` | Reviewing philosophy or token definitions |
| `get_step_by_step(steps)` | Following the build process |
| `get_related_components(name)` | Understanding dependencies before building |
| `search_components(query)` | Finding a component by behavior description |
| `validate_component_checklist(name, features)` | QA before marking a component done |

**Context efficiency rules:**
- Fetch one component at a time with `get_component_spec` — never request the full catalog
- Use `get_component_tests` instead of `get_component_spec` when tests are all you need
- Use `get_component_summary` instead of `get_component_spec` during planning
- Use `get_core_principles(section)` with a specific section — avoid `"all"` unless necessary
- Use `get_step_by_step([n])` with specific step numbers — avoid `"all"` unless necessary

---

## Consistency Patterns (always apply)

**State prop naming** — use consistently across all components:
- `isDisabled` / `disabled` — cannot be interacted with
- `isLoading` / `loading` — async action in progress
- `hasError` / `error` — in error state
- `isRequired` / `required` — mandatory input
- `isReadOnly` / `readOnly` — visible but not editable

**Common props** — all form inputs accept: `value`, `onChange`, `onBlur`, `onFocus`, `disabled`, `required`

**Visual states** — focus, hover, error, success, and disabled must look identical across all components in the system.
