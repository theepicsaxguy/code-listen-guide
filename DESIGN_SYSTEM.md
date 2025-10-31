# Design System Implementation Guide

## Overview

Developer-grade design system with strict tokens, WCAG AA compliance, and systematic component architecture modeled after GitHub's Primer.

**Status:** ✅ Foundation Complete
- Design tokens defined in `src/index.css` via `@theme`
- Runtime values managed in `src/styles/design-tokens.css`
- Tailwind config reduced to container + plugins (CSS-first setup)
- Core primitives (Button, Input, Card, Sidebar) aligned to token scale

---

## Quick Reference

### Tokens
```css
--color-background, --color-surface, --color-surface-subtle
--color-foreground, --color-muted, --color-border, --color-ring
--color-primary, --color-secondary, --color-success, --color-warning, --color-danger
--size-sidebar-expanded, --size-sidebar-collapsed, --size-content-max
--spacing-1 … --spacing-16, --spacing-section
--shadow-flat, --shadow-raised, --shadow-overlay
```

### Usage
```tsx
// ✅ CORRECT
<div className="rounded-lg border-default bg-surface text-foreground" />
<Button className="transition-standard" />

// ❌ WRONG
<div className="bg-gray-800 text-white border-gray-700" />
<div className="shadow-[0_0_10px_rgba(0,0,0,0.5)]" />
```

### Contrast Ratios (WCAG AA)
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- UI borders/icons: 3:1 minimum

---

## Implementation Details

All design tokens are defined in `src/index.css` via `@theme`:
- Complete token reference
- Component standards
- Typography system
- Spacing (8px grid)
- Layout patterns
- Migration checklist
