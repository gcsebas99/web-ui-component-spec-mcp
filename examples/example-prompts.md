# Example Prompts

Practical examples of how to use the skill and MCP server together.
Paste the skill content into your system prompt, then use these as starting prompts.

---

## Build a component from scratch

```
I'm building a React + TypeScript + Tailwind CSS design system.
Using the Web UI Component Specification as the behavioral reference,
implement a Modal component (component #46).

Before starting:
1. Check its dependencies with get_related_components
2. Load the full spec with get_component_spec
3. Implement all Main Features first, then Accessibility secondary features
4. Use the Test Scenarios as the test suite

Output: the component file, a test file, and a brief summary of any
implementation decisions made.
```

---

## Build a library from scratch

```
I'm starting a new web UI library for a SaaS dashboard application.
Stack: React, TypeScript, Tailwind CSS.

Using the Web UI Component Specification:
1. Call get_components_by_scenario("saas_dashboard") to scope the work
2. Call get_step_by_step([1,2,3,4]) to define design tokens
3. Propose a build plan: which components to build in which order,
   grouped by tier

I want to start with the Tier 1 (Basic) components today.
Begin with Button (#16) — load its spec and implement it fully.
```

---

## Review a component against the spec

```
Review this Button component implementation against the
Web UI Component Specification.

[paste component code here]

Use validate_component_checklist to compare what's implemented
against the spec's Main Features and Test Scenarios.
Report: what's covered, what's missing, overall status.
```

---

## Add tests to an existing component

```
I have this Modal component:

[paste component code here]

Using the Web UI Component Specification:
1. Call get_component_tests("Modal") to get the official test scenarios
2. Write a complete test suite using React Testing Library + jest-axe
3. Each test scenario from the spec should map to at least one test case
4. Flag any scenarios that require manual testing (screen reader, etc.)
```

---

## Review design tokens

```
Review these design token definitions against the
Web UI Component Specification's Core Principles.

[paste token file here]

Call get_core_principles("design_tokens") and check:
- Are all required token categories present?
- Are naming conventions consistent?
- Are accessibility contrast requirements documented?
- What's missing or should be added?
```

---

## Find the right component for a use case

```
I need a component that lets users select a date range
(start date and end date) for a reporting filter.

Use search_components to find the relevant components,
then load the appropriate spec and summarize what I need to implement.
```
