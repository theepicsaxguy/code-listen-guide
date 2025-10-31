# Design System Implementation Guide

Complete reference for the developer-grade design system.

## Table of Contents
1. [Architecture](#architecture)
2. [Color System](#color-system)
3. [Components](#components)
4. [Typography](#typography)
5. [Spacing](#spacing)
6. [Layout Patterns](#layout-patterns)
7. [Migration Guide](#migration-guide)

---

## Architecture

### Single Source of Truth

```
design-tokens.css → tailwind.config.ts → Components
```

All colors use HSL without commas for Tailwind `<alpha-value>` support:

```css
/* ✅ CORRECT */
--primary: 222 100% 62%;
/* Usage: bg-primary/20 works */

/* ❌ WRONG */
--primary: hsl(222, 100%, 62%);
/* Opacity classes broken */
```

---

## Color System

### Base Tokens

**Dark Theme (Primary):**
```css
--bg: 220 15% 10%              /* Main background */
--surface: 220 15% 12%         /* Cards, panels */
--text: 220 20% 88%            /* Primary text (13.5:1) */
--text-muted: 220 10% 60%      /* Secondary text (5.8:1) */
--border: 220 15% 20%          /* Borders (3.1:1) */
```

**Light Theme:**
```css
--bg: 220 20% 98%
--surface: 220 25% 99%
--text: 220 25% 15%            /* Dark text (13.8:1) */
--text-muted: 220 15% 45%      /* Secondary (5.1:1) */
--border: 220 15% 88%          /* Light borders */
```

### Semantic Colors

All include base + foreground variants:

```css
--primary: 222 100% 62%        /* Calm blue */
--primary-foreground: 220 20% 98%

--secondary: 260 90% 70%       /* Subtle purple */
--success: 145 60% 45%         /* Green (4.6:1) */
--warning: 38 90% 60%          /* Orange (6.1:1) */
--danger: 0 70% 60%            /* Red (5.2:1) */
```

### Usage Examples

```tsx
/* Text colors */
<p className="text-text">Primary text</p>
<p className="text-muted-foreground">Secondary text</p>

/* Backgrounds */
<div className="bg-surface border border-border" />
<div className="bg-primary/20" /> {/* 20% opacity works */}

/* Semantic */
<Badge className="bg-success text-success-foreground">Done</Badge>
<Button className="bg-danger text-danger-foreground">Delete</Button>
```

---

## Components

### Button

**File:** `src/components/ui/button.tsx`

**Variants:**
- `default` - Primary (`bg-primary`)
- `secondary` - Surface with border
- `destructive` - Danger color
- `ghost` - Transparent
- `outline` - Border only
- `link` - Text only

**States:**
- Hover: `brightness-110` (+6%)
- Active: `brightness-125` (+10%)
- Disabled: `opacity-40` (preserves 4.5:1)
- Focus: `ring-2 ring-ring` (2px, 3:1)

**Sizes:**
```tsx
<Button>Default (40px)</Button>
<Button size="sm">Small (36px)</Button>
<Button size="lg">Large (44px)</Button>
<Button size="icon">Icon (40x40)</Button>
```

### Input (Specification)

```tsx
<Input
  className="h-10 bg-input border-border focus:ring-2 focus:ring-ring"
  placeholder="Text"
/>
```

**Requirements:**
- Height: 40px (matches button)
- Background: `bg-input`
- Border: `border-border` (1px, no shadows)
- Focus: 2px ring-primary

### Badge (Specification)

```tsx
<Badge variant="success">Completed</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="danger">Failed</Badge>
<Badge variant="default">In Progress</Badge>
```

**Requirements:**
- Map to semantic tokens
- Maintain 4.5:1 text contrast
- No neon/glow effects

### Card (Specification)

```tsx
<Card className="border-border">
  <CardHeader className="p-4">Title</CardHeader>
  <CardContent className="p-4">Content</CardContent>
  <CardFooter className="p-3">Footer</CardFooter>
</Card>
```

**Spacing:**
- Header: 16px (p-4)
- Body: 16px (p-4)
- Footer: 12px (p-3)
- Border: 1px `border-border`

### Table (Specification)

```tsx
<Table>
  <TableHeader>
    <TableRow className="h-12">
      <TableHead className="text-text/80">Column</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow className="h-12 hover:bg-accent/50">
      <TableCell>Data</TableCell>
      <TableCell className="text-muted-foreground text-sm">
        Secondary
      </TableCell>
    </TableRow>
  </TableBody>
</Table>
```

**Requirements:**
- Row height: 48px (h-12)
- Header: `text-text/80`, no uppercase
- Hover: `bg-accent/50`, not white border
- Zebra: `bg-surface` with alpha

---

## Typography

### Font Stacks

**Sans (Default):**
```css
ui-sans-serif, system-ui, -apple-system, ...
```

**Mono (Code):**
```css
ui-monospace, SFMono-Regular, ...
```

### Type Scale

```tsx
text-xs    /* 12px, lh 1.55 */
text-sm    /* 14px, lh 1.55 */
text-base  /* 16px, lh 1.55 - Body default */
text-lg    /* 18px, lh 1.55 */
text-xl    /* 20px, lh 1.35 - Headings */
text-2xl   /* 24px, lh 1.35 */
text-3xl   /* 30px, lh 1.35 */
text-4xl   /* 36px, lh 1.35 - Max for app UIs */
```

**Rule:** Headlines >36px **only on landing hero**.

### Heading Hierarchy

```tsx
<h1 className="text-4xl font-bold">Page Title (36px)</h1>
<h2 className="text-3xl font-bold">Section (30px)</h2>
<h3 className="text-2xl font-bold">Subsection (24px)</h3>
<h4 className="text-xl font-bold">Card Title (20px)</h4>
```

---

## Spacing

### 8px Grid

All spacing snaps to multiples of 8:

```tsx
p-1  /* 8px */
p-2  /* 16px */
p-3  /* 24px */
p-4  /* 32px */
p-5  /* 40px */
p-6  /* 48px */
p-8  /* 64px */
```

### Examples

```tsx
/* Card spacing */
<Card className="p-4" />     /* 32px all sides */

/* Grid gaps */
<div className="grid gap-4" /> /* 32px gap */
<div className="flex gap-2" /> /* 16px gap */

/* Section rhythm */
<section className="space-y-6"> /* 48px between items */
```

---

## Layout Patterns

### Application Shell

```tsx
<div className="flex h-screen">
  {/* Sidebar: 264px */}
  <aside className="w-[264px] bg-sidebar border-r border-sidebar-border">
    <Sidebar />
  </aside>
  
  {/* Main content */}
  <main className="flex-1 overflow-auto">
    <PageHeader />
    <div className="max-w-[1280px] mx-auto p-6">
      {/* Content */}
    </div>
  </main>
</div>
```

### Page Header

```tsx
<div className="border-b border-border pb-4 mb-6">
  <Breadcrumb className="mb-2" />
  <div className="flex items-center justify-between">
    <div>
      <h1 className="text-2xl font-bold">Title</h1>
      <p className="text-sm text-muted-foreground">Description</p>
    </div>
    <div className="flex gap-2">
      <Button variant="secondary">Secondary</Button>
      <Button>Primary</Button>
    </div>
  </div>
</div>
```

**Pattern:** Breadcrumb → Title + Desc → Actions (right)

### Sidebar Navigation

```tsx
<nav>
  {/* Regular item */}
  <a className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-sidebar-accent">
    <Icon className="w-5 h-5" />
    <span>Dashboard</span>
  </a>
  
  {/* Active item: 2px primary stripe + bg tint */}
  <a className="flex items-center gap-3 px-3 py-2 rounded-md bg-sidebar-accent border-l-2 border-primary">
    <Icon className="w-5 h-5 text-primary" />
    <span className="font-semibold">Jobs</span>
  </a>
</nav>
```

### Filter Panel (Collapsible)

```tsx
<Collapsible>
  <CollapsibleTrigger className="text-sm font-medium">
    <FilterIcon className="w-4 h-4" />
    Filters
  </CollapsibleTrigger>
  <CollapsibleContent className="mt-2 p-4 bg-muted rounded-md">
    {/* Controls */}
  </CollapsibleContent>
</Collapsible>
```

---

## Migration Guide

### Phase 1: Core Components ✅

- [x] Design tokens created
- [x] Tailwind config updated
- [x] Button migrated
- [ ] Input
- [ ] Badge
- [ ] Card
- [ ] Table

### Phase 2: Find and Replace

**Text Colors:**
```bash
# Find hardcoded white
grep -r "text-white" src/

# Replace with semantic token
text-white → text-text
text-gray-400 → text-muted-foreground
```

**Backgrounds:**
```bash
bg-gray-900 → bg-background
bg-gray-800 → bg-surface
bg-gray-700 → bg-muted
```

**Borders:**
```bash
border-white → border-border
border-gray-700 → border-border
```

### Phase 3: Spacing Alignment

Ensure all spacing uses 8px grid:

```tsx
/* ❌ BEFORE */
<div className="p-5 gap-7" />

/* ✅ AFTER */
<div className="p-4 gap-6" />  /* 32px, 48px */
```

### Phase 4: Remove Gradients from App UIs

Keep gradients **only in landing hero**:

```tsx
/* ❌ App UI - Remove */
className="bg-gradient-to-r from-purple-600 to-blue-500"

/* ✅ App UI - Use tokens */
className="bg-primary"

/* ✅ Landing hero - Keep gradients */
className="bg-gradient-to-r from-purple-600 to-blue-500"
```

### Phase 5: Accessibility Audit

```bash
# Add contrast checker (planned)
npm install --save-dev @adobe/leonardo-contrast-colors
npx leonardo check
```

---

## Common Patterns

### Status Badge Map

```tsx
const statusMap = {
  pending: "bg-muted text-muted-foreground",
  in_progress: "bg-primary/10 text-primary border border-primary/20",
  completed: "bg-success/10 text-success border border-success/20",
  failed: "bg-danger/10 text-danger border border-danger/20",
};

<Badge className={statusMap[status]}>{status}</Badge>
```

### KPI Card

```tsx
<Card className="border-border">
  <CardContent className="p-4">
    <div className="text-2xl font-bold text-text">{value}</div>
    <div className="text-sm text-muted-foreground">{label}</div>
  </CardContent>
</Card>
```

### Data Table Row

```tsx
<TableRow className="h-12 hover:bg-accent/30">
  <TableCell className="font-medium">{primary}</TableCell>
  <TableCell className="text-muted-foreground text-sm">
    {secondary}
  </TableCell>
  <TableCell className="text-right">
    <Button variant="ghost" size="sm">Action</Button>
  </TableCell>
</TableRow>
```

---

## Accessibility

### Focus Visibility

All interactive elements:

```tsx
className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
```

### Keyboard Navigation

- Tab reaches all buttons/links
- Escape closes modals/dropdowns
- Focus returns to trigger after close

### Reduced Motion

Respects `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Resources

- **Primer:** https://primer.style
- **WCAG 2.1:** https://www.w3.org/TR/WCAG21/
- **Tailwind Variables:** https://tailwindcss.com/docs/customizing-colors
- **Material Density:** https://m2.material.io/design/layout/applying-density.html
- **NN/g Hierarchy:** https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
