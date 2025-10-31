# Design System Implementation Plan

**Non-Negotiable Developer-Grade Interface**

Built on Primer design principles, WCAG AA compliance, and proven patterns from GitHub, Material Design, and Nielsen Norman Group research.

---

## ✅ IMPLEMENTATION STATUS

**Foundation:** Complete
- Design tokens: `src/styles/design-tokens.css` ✅
- Tailwind config with HSL alpha-value support ✅
- Button, Badge, Card components migrated ✅
- Typography and spacing system ✅

**Next Priority:**
1. Input component (#1)
2. Select component (#2)
3. Table component (#3)
4. Screen migrations (Payments, Jobs, Agent Test, Settings)

---

## Quick Reference

### Token Usage

```tsx
/* Backgrounds */
<div className="bg-background" />       /* Page background */
<div className="bg-surface" />          /* Cards, panels */
<div className="bg-muted/20" />         /* Subtle highlights */

/* Text */
<p className="text-text" />             /* Primary text */
<p className="text-muted-foreground" /> /* Secondary text */

/* Borders */
<div className="border border-border" /> /* Standard 1px border */

/* Status Colors */
<Badge variant="success" />   /* Completed */
<Badge variant="danger" />    /* Failed */
<Badge variant="warning" />   /* Caution */
<Badge variant="primary" />   /* In progress */
```

### Common Replacements

| ❌ Old | ✅ New |
|--------|--------|
| `text-white` | `text-text` |
| `bg-gray-900` | `bg-background` |
| `bg-gray-800` | `bg-surface` |
| `border-white` | `border-border` |
| `p-5` | `p-4` (8px grid) |
| `gap-7` | `gap-6` (8px grid) |

---

## Implementation Phases

### Phase 1: Core Components ✅ → 🚧

- [x] Button with proper states (hover +6%, active +10%, disabled 40% opacity)
- [x] Badge mapped to semantic tokens (no gradients)
- [x] Card with 8px grid spacing (header p-4, content p-4, footer p-3)
- [ ] Input (h-10, bg-input, border-border, 2px focus ring)
- [ ] Select (same as Input)
- [ ] Table (row h-12, header text-text/80, no uppercase, hover bg-accent/50)

### Phase 2: Find & Replace

```bash
# Text colors
text-white → text-text
text-gray-400 → text-muted-foreground

# Backgrounds
bg-gray-900 → bg-background
bg-gray-800 → bg-surface

# Borders
border-white → border-border
border-gray-700 → border-border
```

### Phase 3: Screen Migrations

1. **Payments Dashboard:** 3-column KPI grid, export actions in header, table row h-12
2. **Jobs List:** Collapsible filters, badge status, progress bar with border track
3. **Agent Test:** 2-column layout (config left, output right), monospace font
4. **Settings:** Grouped sections (Profile, Notifications, Billing), inputs h-10
5. **Landing Hero:** Keep gradients, remove glow, one primary CTA

---

## Component Standards

### Button

```tsx
<Button>Primary (bg-primary)</Button>
<Button variant="secondary">Surface + border</Button>
<Button variant="destructive">Danger</Button>
<Button variant="ghost">Transparent</Button>
<Button variant="outline">Border only</Button>
<Button variant="link">Text only</Button>
```

### Badge

```tsx
<Badge variant="default">Pending (muted)</Badge>
<Badge variant="success">Completed (success)</Badge>
<Badge variant="danger">Failed (danger)</Badge>
<Badge variant="primary">In Progress (primary outline)</Badge>
<Badge variant="warning">Warning (warning)</Badge>
```

### Card

```tsx
<Card className="border-border">
  <CardHeader className="p-4">
    <CardTitle>Title (20px)</CardTitle>
    <CardDescription>Subtitle</CardDescription>
  </CardHeader>
  <CardContent className="p-4">Content</CardContent>
  <CardFooter className="p-3">Footer</CardFooter>
</Card>
```

---

## Design Principles

### 1. Color System

- **No pure white/black:** Use softer neutrals (--text: 220 20% 88%)
- **HSL without commas:** Enables `<alpha-value>` pattern (bg-primary/20)
- **WCAG AA compliance:** Normal text 4.5:1, large text 3:1, UI 3:1 minimum
- **Two themes:** Dark (primary) and light with same semantic tokens

### 2. Typography

- **Font:** System UI stack (no custom fonts)
- **Scale:** 12, 14, 16 (base), 18, 20, 24, 30, 36 (hero only)
- **Line height:** 1.55 (body), 1.35 (headings)
- **Hero limit:** 36px headlines only on landing page

### 3. Spacing

- **8px grid:** All spacing snaps to multiples of 8
- **High density:** Data tables and code only (still on grid)
- **Consistent:** p-4 (32px), gap-2 (16px), mb-6 (48px)

### 4. Layout

- **Sidebar:** 264px fixed width
- **Content:** max-width 1280px (marketing), fluid (app tables)
- **Elevation:** By contrast, not drop shadows
- **Borders:** 1px border-border, no white/glow

### 5. Hierarchy

**Page structure (every app page):**
1. Breadcrumb (left-aligned)
2. Page title + description
3. Primary action (right side, one only)
4. Filter panel (collapsible, default closed)
5. Content module
6. Pagination

---

## Accessibility

### Focus Visibility (WCAG Required)

```tsx
className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
```

- 2px ring in primary color (3:1 contrast)
- Offset 2px for clarity
- Every interactive element

### Contrast Ratios (Verified)

- --text on --bg: 13.5:1 ✅
- --text-muted on --bg: 5.8:1 ✅
- --border on --bg: 3.1:1 ✅
- --success: 4.6:1 ✅
- --warning: 6.1:1 ✅
- --danger: 5.2:1 ✅

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## CI/CD Integration (Planned)

### Contrast Checks

```bash
npm install --save-dev @adobe/leonardo-contrast-colors
npm run check-contrast  # Fails if < 4.5:1 for text, < 3:1 for UI
```

### ESLint Rules

```bash
npm install --save-dev eslint-plugin-tailwindcss
```

Block patterns:
- `bg-gray-*` (use tokens)
- `text-white` (use `text-text`)
- `border-white` (use `border-border`)
- Hex colors in className

---

## Resources

1. [Primer Design System](https://primer.style/) - GitHub's system at scale
2. [GitHub Contrast Updates](https://github.blog/changelog/2023-03-27-light-and-dark-theme-color-contrast-improvements/)
3. [WCAG 2.1](https://www.w3.org/TR/WCAG21/) - Contrast requirements
4. [Tailwind CSS Variables](https://tailwindcss.com/docs/customizing-colors) - Alpha-value pattern
5. [WebAIM](https://webaim.org/resources/contrastchecker/) - Contrast checker
6. [NN/g Hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)
7. [Material Design](https://m2.material.io/design/layout/understanding-layout.html) - 8px grid

---

**Last Updated:** 2025-10-31  
**See Also:** `docs/DESIGN_SYSTEM_GUIDE.md` for detailed examples
