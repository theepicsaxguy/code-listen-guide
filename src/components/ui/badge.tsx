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
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        // Info: blue (Comments) - Subtle muted neon
        default:
          "bg-blue-500/5 text-blue-300",
        
        // Success: green (Accessibility)
        success:
          "bg-green-500/5 text-green-300",
        
        // Danger: red (Share)
        danger:
          "bg-red-500/5 text-red-300",
        
        // Warning: orange (Collaborators)
        warning:
          "bg-orange-500/5 text-orange-300",
        
        // Info: blue semantic
        info:
          "bg-blue-500/5 text-blue-300",
        
        // Pending: purple (CMS Drafts)
        pending:
          "bg-purple-500/5 text-purple-300",
        
        // Primary: cyan/teal (Feature Flags)
        primary:
          "bg-cyan-500/5 text-cyan-300",
        
        // Secondary: purple accent
        secondary:
          "bg-purple-500/5 text-purple-300",
        
        // Outline: minimal badge with border
        outline:
          "bg-transparent text-zinc-500 border border-zinc-800",
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
