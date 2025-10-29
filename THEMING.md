# Codebase Audiobook - Theming Guide

## Brand Colors

- **Primary**: Electric Purple = `text-purple-500`, `bg-purple-500`
- **Accent**: Cyan = `text-cyan-500`, `bg-cyan-500`
- **Background**: `bg-gray-950` (page), `bg-gray-900` (cards)
- **Borders**: `border-gray-800`
- **Text**: `text-white` (headings), `text-gray-400` (descriptions)

## ⚠️ CRITICAL RULE

**ALWAYS use explicit Tailwind gray classes instead of CSS variables!**

```tsx
// ✅ GOOD - Explicit colors
<div className="bg-gray-900 border border-gray-800">
<h1 className="text-white">Title</h1>
<p className="text-gray-400">Description</p>

// ❌ BAD - CSS variables (inconsistent)
<div className="bg-card border border-border">
<h1 className="text-foreground">Title</h1>
<p className="text-muted-foreground">Description</p>
```

## Standard Color Palette

### Backgrounds
- `bg-gray-950` - Page background
- `bg-gray-900` - Card/section background
- `bg-gray-800` - Hover states
- `bg-gray-800/50` - Subtle backgrounds

### Borders
- `border-gray-800` - Default borders
- `border-gray-700` - Lighter borders (inputs)

### Text
- `text-white` - Headings, important text
- `text-gray-300` - Body text
- `text-gray-400` - Descriptions, secondary text
- `text-gray-500` - Muted/disabled text

### Brand Accents
- `text-purple-500` / `bg-purple-500` - Primary actions, highlights
- `text-cyan-500` / `bg-cyan-500` - Secondary highlights
- Gradients: `bg-gradient-to-r from-purple-500 to-cyan-500`

## Components

### Admin Components (Reusable)

1. **StatusBadge** (`/src/components/admin/StatusBadge.tsx`)
   - Automatic colors based on status
   - Built-in icons
   
2. **StatCard** (`/src/components/admin/StatCard.tsx`)
   - Dashboard statistics
   - Consistent styling
   
3. **DataTable** (`/src/components/admin/DataTable.tsx`)
   - Table wrapper with proper styling
   - Empty state included

### Theme Utilities (`/src/lib/theme.ts`)

```tsx
import { formatCurrency, formatNumber, getStatusClasses } from "@/lib/theme";

// Format money
formatCurrency(1250) // "$12.50"

// Format numbers
formatNumber(1000000) // "1,000,000"

// Get status colors
const classes = getStatusClasses("completed");
// Returns: { bg: "bg-green-500/10", text: "text-green-500", ... }
```

## Page Structure Template

```tsx
export default function AdminPage() {
  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Page Title</h1>
        <p className="text-gray-400 mt-1">Page description</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Total" value={123} icon={Icon} />
      </div>

      {/* Content Card */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Section</h3>
        {/* Content */}
      </div>

      {/* Table */}
      <DataTable>
        <Table>
          {/* Table content */}
        </Table>
      </DataTable>
    </div>
  );
}
```

## Migration Checklist

For each admin page:

- [ ] Replace `bg-card` → `bg-gray-900`
- [ ] Replace `border-border` → `border-gray-800`
- [ ] Replace `text-foreground` → `text-white`
- [ ] Replace `text-muted-foreground` → `text-gray-400`
- [ ] Use `<StatusBadge>` for status indicators
- [ ] Use `<DataTable>` for tables
- [ ] Use `formatCurrency()` for money
- [ ] Use `formatNumber()` for large numbers

## Files Updated

- ✅ `/src/lib/theme.ts` - Centralized utilities
- ✅ `/src/components/admin/StatusBadge.tsx` - Status component
- ✅ `/src/components/admin/DataTable.tsx` - Table wrapper
- ✅ `/src/pages/admin/Dashboard.tsx` - Admin dashboard
- ✅ `/src/pages/admin/AgentMonitoring.tsx` - Agent monitoring
- ✅ `/src/pages/admin/AuditLogs.tsx` - Already using hardcoded colors

## Files TODO

- [ ] `/src/pages/admin/Users.tsx`
- [ ] `/src/pages/admin/Content.tsx`
- [ ] `/src/pages/admin/Payments.tsx`
- [ ] `/src/pages/admin/JobTracing.tsx`
- [ ] `/src/pages/admin/Agents.tsx`
- [ ] `/src/pages/admin/Settings.tsx`
- [ ] `/src/pages/admin/Support.tsx`
