import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 shadow-sm",
  {
    variants: {
      variant: {
        default: "border-transparent bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-md shadow-primary/20",
        secondary: "border-transparent bg-gradient-secondary text-secondary-foreground hover:opacity-90 shadow-md shadow-secondary/20",
        destructive: "border-transparent bg-gradient-to-r from-destructive to-destructive/80 text-destructive-foreground hover:opacity-90 shadow-md shadow-destructive/20",
        outline: "text-foreground border-primary/40 hover:border-primary/60 hover:bg-primary/10",
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
