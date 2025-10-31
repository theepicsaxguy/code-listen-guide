import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

/**
 * Badge Component
 * Status and label indicators with WCAG AA compliance
 * 
 * Variants mapped to design tokens:
 * - default (pending): muted on surface
 * - success: success token (4.6:1 contrast)
 * - danger: danger token (5.2:1 contrast)
 * - primary (in-progress): primary outline
 * - warning: warning token (6.1:1 contrast)
 * 
 * No gradients or glow effects in product UIs
 */
const badgeVariants = cva(
  "inline-flex items-center rounded-control px-2.5 py-0.5 text-xs font-semibold transition-standard focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        // Pending/default: purple semantic color
        default:
          "bg-pending/5 text-pending",
        
        // Success: completed jobs - green semantic
        success:
          "bg-success/5 text-success",
        
        // Danger/Failed: error states - red semantic
        danger:
          "bg-danger/5 text-danger",
        
        // Primary/In Progress: active states - cyan
        primary:
          "bg-primary/5 text-primary",
        
        // Warning: caution states - amber
        warning:
          "bg-warning/5 text-warning",
        
        // Secondary: purple accent (use sparingly)
        secondary:
          "bg-secondary/5 text-secondary",
        
        // Outline: minimal badge with border
        outline:
          "bg-surface text-foreground border border-border",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
