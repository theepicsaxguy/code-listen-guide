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
  "inline-flex items-center rounded-control border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        // Pending/default: muted on surface
        default:
          "border-transparent bg-muted/20 text-muted-foreground",
        
        // Success: completed jobs
        success:
          "border-transparent bg-success/10 text-success border border-success/20",
        
        // Danger/Failed: error states
        danger:
          "border-transparent bg-danger/10 text-danger border border-danger/20",
        
        // Primary/In Progress: active states
        primary:
          "bg-primary/10 text-primary border border-primary/20",
        
        // Warning: caution states
        warning:
          "border-transparent bg-warning/10 text-warning border border-warning/20",
        
        // Secondary: purple accent (use sparingly)
        secondary:
          "border-transparent bg-secondary/10 text-secondary border border-secondary/20",
        
        // Outline: minimal badge
        outline:
          "text-text border-border",
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
