# Design System Implementation Guide

## Overview

Developer-grade design system with strict tokens, WCAG AA compliance, and systematic component architecture modeled after GitHub's Primer.

**Status:** ✅ Foundation Complete
- Design tokens in `src/styles/design-tokens.css`
- Tailwind configured with HSL alpha-value support
- Button component updated
- Ready for component migration

---

## Quick Reference

### Tokens
```css
--bg, --surface, --text, --text-muted, --border
--primary, --secondary, --success, --warning, --danger
--card, --popover, --muted, --accent
```

### Usage
```tsx
// ✅ CORRECT
<div className="bg-surface text-text border-border" />
<Button className="bg-primary text-primary-foreground" />

// ❌ WRONG
<div className="bg-gray-800 text-white border-gray-700" />
```

### Contrast Ratios (WCAG AA)
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- UI borders/icons: 3:1 minimum

---

## Implementation Details

See full documentation in `DESIGN_SYSTEM_GUIDE.md` for:
- Complete token reference
- Component standards
- Typography system
- Spacing (8px grid)
- Layout patterns
- Migration checklist
