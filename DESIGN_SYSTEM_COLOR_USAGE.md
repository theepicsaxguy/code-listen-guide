# Modern Developer-Tool Dark UI Color System

## Specification Compliance

This document outlines the color system usage patterns aligned with the Modern Developer-Tool Dark UI specification.

## Core Surface Palette (Neutral Foundation)

### Layer Hierarchy

1. **Base Background** (`bg-background`)
   - Darkest deep grey: `hsl(0 0% 4%)`
   - Use for: Full-screen, root backgrounds
   - Example: `div className="min-h-screen bg-background"`

2. **Elevated Surface** (`bg-surface`)
   - Slightly lighter grey: `hsl(240 5% 10%)`
   - Use for: Cards, panels, elevated containers
   - Example: `<Card className="bg-surface">` or `div className="bg-surface p-6"`

3. **Active Surface** (`bg-surface-active` or `bg-surface-secondary`)
   - Lightest grey: `hsl(240 5% 16%)`
   - Use for: Highlighted sections, hover states, active items
   - Example: `div className="hover:bg-surface-secondary"`

### Typography on Surfaces

- **Headings**: `text-foreground` (very light, highest contrast)
  - Example: `<h1 className="text-5xl font-bold text-foreground">`

- **Body Text**: `text-foreground-muted` or `text-muted-foreground` (light, readable)
  - Example: `<p className="text-base text-muted-foreground">`

- **Metadata**: `text-muted` (muted but readable, often uppercase/tracking-wide)
  - Example: `<span className="text-xs text-muted uppercase tracking-wide">`

### Separation Rules

- **No borders** for structural separation
- Use **subtle luminance shifts** (3-5% difference)
- Use **soft shadows** for depth: `shadow-xl shadow-primary/10`
- Gradient accents for ambient depth: `bg-gradient-to-br from-primary/5 via-transparent`

## Accent Palette (Chromatic Highlights)

### 1. Brand / Primary Accent

**Color**: `hsl(188 94% 43%)` (cyan-500)

**Usage Rules**:
- Max **one per major layout row**
- Reserved for: Hero CTAs, active states, key highlights
- Use sparingly to maintain hierarchy

**Examples**:
```tsx
// Primary button
<Button className="bg-primary text-primary-foreground">Get Started</Button>

// Active state glow
<div className="shadow-xl shadow-primary/10">Card</div>

// Accent line/icon
<Icon className="text-primary" />
```

### 2. Secondary Accent

**Color**: `hsl(260 90% 70%)` (purple)

**Usage Rules**:
- **One or two per card or section**
- For: Links, less-dominant buttons, tags, interactive hover states
- Provides "alive" feel without dominating

**Examples**:
```tsx
// Tag background
<Badge variant="secondary" className="bg-secondary/5 text-secondary">Tag</Badge>

// Link
<a className="text-secondary hover:text-secondary-hover">Link</a>

// Icon background
<div className="bg-secondary/10 text-secondary">Icon</div>
```

### 3. Semantic Accents

**Colors**:
- Success: `hsl(142 76% 36%)` (green-400)
- Warning: `hsl(38 92% 50%)` (amber-400)
- Error/Danger: `hsl(0 84% 60%)` (red-400)
- Info: `hsl(217 91% 60%)` (blue-400)
- Pending: `hsl(258 90% 66%)` (purple-400)

**Usage Rules**:
- Only where **state needs presentation** (badges, indicators, alerts)
- Apply as: **text + low-alpha background (5-10% opacity)**
- Example: `bg-success/5 text-success` (not full saturation)

**Examples**:
```tsx
// Status badge
<Badge className="bg-success/5 text-success">Completed</Badge>
<Badge className="bg-danger/5 text-danger">Failed</Badge>
<Badge className="bg-pending/5 text-pending">Pending</Badge>

// Alert
<div className="bg-warning/5 text-warning border border-warning/20">Warning</div>
```

## Interaction & Depth Effects

### Hover / Active States

- **Surfaces**: Use brand accent as **glow/shadow**, not full saturate fill
  - Example: `hover:shadow-xl hover:shadow-primary/10`

- **Interactive elements**: Subtle background shift
  - Example: `hover:bg-surface-secondary`

- **Brand accent buttons**: Full color on hover
  - Example: `hover:bg-primary/90`

### Background Gradients

- **Ambient depth**: Subtle radial/linear gradients at **3-8% opacity**
- Example: `bg-gradient-to-br from-primary/5 via-transparent to-transparent`
- Applied as background layer, not main surface

### Motion

- **Sparse usage**: Tiny scale or glow changes on hover
- Example: `transition-standard hover:shadow-xl hover:shadow-primary/10`

## Usage Guidelines

### Screen Layout Hierarchy

```
Background (base)
  └─ Elevated Surface (cards)
      └─ Active Surface (hover states)
          └─ Card layers (nested content)
```

### Accent Usage per Screen

1. **Brand accent**: Maximum one per major layout row
2. **Secondary accent**: One or two per card/section
3. **Semantic colors**: Only where state needs presentation

### Typography Scale

- **Headings**: Large, bright, high contrast
  - H1: `text-5xl font-bold text-foreground`
  - H2: `text-3xl font-bold text-foreground`
  
- **Body**: Moderate size, slightly muted contrast
  - Body: `text-base leading-relaxed text-muted-foreground`
  
- **Metadata**: Small, muted, uppercase/tracking-wide
  - Label: `text-xs font-medium text-muted uppercase tracking-wide`

### Spacing Rhythm

- **Large sections**: `py-24` (96px)
- **Normal containers**: `p-6` (24px)
- **Tight groups**: `gap-2` or `gap-4` (8-16px)
- **Card padding**: `p-6` with nested `p-4`

### Accessibility

- All text meets WCAG AA contrast standards in dark mode
- Interactive elements have clear focus states
- Semantic colors have sufficient contrast when used as text

## Tailwind v4 Implementation

All colors are defined as CSS variables in `@theme`:
- Native Tailwind v4 CSS-first approach
- Token-driven design system
- No legacy plugin dependencies

## Example Component Patterns

### Card with Hover
```tsx
<Card className="bg-surface hover:shadow-xl hover:shadow-primary/10 transition-standard">
  <CardHeader>
    <CardTitle className="text-xl font-semibold text-foreground">Title</CardTitle>
    <CardDescription className="text-sm text-muted-foreground">Description</CardDescription>
  </CardHeader>
</Card>
```

### Status Badge
```tsx
<Badge className="bg-success/5 text-success">Completed</Badge>
```

### Primary CTA
```tsx
<Button className="bg-primary text-primary-foreground hover:bg-primary/90">
  Get Started
</Button>
```

### Secondary Interactive
```tsx
<Button variant="outline" className="border-border text-foreground hover:bg-surface-secondary">
  Secondary Action
</Button>
```

## Goals Achieved

✅ Neutral-first surface system  
✅ Multiple accent roles (brand + secondary + semantic)  
✅ Alive feel without monotony  
✅ Professional developer tool aesthetics  
✅ Tailwind v4 CSS-token driven  
✅ No borders, shadows and luminance shifts for depth  
✅ Modern, clean, readable interface
