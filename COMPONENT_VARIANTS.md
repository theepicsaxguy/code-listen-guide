# Component Variants Documentation

This document defines the standardized variants, sizes, states, and density options for all UI components in the design system.

## Button Component

**Location:** `src/components/ui/button.tsx`

### Variants
- `default` - Primary action button (bg-primary)
- `secondary` - Secondary action (bg-surface with border)
- `danger` - Destructive actions (bg-danger)
- `ghost` - Transparent with hover state
- `link` - Text-only with underline
- `outline` - Border only, no background

### Sizes
- `default` - h-11 (44px) px-5
- `sm` - h-10 px-4 text-sm
- `lg` - h-12 px-6 text-base
- `icon` - h-11 w-11 (square, icon-only)

### States
- `hover` - Opacity/color change via hover:
  - default: `hover:bg-primary/90`
  - secondary: `hover:bg-accent`
  - danger: `hover:bg-danger/90`
- `active` - Pressed state: lighter opacity
- `disabled` - `disabled:opacity-40 disabled:pointer-events-none`
- `focus-visible` - 2px ring-ring with offset

### Border Radius
- All buttons: `rounded-control` (0.5rem)

## Card Component

**Location:** `src/components/ui/card.tsx`

### Variants
- Default card container

### Radius
- `rounded-card` (0.75rem)

### Elevation
- Uses elevation tokens: `elevation-flat`, `elevation-raised`, `elevation-overlay`
- No shadows - elevation by contrast only

## Input Component

**Location:** `src/components/ui/input.tsx`

### Size
- Fixed height: `h-11` (44px) for touch target compliance

### Radius
- `rounded-control` (0.5rem)

### States
- `focus-visible` - 2px ring-ring
- `disabled` - `disabled:opacity-50 disabled:cursor-not-allowed`

## Badge Component

**Location:** `src/components/ui/badge.tsx`

### Variants
- `default` - Muted (bg-muted/20)
- `success` - Success state (bg-success/10)
- `danger` - Error state (bg-danger/10)
- `primary` - Active state (bg-primary/10)
- `warning` - Warning state (bg-warning/10)
- `secondary` - Accent state (bg-secondary/10)
- `outline` - Border only

### Radius
- `rounded-control` (0.5rem)

## Select Component

**Location:** `src/components/ui/select.tsx`

### Size
- Trigger: `h-11` (44px)

### Radius
- Trigger: `rounded-control`
- Content: `rounded-card`
- Items: `rounded-control`

### Elevation
- Content: `elevation-raised`

## Dialog Component

**Location:** `src/components/ui/dialog.tsx`

### Radius
- Content: `rounded-card`

### Elevation
- Content: `elevation-overlay`

## Alert Component

**Location:** `src/components/ui/alert.tsx`

### Variants
- `default` - Standard alert
- `danger` - Error alert (border-danger/40)

### Radius
- `rounded-card` (0.75rem)

## Tabs Component

**Location:** `src/components/ui/tabs.tsx`

### Radius
- List: `rounded-card`
- Trigger: `rounded-control`

## Toast Component

**Location:** `src/components/ui/toast.tsx`

### Variants
- `default` - Standard toast
- `danger` - Error toast

### Radius
- Container: `rounded-card`
- Action button: `rounded-control`
- Close button: `rounded-control`

### Elevation
- Container: `elevation-raised`

## Icon Sizing

Standardized icon sizes (defined in @theme):
- `--size-icon-xs` - 0.75rem (12px)
- `--size-icon-sm` - 1rem (16px)
- `--size-icon-md` - 1.25rem (20px)
- `--size-icon-lg` - 1.5rem (24px)
- `--size-icon-xl` - 2rem (32px)

### Usage in components
- Button icons: `size-5` (1.25rem)
- Navigation icons: `h-4 w-4` or `h-5 w-5`
- Hero/large icons: `h-8 w-8` or `h-12 w-12`

## Spacing Scale

Base 4px spacing scale (all values in rem):
- `--spacing-0` - 0px
- `--spacing-1` - 0.25rem (4px)
- `--spacing-2` - 0.5rem (8px)
- `--spacing-3` - 0.75rem (12px)
- `--spacing-4` - 1rem (16px)
- `--spacing-5` - 1.25rem (20px)
- `--spacing-6` - 1.5rem (24px)
- `--spacing-8` - 2rem (32px)
- `--spacing-10` - 2.5rem (40px)
- `--spacing-12` - 3rem (48px)
- `--spacing-16` - 4rem (64px)
- `--spacing-20` - 5rem (80px)
- `--spacing-24` - 6rem (96px)

**Rule:** Use spacing scale values only. No arbitrary values like `p-[17px]` or `gap-[23px]`.

## Content Widths

Standardized content width tokens:
- `--size-content-narrow` - 42rem (672px)
- `--size-content-default` - 64rem (1024px)
- `--size-content-wide` - 80rem (1280px)
- `--size-content-max` - 80rem (1280px)

**Usage:**
- `max-w-content-default` - Standard page content
- `max-w-content-wide` - Wide layouts (admin tables)
- `max-w-content-narrow` - Narrow dialogs/forms

## Elevation Tokens

Three unified elevation levels:
- `elevation-flat` - Subtle shadow for cards
- `elevation-raised` - Medium shadow for elevated surfaces
- `elevation-overlay` - Strong shadow for modals/overlays

**Rule:** Use elevation tokens only. No `shadow-lg`, `shadow-xl`, or `shadow-primary/20`.

## Radius Tokens

Two unified radius values:
- `--radius-control` - 0.5rem (8px) - For buttons, inputs, badges, small interactive elements
- `--radius-card` - 0.75rem (12px) - For cards, dialogs, containers

**Usage:**
- `rounded-control` - All form controls, buttons, badges
- `rounded-card` - All containers, cards, dialogs, popovers

## Color Roles

Locked semantic color roles:
- `primary` - Primary actions, links, focus states
- `secondary` - Secondary actions, accents
- `accent` - Subtle highlights, hover states
- `success` - Success states, completed actions
- `warning` - Warning states, pending actions
- `danger` - Error states, destructive actions

**Rule:** Use semantic tokens only. No palette utilities (`blue-500`, `red-500`, etc.).

## Focus States

Standardized focus ring:
- Width: `--ring-width` (2px)
- Offset: `--ring-offset` (2px)
- Color: `--ring-color` (primary color)

**Usage:** Applied automatically via `*:focus-visible` rule in base layer.

## Touch Targets

Minimum touch target size: `--size-touch-target` (2.75rem / 44px)

**Enforcement:** Applied automatically to all buttons via base layer rule.

## Motion

Standardized motion tokens:
- `--motion-duration-short` - 150ms
- `--motion-duration-medium` - 250ms
- `--motion-duration-long` - 400ms
- `--motion-ease-standard` - cubic-bezier(0.2, 0, 0, 1)

**Usage:**
- `transition-standard` - Standard transitions
- `transition-standard-fast` - Quick transitions
- `transition-standard-slow` - Slow transitions

**Motion Reduction:** All animations wrapped with `@media (prefers-reduced-motion: reduce)`.

## Local Overrides

**Rule:** No local overrides in feature code. All styling must go through component variant APIs.

**Bad:**
```tsx
<Button className="rounded-xl shadow-lg">  // ❌ Local override
```

**Good:**
```tsx
<Button variant="primary" size="lg">  // ✅ Uses variant API
```

## Adding New Variants

When adding variants to components:

1. Define in component's `cva()` configuration
2. Use semantic tokens (no palette colors)
3. Use standardized radius/elevation tokens
4. Ensure touch target compliance (44x44 minimum)
5. Test focus states in both themes
6. Document in this file
