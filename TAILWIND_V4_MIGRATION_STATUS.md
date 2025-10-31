# Tailwind v4 Migration Status

## ✅ Completed

1. **Theme colors as full HSL values** - Converted all color tokens from channel triples to full `hsl()` values in `@theme` block
2. **Fixed @source globs** - Single accurate source pattern: `../src/**/*.{ts,tsx}`
3. **Typography plugin enabled** - Added `@import "@tailwindcss/typography"` and removed `dark:prose-invert` (handled by variant)
4. **Dark mode standardized** - Using `@variant dark ([data-theme="dark"] &)` only, removed class-based `.dark`
5. **PostCSS verified** - Using official `@tailwindcss/postcss` plugin
6. **Many palette utilities replaced** - Replaced status colors, icons, and badges with semantic tokens:
   - `bg-green-500` → `bg-success`
   - `bg-red-500` → `bg-danger`
   - `bg-blue-500` → `bg-primary`
   - `bg-yellow-500` → `bg-warning`
   - `bg-purple-500` → `bg-secondary`
   - And many more...

7. **Max-width constraints** - Replaced `max-w-[1280px]` with `max-w-content-default`, `max-w-[1800px]` with `max-w-content-wide`
8. **Motion reduction** - Added `@media (prefers-reduced-motion: reduce)` support
9. **Focus normalization** - Standardized focus ring via `*:focus-visible` rule
10. **Touch target enforcement** - Added minimum 44x44 size for buttons

## 🚧 In Progress / Partial

1. **Radius unification** - Defined `--radius-control` and `--radius-card` tokens, but many components still use `rounded-lg`, `rounded-xl`, etc.
2. **Elevation tokens** - Defined `elevation-flat`, `elevation-raised`, `elevation-overlay`, but many components use `shadow-lg`, `shadow-xl`, `shadow-primary/20`, etc.
3. **Icon sizing** - Defined tokens (`--size-icon-xs` through `--size-icon-xl`), but not consistently applied
4. **Gradients** - Still many custom gradients that don't match brand tokens
5. **Bracket utilities** - Many `w-[...]`, `h-[...]`, `p-[...]` still exist

## ❌ Remaining Work

1. **Replace all `rounded-lg`/`rounded-xl`** with `rounded-control` or `rounded-card`
2. **Replace shadow utilities** (`shadow-lg`, `shadow-xl`, `shadow-primary/20`) with elevation tokens
3. **Replace gradients** - Consolidate to 1-2 brand gradients
4. **Remove bracket utilities** - Replace `w-[264px]`, `h-[400px]`, etc. with spacing/size tokens
5. **Component variants documentation** - Document size variants, states, density for each component
6. **Charts styling** - Ensure charts use tokens, not inline colors
7. **Contrast checker in CI** - Add as hard gate (script exists but not enforced)
8. **Spacing alignment** - Audit and replace off-scale spacing values
9. **Border normalization** - Ensure single default border width/color everywhere
10. **Verify tailwindcss-animate** - Confirm CSS import works (may need to stay in JS config)

## Files Modified

- `src/index.css` - Complete rewrite with v4 @theme, full colors, unified tokens
- `tailwind.config.ts` - Removed JS plugins (moved to CSS)
- `postcss.config.js` - Verified correct v4 plugin
- `src/pages/admin/Agents.tsx` - Replaced palette utilities
- `src/pages/admin/Content.tsx` - Replaced status colors
- `src/pages/admin/JobTracing.tsx` - Replaced status colors
- `src/pages/admin/ChonkieTest.tsx` - Replaced palette utilities
- `src/pages/admin/Chonkieest.tsx` - Replaced palette utilities
- `src/pages/admin/UserDetails.tsx` - Replaced status colors
- `src/pages/admin/AgentTest.tsx` - Replaced icon colors
- `src/pages/Dashboard.tsx` - Replaced max-width constraints
- `src/pages/admin/Dashboard.tsx` - Replaced max-width constraints
- `src/pages/AdminParse.tsx` - Replaced palette utilities and max-width
- `src/pages/admin/workflows/WorkflowList.tsx` - Replaced max-width constraint
- `src/App.css` - Replaced max-width constraint

## Next Steps

1. Systematically replace all `rounded-*` utilities (grep and replace)
2. Systematically replace all `shadow-*` utilities (grep and replace)
3. Audit and consolidate gradients
4. Replace bracket utilities with tokens
5. Document component variants
6. Add contrast checker to CI pipeline
