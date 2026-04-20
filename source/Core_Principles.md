
# Core Principles

## Component Philosophy

Good UI components are deceptively simple to use and surprisingly hard to build well. The gap between a component that *appears* to work and one that *actually* works — under keyboard navigation, with a screen reader, across edge cases, in the hands of a user who interacts with it differently than you expected — is where most of the real engineering effort lives. This specification takes a specific philosophical stance on how to close that gap, and understanding that stance is essential before reading any individual component specification.

The components described here follow a **presentational** approach. They are responsible for rendering visual state and communicating user interactions — nothing more. They do not contain business logic. They do not decide whether a form field's value is valid. They do not determine what happens when a button is clicked. These concerns belong to the layer above: the application, the form controller, the state management system. A component's job is to show what it's told and report what the user does.

This separation is not just an architectural preference — it's what makes components genuinely reusable. A component that embeds validation logic, or that makes assumptions about what should happen on submit, is only usable in the contexts it was designed for. A component that purely receives state and emits events can be used anywhere. It can be tested in isolation. It can be understood without knowing anything about the application it's embedded in. It can be handed to an AI system with a clear behavioral specification and implemented correctly the first time. The presentational philosophy is what makes this specification possible.

The five design principles that follow from this philosophy — simple and focused, state receivers, event emitters, composable, and flexible — are not independent rules. They reinforce each other. A component that receives state rather than calculating it is naturally simpler. A component that emits events rather than handling them is naturally composable. Understanding them as a unified stance, rather than a checklist, is what produces components that feel coherent rather than assembled.

**Simple and Focused**

The first and most important constraint is simplicity. A component should do one thing well: render its current state visually and respond to user interactions. The moment a component starts making decisions — validating input, calculating what should happen next, managing application state — it becomes harder to test, harder to reuse, and harder to reason about. Keeping components "dumb" isn't a limitation; it's the quality that makes them composable across an entire system.

- Components handle visual states and user interactions

- They do NOT contain business logic or validation rules

- They are "dumb" in the best sense: predictable, testable, and reusable

**State Receivers, Not State Calculators**

Think of a component as a display, not a decision-maker. It should accept whatever state it's given — an error flag, a loading indicator, a current value — and render it faithfully. The question of why a field is in an error state, or when it should be, belongs to the layer above. When a component tries to own that logic, it can only work correctly in the specific context it was built for. When it simply reflects state, it works everywhere.

- Components accept state from parent components or external systems (e.g., `hasError`, `isDisabled`, `value`)

- They display that state visually

- They do NOT determine what state they should be in

**Event Emitters**

Components communicate upward through events, not by acting on their own judgment. When a user types, the component fires `onChange`. When they leave the field, it fires `onBlur`. What happens next — whether to validate, navigate, submit, or do nothing — is the application's responsibility. This contract keeps components honest: they report faithfully, and the system decides. It also makes testing dramatically simpler, since you can verify a component's behavior by observing its events without needing to simulate an entire application around it.

- Components notify when user interactions occur (e.g., `onChange`, `onBlur`, `onFocus`, `onClick`)

- They do NOT decide what happens in response to those events

- External logic (form controllers, validation libraries, state management) handles the decisions

**Composable and Extendable**

A well-designed component is a starting point, not an endpoint. Base components should be buildable-upon — a `text-input` becomes an `email-input` by adding format validation feedback; it becomes a `search-input` by adding a clear button and search icon. Specializations inherit everything from their base and only describe what's different. This keeps the system from growing into dozens of one-off components that share no common lineage and drift apart over time.

- Base components can be extended to create specialized variants

::: example
e.g. `text-input` → `email-input`, `money-input`, `search-input`
:::

- Specialized components inherit base behavior and add specific features

**Flexible for Customization**

Components will inevitably need to adapt to different contexts — different container widths, different surrounding layouts, different visual contexts. A good component allows this without requiring consumers to wrap it in extra divs or fight its internals. The key is knowing what to protect and what to expose: visual properties like margin, max-width, and display can be freely overridden; behavioral and accessibility properties — focus management, ARIA attributes, keyboard handling — should be defended. Flexibility in service of reuse, not flexibility at the cost of correctness.

- Components should allow basic styling/positioning adjustments without requiring wrappers

- Accept standard web extension mechanisms (e.g., `className`, `style`, data attributes) while keeping core behavior intact

- Non-critical visual properties (margins, max-width, display) can be overridden by consumers

- Critical behavioral and accessibility properties should be protected/enforced

- Balance: Make common adjustments easy, but maintain component integrity

**Example: Text Input Component**

::: example-code
```jsx
// Component receives state
<TextInput 
  value="john@example"
  hasError={!!error}
  errorMessage={errorMessage}
  onChange={handleChange}  // Component notifies of changes
  onBlur={handleBlur}      // Component notifies when user leaves field
/>

// External validation logic (NOT in component)
const handleBlur = (value) => {
  const isValid = validateEmail(value);
  setError(!isValid);
  setErrorMessage(isValid ? "" : "Invalid email format");
}
```
:::

> **Note for non-web platforms**: The prop names above use web/React conventions (`onChange`, `onBlur`, `className`). On other platforms, translate these to your framework's equivalents — the behavioral contract (receive state, emit events, avoid internal logic) remains the same regardless of syntax.


## Design Tokens

Design tokens are the **foundational variables** that create visual consistency across your UI system. They are the bridge between design decisions and code — named, reusable values that encode choices like "the primary action color," "the base spacing unit," or "the duration of a standard transition," in a way that components can consume without hardcoding specific values.

The importance of tokens extends well beyond convenience. Without them, visual decisions get scattered across a codebase as magic numbers and hardcoded hex values. When a brand color changes, or a spacing system is refined, updates become a search-and-replace exercise across dozens of files — error-prone and never quite complete. Tokens centralize those decisions in one place, so a single change propagates automatically to every component that references that token. This is what makes a UI system feel coherent and what makes it maintainable over time.

Tokens also serve as the vocabulary shared between design tools and code. When a designer specifies that a button background should use `color-primary-600`, and that same name exists in the codebase as a CSS Custom Property, the design intent translates directly without interpretation or loss. This shared language reduces the most common category of design-to-development friction: the gap between what was designed and what was built.

Design tokens should be defined before building any components. Components that are built without tokens become tightly coupled to specific values, making theming, dark mode, and future design updates significantly harder. Defining tokens first is the investment that pays for itself repeatedly throughout the life of a UI system.

#### Color Palette {-}

Color is the most immediate signal your UI sends. Before a user reads a label or processes a layout, they've already registered whether something looks like a primary action, an error, or a disabled state. A well-defined color palette makes those signals consistent and intentional — not just aesthetically, but semantically. The categories below aren't arbitrary groupings; they map to real communication roles that components will rely on throughout the system.

- **Primary colors**: Main brand colors used for key actions and emphasis
- **Secondary colors**: Supporting colors for variety and hierarchy
- **Semantic colors**: Colors with specific meanings
  - Success (typically green tones)
  - Error/Danger (typically red tones)
  - Warning (typically yellow/orange tones)
  - Info (typically blue tones)
- **Neutral colors**: Grayscale for text, backgrounds, borders, and dividers
- **State colors**: Focus indicators, hover states, active states

**Considerations:**

- Ensure sufficient contrast ratios for accessibility (WCAG 2.2 AA minimum: 4.5:1 for normal text, 3:1 for large text and UI components; Campbell et al., 2023, SC 1.4.3, 1.4.11)
- Test colors in both light and dark modes if applicable
- Consider color blindness scenarios (don't rely on color alone to convey information)

#### Light Mode and Dark Mode {-}

Supporting both light and dark color schemes is no longer optional for a serious web UI system — it's an expectation. System-level dark mode preferences are now standard across macOS, Windows, iOS, and Android, and users notice when an application ignores them. Beyond preference, dark mode has real accessibility implications: many users with light sensitivity, migraines, or visual impairments rely on it. Others simply spend long hours in low-light environments where a bright white interface causes genuine discomfort. Designing for both modes from the start is significantly easier than retrofitting dark mode onto a system built only for light — and the token-based approach described in this section is what makes it tractable.

**Approach to Theming**

*Semantic Color Tokens*

Instead of hardcoding specific color values, use semantic naming that can adapt to themes:

- `color-background` (white in light, dark gray in dark)
- `color-text-primary` (near-black in light, near-white in dark)
- `color-text-secondary` (gray in light, light gray in dark)
- `color-surface` (for cards/panels, adapts to theme)
- `color-border` (subtle in light, more prominent in dark)

*Design Considerations for Dark Mode*

- **Not just inverted colors**: Dark mode isn't simply inverting light mode — it requires careful adjustment
- **Reduced contrast**: Pure white (#FFFFFF) on pure black (#000000) causes eye strain; use off-white (#E0E0E0) on dark gray (#121212)
- **Elevated surfaces**: In dark mode, elevated surfaces (cards, modals) should be *lighter* than the background, not darker
- **Color saturation**: Reduce color saturation in dark mode for better readability (bright colors are harsh on dark backgrounds)
- **Shadows**: Shadows work differently in dark mode; consider using lighter borders or subtle glows instead

*Web Implementation Strategies*

1. **CSS Custom Properties**: Define theme tokens that change based on a `data-theme` attribute or a `.dark` class on the root element
2. **Preference detection**: Respect system preference with the `prefers-color-scheme` media query as the default
3. **User toggle**: Allow users to override the system preference via a theme switcher control
4. **Persistence**: Remember the user's theme choice across sessions (localStorage or a user profile setting)

*Testing Dark Mode*

- Test all components in both themes
- Verify contrast ratios in both modes
- Ensure images and icons work in both modes (some may need theme-specific versions)
- Check that focus indicators remain visible in both themes
- Test with actual users in different lighting conditions

*Useful Resources*

- Material Design Dark Theme guidelines (Google LLC, n.d.)
- Apple Human Interface Guidelines — Dark Mode (Apple Inc., n.d.)
- WCAG 2.2 contrast ratio requirements (Campbell et al., 2023)

#### Typography Scale {-}

Typography is the invisible infrastructure of readability. Users don't notice a good type system — they just find the interface easy to read, scan, and navigate. They notice a bad one immediately, even if they can't articulate why. A type scale isn't just a list of font sizes; it's a set of relationships that create visual rhythm and hierarchy throughout the entire interface. Defined once as tokens, these relationships apply consistently to every heading, paragraph, label, and code snippet across the entire product.

- **Font families**: Primary (body text), secondary (headings), monospace (code)
- **Font sizes**: Defined scale using CSS units (e.g., 12px, 14px, 16px, 20px, 24px, 32px, 48px)
- **Font weights**: Available weights (e.g., 400-regular, 500-medium, 600-semibold, 700-bold)
- **Line heights**: Corresponding line heights for each size (typically 1.2–1.8)
- **Letter spacing**: Adjustments for different sizes or use cases

**Considerations**

- Base font size should be at least 16px for body text to ensure readability at default browser zoom
- Ensure text remains readable at different browser zoom levels (up to 200% per WCAG)
- Consider font loading performance — each weight and style variant is a separate network request

#### Spacing System {-}

Spacing is one of those things that's nearly invisible when done well and immediately obvious when done poorly. Inconsistent spacing — elements too close together, breathing room that varies unpredictably from component to component — makes an interface feel unfinished even when the individual elements are well-designed. A spacing system solves this by replacing arbitrary pixel decisions with a small set of named increments derived from a single base unit. Once defined, every gap, padding value, and margin in the system comes from that scale. The result is visual rhythm that holds together across the entire UI without anyone having to consciously enforce it.

- **Base unit**: Foundation for all spacing (commonly 4px or 8px)
- **Scale**: Consistent increments based on the base unit (e.g., 4, 8, 12, 16, 24, 32, 48, 64px)
- **Usage categories**:
  - Gaps: Space between related elements
  - Padding: Space inside containers
  - Margins: Space outside components

**Considerations**

- Touch targets should be at least 44×44px (Apple Inc., n.d.) or 48×48dp (Google LLC, n.d.) for accessibility
- Maintain consistent rhythm and alignment across the interface

#### Border Radius {-}

Border radius is a small decision that has a surprisingly large impact on the personality of a UI. Tight corners read as formal and precise; generous rounding reads as friendly and approachable. Neither is inherently better — but inconsistency between them is always a problem. A button with 4px corners next to a card with 12px corners next to a modal with 8px corners feels like it was assembled from three different design systems. Defining a small set of radius values upfront and applying them by role — not by component — keeps the system coherent.

- **Values**: Defined set of border radius values (e.g., 0, 2px, 4px, 8px, 16px, full/circle)
- **Usage**: Small (buttons, inputs), medium (cards), large (modals), full (pills, avatars)

#### Shadow/Elevation Levels {-}

Shadows do more than add visual depth — they communicate hierarchy and interactivity. An element with a shadow sits above the page; it demands attention. A modal carries more shadow than a card because it's operating at a higher level of the interface. When shadows are applied consistently by elevation rather than by whim, users develop an intuitive sense of the interface's layer structure without ever consciously thinking about it. Define your shadow levels once, assign them to elevation roles, and every component that uses them inherits a shared spatial language.

- **Levels**: Graduated shadow system to indicate elevation (e.g., level 1–5)
- **Usage**: Subtle (cards) to prominent (modals, dropdowns)
- **Consistency**: Same elevation = same shadow across all components

#### Breakpoints {-}

Every component in this specification will be used across a range of screen sizes, from narrow mobile viewports to wide desktop displays. Breakpoints are the points at which the layout and behavior of components adapt to available space. Rather than treating responsive behavior as a component-by-component problem, defining breakpoints as named system tokens — mobile, tablet, desktop — creates a shared vocabulary that keeps responsive decisions consistent. A component that collapses at "mobile" width collapses at the same pixel value as every other component that does the same, because they're all referencing the same token.

- **Mobile**: Small screens (e.g., < 640px)
- **Tablet**: Medium screens (e.g., 640px–1024px)
- **Desktop**: Large screens (e.g., > 1024px)
- **Additional**: Extra-large, or custom breakpoints as needed

**Considerations**

- Test components at breakpoint boundaries
- Design mobile-first, then progressively enhance for larger screens
- Ensure touch targets remain adequate at all viewport sizes

#### Transition/Animation Durations {-}

Motion in a UI isn't decoration — it's communication. A transition that's too fast feels abrupt; one that's too slow feels sluggish; one that's inconsistent between components feels broken. Defining a small set of named duration values — fast, normal, slow — and assigning them to specific types of interactions creates a motion language that users feel even if they don't consciously register it. Hover feedback is always fast. Modal entrances are always deliberate. State changes are always in the middle. Consistency in timing is what separates an interface that feels polished from one that just happens to have animations.

- **Fast**: Quick feedback (e.g., 100–150ms) for hovers, focus states
- **Normal**: Standard transitions (e.g., 200–300ms) for most UI state changes
- **Slow**: Deliberate animations (e.g., 400–500ms) for major layout or overlay changes
- **Easing**: Consistent CSS easing functions (ease-in, ease-out, ease-in-out, or custom cubic-bezier)

**Considerations**

- Always respect the `prefers-reduced-motion` media query — provide instant or minimal transitions for users who opt out of motion
- Animations should enhance, not impede, user interaction


## Interaction Principles

Interaction principles are the behavioral commitments that a UI system makes to its users. They answer a fundamental question that every component must resolve dozens of times during implementation: *when something happens, what should the component do?* Without explicit principles, these decisions get made ad hoc — sometimes consistently, often not — and the result is an interface that feels unpredictable, because it is.

The six principles below are adapted from Nielsen's 10 Usability Heuristics (Nielsen, 1994), one of the most empirically grounded frameworks in interaction design, and translated to the specific concerns of component-level behavior. They are not guidelines to apply when convenient — they are constraints to satisfy in every component, in every state, for every user. A component that violates these principles isn't just inconsistent; it's failing the people who depend on it.

Treating these as first-class requirements rather than aspirational guidelines changes how component development works in practice. It means that "does this provide clear feedback?" is a test condition, not a design suggestion. It means that "does this respect user control?" is a review criterion, not a preference. The Test Scenarios in the Component Catalog reflect this — they are written specifically to verify that each principle is upheld for each component.

**1. Provide Clear Feedback**

- Every user action should have an immediate, visible response
- Loading states should be indicated clearly
- Success and error states should be distinguishable
- Changes should be perceivable (visual, and where appropriate, announced to screen readers)

**2. Maintain Consistent State Representation**

- The same state should look the same across all components
- Focus states should be visually consistent
- Error states should follow the same pattern
- Disabled components should be clearly distinguishable from enabled ones

**3. Respect User Control**

- Users should be able to dismiss, cancel, or undo actions when appropriate
- No unexpected behavior (e.g., auto-submit, sudden navigation)
- Confirmations for destructive actions
- The Escape key should close overlays, modals, and dropdowns

**4. Progressive Disclosure**

- Show complexity only when needed
- Start simple, reveal advanced features on demand
- Don't overwhelm users with all options at once
- Provide sensible defaults

**5. Preserve User Input**

- Don't lose user data unexpectedly
- Warn before discarding unsaved changes
- Maintain form state when appropriate

**6. Use Motion Purposefully**

- Animations should communicate meaning and guide attention, not serve as decoration
- Purposeful motion examples:
  - Slide-in from right suggests forward progression or new content
  - Slide-out to left suggests backward navigation or dismissal
  - Fade-in suggests appearance or reveal
  - Shake/wiggle suggests error or rejection
  - Scale-up suggests emphasis or selection
  - Collapse/expand shows relationship between summary and detail
- Avoid gratuitous motion: Every animation should have a purpose (draw attention, show relationship, indicate state change)
- Respect user preferences: Always honor `prefers-reduced-motion` for users who find motion distracting or disorienting
- Keep it subtle: Animations should enhance understanding, not slow down interaction


## Consistency Patterns

One of the quieter benefits of a well-built component system is that developers stop making micro-decisions. Not because the decisions don't matter — they do — but because they've already been made, once, and encoded into patterns that apply everywhere. When every form input uses the same prop name for its error state, you don't have to look it up. When every interactive element responds to focus the same way, you don't have to test it separately. When every component that can be disabled looks disabled in the same way, users build accurate mental models without extra effort.
The patterns below are the shared conventions that make this possible. They aren't constraints for their own sake — they're the accumulated decisions that prevent a system from fragmenting into a collection of individually reasonable but collectively inconsistent components. Adopt them early, and they pay for themselves every time a new component is built or a new developer joins the team.

**State Naming Conventions**

Use consistent naming for common states across all components:

- `isDisabled` / `disabled`: Component cannot be interacted with
- `isLoading` / `loading`: Component is performing an async action
- `hasError` / `error`: Component is in an error state
- `isRequired` / `required`: Input is mandatory
- `isReadOnly` / `readOnly`: Value is visible but not editable
- `isActive` / `active`: Component is currently selected or in use

**Common Props/Parameters**

Similar components should accept similar parameters:

- All form inputs: `value`, `onChange`, `onBlur`, `onFocus`, `disabled`, `required`
- All interactive elements: `onClick`, `disabled`, `aria-label`
- All components with children: `children` or `content`

**Visual Feedback Patterns**

- Focus: Same focus indicator style across all interactive elements (outline, ring, or border change)
- Hover: Consistent hover behavior (color shift, opacity change, or elevation increase)
- Error: Same visual treatment everywhere (border color, icon, message position)
- Success: Same visual treatment across all components
- Disabled: Consistent reduced opacity or muted color to indicate non-interactive state

**Accessibility Patterns**

Accessibility is not a feature to be added at the end — it's a dimension of correctness that every component either satisfies or fails. A component that a keyboard user can't operate isn't less accessible; it's broken for that user. A component that a screen reader misrepresents isn't imperfect; it's unusable for the people who depend on that technology. This framing matters because it changes how accessibility requirements are prioritized: not as a secondary checklist, but as part of the definition of done.

The accessibility requirements throughout this specification follow WCAG 2.2 (Campbell et al., 2023) and the ARIA Authoring Practices Guide (W3C WAI, n.d.) — the two primary standards that define what accessible web components must do. These standards exist because access to information and functionality matters, and because the web's strength is its universality. A UI system that works only for users without disabilities, or only for users with a mouse, is not meeting the bar this specification sets.

The patterns below summarize the non-negotiable baseline that applies to every component in the Component Catalog. They are a starting point, not a ceiling:

- All interactive elements are keyboard accessible — every action reachable by mouse must be reachable by keyboard
- Focus order follows logical reading order, matching the visual and DOM structure
- Labels are programmatically associated with their inputs via `for`/`id` or `aria-labelledby` — never implied by visual proximity alone
- ARIA roles, states, and properties are used correctly and consistently — not added speculatively, but applied according to the patterns defined in the ARIA APG
- Color is never the only means of conveying information — icons, text labels, or patterns always accompany color-based signals so that color-blind users receive the same information

