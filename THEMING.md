# Codebase Audiobook – Theming Guide

Our design system is token-first. Tailwind consumes tokens declared in `src/index.css` via `@theme`, while the concrete dark/light values live in `src/styles/design-tokens.css`. Use semantic utilities (`bg-surface`, `text-muted`, `border-default`, etc.) everywhere—never fall back to raw Tailwind gray/brand palettes.

## Semantic Roles

| Role            | Utility examples                                    | Purpose                                 |
|-----------------|------------------------------------------------------|-----------------------------------------|
| Backgrounds     | `bg-background`, `bg-surface`, `bg-surface-subtle`    | Page, card, and inset surfaces          |
| Text            | `text-foreground`, `text-muted`                      | Primary/secondary copy                  |
| Borders & rings | `border-default`, `focus-ring`                       | Structural lines + focus states         |
| Primary action  | `bg-primary`, `text-primary`, `ring-primary`         | High emphasis actions & highlights      |
| Secondary       | `bg-secondary`, `text-secondary`                     | Secondary accents                       |
| Status          | `bg-success`, `bg-warning`, `bg-danger`              | Success / warning / failure indicators  |
| Sidebar         | `bg-sidebar`, `text-sidebar-foreground`              | Navigation shell                        |

## Layout & Spacing

Tokens expose named sizes to avoid arbitrary values:

```tsx
<div className="w-sidebar-expanded border-default" />
<section className="section-spacing">
  <div className="max-w-content px-4">…</div>
</section>
```

For dialog and viewer heights use `max-h-pane-md` or `max-h-pane-lg` (defined in `src/index.css`). Avoid hard-coded pixel heights.

## Elevation & Motion

- Use `elevation-flat` or `elevation-raised` for shadows—no custom glow strings.
- Apply `transition-standard` alongside Tailwind transition utilities for consistent duration/easing.

## Typography

Base heading/body sizes are set in `src/index.css`. Use semantic utilities (`text-3xl`, `font-semibold`, etc.) in combination with tokens—avoid gradients or manual pixel values for marketing copy.

## Dark Mode

Dark mode is handled via a custom `dark:` variant defined in CSS. Theme overrides live in `src/styles/design-tokens.css`. No JS configuration is required—when `.dark` or `[data-theme="dark"]` is present the token values swap automatically.

## Checklist When Updating Screens

- [ ] Replace palette classes (e.g., `bg-gray-900`, `text-blue-500`) with semantic token utilities.
- [ ] Ensure borders use `border-default` and interactive states use `focus-ring`.
- [ ] Swap arbitrary spacing/widths (`w-[264px]`, `h-[400px]`) for named tokens (`w-sidebar-expanded`, `max-h-pane-lg`, `section-spacing`).
- [ ] Remove gradient or glow text in primary actions/headings.
- [ ] Use `Button`, `Input`, `Textarea`, and other primitives instead of custom class stacks.
