#!/bin/bash

# Find Hardcoded Colors Script
# Identifies components using hardcoded colors instead of design tokens

echo "🔍 Scanning for hardcoded colors in components..."
echo ""

echo "=== Hardcoded Text Colors ==="
grep -rn --include="*.tsx" --include="*.ts" \
  -E "text-(white|gray-[0-9]+|black)" \
  src/components src/pages | head -20

echo ""
echo "=== Hardcoded Background Colors ==="
grep -rn --include="*.tsx" --include="*.ts" \
  -E "bg-(gray|slate|zinc|neutral|stone)-[0-9]+" \
  src/components src/pages | head -20

echo ""
echo "=== Hardcoded Border Colors ==="
grep -rn --include="*.tsx" --include="*.ts" \
  -E "border-(white|gray-[0-9]+|black)" \
  src/components src/pages | head -20

echo ""
echo "=== Gradient Usage (should be hero only) ==="
grep -rn --include="*.tsx" --include="*.ts" \
  -E "bg-gradient-" \
  src/components src/pages | head -20

echo ""
echo "=== Off-Grid Spacing (not multiples of 8) ==="
grep -rn --include="*.tsx" --include="*.ts" \
  -E "p-[57]|px-[57]|py-[57]|m-[57]|mx-[57]|my-[57]|gap-[57]" \
  src/components src/pages | head -20

echo ""
echo "✅ Scan complete. Fix these before migration."
