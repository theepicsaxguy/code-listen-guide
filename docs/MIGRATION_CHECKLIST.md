# Design System Migration Checklist

Track progress migrating to the developer-grade design system.

## Foundation ✅

- [x] Create `src/styles/design-tokens.css` with HSL tokens
- [x] Update `tailwind.config.ts` with alpha-value mappings
- [x] Import tokens in `src/index.css`
- [x] Remove duplicate color definitions from `index.css`
- [x] Update Button component to use new tokens
- [x] Create `DESIGN_SYSTEM.md` documentation
- [x] Create `docs/DESIGN_SYSTEM_GUIDE.md` full reference
- [x] Create migration scripts

## Component Updates

### Core UI Components (src/components/ui/)

- [x] `button.tsx` - ✅ Migrated
- [ ] `input.tsx` - Update to use `bg-input`, `border-border`, focus ring
- [ ] `badge.tsx` - Map variants to semantic tokens (success, warning, danger)
- [ ] `card.tsx` - Use `bg-card`, `border-border`, proper spacing (p-4, p-3)
- [ ] `table.tsx` - Row height 48px, header text-text/80, hover bg-accent
- [ ] `select.tsx` - Match input styles
- [ ] `textarea.tsx` - Match input styles
- [ ] `dialog.tsx` - Use popover tokens
- [ ] `dropdown-menu.tsx` - Use popover tokens
- [ ] `context-menu.tsx` - Use popover tokens
- [ ] `sheet.tsx` - Use card/popover tokens
- [ ] `alert.tsx` - Map to semantic colors
- [ ] `toast.tsx` - Use card tokens

### Layout Components (src/components/layout/)

- [ ] `Sidebar.tsx` - 264px width, use sidebar tokens, active state with 2px stripe
- [ ] `AppShell.tsx` - Verify spacing grid, max-width 1280px
- [ ] `PageHeader.tsx` - Breadcrumb → Title → Actions pattern

### Custom Components (src/components/)

- [ ] `Hero.tsx` - Keep gradient, use token-based text/CTAs
- [ ] `Footer.tsx` - Use text tokens
- [ ] `Pricing.tsx` - Card borders, spacing grid
- [ ] `Stats.tsx` - KPI card pattern
- [ ] `MarketValidation.tsx` - Chart contrast WCAG AA
- [ ] `Testimonials.tsx` - Card styling
- [ ] `FAQ.tsx` - Accordion with proper tokens
- [ ] `SampleShowcase.tsx` - Card grid
- [ ] `ChunkVisualizer.tsx` - Code blocks with mono font
- [ ] `FileViewer.tsx` - Code display contrast
- [ ] `RepositoryBrowser.tsx` - Tree view styling
- [ ] `AdminFileViewer.tsx` - Same as FileViewer

## Page Updates

### Public Pages (src/pages/)

- [ ] `Index.tsx` - Landing page, hero gradient OK, rest use tokens
- [ ] `Auth.tsx` - Form inputs, buttons
- [ ] `WhyWeExist.tsx` - Content page styling
- [ ] `Submit.tsx` - Form layout, depth selector
- [ ] `Dashboard.tsx` - Job list, filter panel (collapsible), status badges
- [ ] `JobDetails.tsx` - Card layout, progress indicators
- [ ] `Player.tsx` - Audio player UI
- [ ] `OutlinePreview.tsx` - Chapter list, approval flow

### Admin Pages (src/pages/admin/)

- [ ] `Users.tsx` - Table with 48px rows, hover states
- [ ] `Payments.tsx` - KPI cards 3-column grid, table styling
- [ ] `Jobs.tsx` - Job management table
- [ ] `Agents.tsx` - Agent test 2-column layout (config | log)
- [ ] `Chonkieest.tsx` - Code analysis UI
- [ ] `Settings.tsx` - Grouped sections (Profile, Notifications, Billing)
- [ ] `AuditLogs.tsx` - Table with secondary text for IDs

## Systematic Replacements

### Text Colors

- [ ] Find/replace `text-white` → `text-text`
- [ ] Find/replace `text-gray-400` → `text-muted-foreground`
- [ ] Find/replace `text-gray-300` → `text-text`
- [ ] Find/replace `text-gray-500` → `text-muted-foreground`
- [ ] Verify all text meets 4.5:1 contrast

### Background Colors

- [ ] Find/replace `bg-gray-900` → `bg-background`
- [ ] Find/replace `bg-gray-800` → `bg-surface`
- [ ] Find/replace `bg-gray-700` → `bg-muted`
- [ ] Remove `bg-black` (use `bg-background`)

### Border Colors

- [ ] Find/replace `border-white` → `border-border`
- [ ] Find/replace `border-gray-700` → `border-border`
- [ ] Find/replace `border-gray-600` → `border-border`
- [ ] Remove white borders from hover states

### Gradients

- [ ] Remove gradients from Button (except landing hero CTAs)
- [ ] Remove gradients from Cards
- [ ] Remove gradients from Badges
- [ ] Keep gradients only in Hero component
- [ ] Remove glow effects from app UIs

### Spacing Grid

- [ ] Run `scripts/find-hardcoded-colors.sh` to find off-grid spacing
- [ ] Fix `p-5` → `p-4` or `p-6` (32px or 48px)
- [ ] Fix `gap-7` → `gap-6` or `gap-8` (48px or 64px)
- [ ] Verify all spacing multiples of 8px

## Layout Patterns

### Application Shell

- [ ] Sidebar: 264px fixed width
- [ ] Sidebar: Active item with 2px primary stripe + bg tint
- [ ] Content: max-w-[1280px] for marketing, fluid for tables
- [ ] Header: 64px height, breadcrumb + title + actions

### Page Headers

- [ ] Breadcrumb above title (left-aligned)
- [ ] Title + short description on left
- [ ] Primary action on right (one only)
- [ ] Secondary actions next to primary

### Filters

- [ ] Move filters to collapsible panel
- [ ] Default collapsed state
- [ ] Toggle visible and discoverable

### Tables

- [ ] Row height: 48px (h-12)
- [ ] Header: text-text/80, no uppercase
- [ ] Hover: bg-accent/50, not white border
- [ ] Zebra: bg-surface with alpha
- [ ] Secondary text: text-muted-foreground, text-sm

## Accessibility

### Focus States

- [ ] All buttons have focus-visible:ring-2
- [ ] All inputs have focus ring
- [ ] All links have focus styles
- [ ] Focus ring is 2px primary at 3:1 contrast

### Keyboard Navigation

- [ ] Tab reaches all interactive elements
- [ ] Escape closes modals/dropdowns
- [ ] Focus returns to trigger after close

### Contrast Checks

- [ ] Run contrast checker on all text
- [ ] Verify semantic colors meet 4.5:1
- [ ] Check UI borders meet 3:1
- [ ] Test with high-contrast mode

## CI/CD

- [ ] Add contrast check to GitHub Actions
- [ ] Add ESLint rule to block hardcoded hex colors
- [ ] Configure Storybook for component docs
- [ ] Set up visual regression testing
- [ ] Add pre-commit hook for token validation

## Documentation

- [x] Main README updated with design system reference
- [ ] Storybook stories for all UI primitives
- [ ] Visual regression snapshots locked
- [ ] Component API docs generated

## Testing

- [ ] Test dark theme in all pages
- [ ] Test light theme in all pages
- [ ] Test theme toggle functionality
- [ ] Test with prefers-reduced-motion
- [ ] Test with prefers-contrast: high
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility

## Performance

- [ ] Verify CSS bundle size (tokens should be minimal)
- [ ] Check for unused Tailwind classes
- [ ] Purge old gradient/shadow utilities
- [ ] Optimize theme switching performance

---

## Progress Tracking

**Phase 1 (Foundation):** ✅ 100% Complete
**Phase 2 (Core Components):** 🟡 10% Complete (1/12)
**Phase 3 (Pages):** ⚪ 0% Complete (0/15)
**Phase 4 (Cleanup):** ⚪ 0% Complete
**Phase 5 (Polish):** ⚪ 0% Complete

**Overall:** 🟡 15% Complete

---

## Next Steps

1. **Immediate:** Update Input, Badge, Card components
2. **This Week:** Migrate Dashboard and JobDetails pages
3. **Next Week:** Admin pages and systematic replacements
4. **After:** CI/CD integration and visual regression tests

Run `scripts/find-hardcoded-colors.sh` to identify high-priority fixes.
