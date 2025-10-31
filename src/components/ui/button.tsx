import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

/**
 * Button Component
 * Developer-grade with WCAG AA compliance
 * 
 * Variants:
 * - Primary: bg-primary with 8.2:1 contrast
 * - Secondary: bg-surface with border
 * - Danger: bg-danger for dangerous actions
 * - Ghost: Transparent with hover state
 * - Link: Text-only with underline
 * 
 * States:
 * - Hover: +6% lightness via filter
 * - Active: +10% lightness
 * - Disabled: 40% opacity, maintains 4.5:1 text contrast
 * - Focus: 2px ring-primary at 3:1 contrast
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-medium transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-40 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        // Primary: Pill-shaped cyan/white CTA
        default:
          "bg-cyan-500 text-black hover:brightness-110 active:brightness-95",

        // Secondary: Transparent with white border
        secondary:
          "bg-transparent text-white border border-white/20 hover:border-white/40 hover:brightness-110",

        // Danger: High risk actions
        danger:
          "bg-danger text-danger-foreground hover:brightness-110 active:brightness-95",

        // Ghost: Transparent with brightness shift
        ghost:
          "text-zinc-300 hover:text-white hover:bg-zinc-900/30",

        // Link: Text-only
        link:
          "text-cyan-500 underline-offset-4 hover:underline hover:text-cyan-400",

        // Outline: Transparent with subtle border
        outline:
          "bg-transparent text-zinc-300 border border-zinc-800 hover:border-zinc-700 hover:text-white",
      },
      size: {
        default: "h-10 px-4 py-2", // Reduced padding
        sm: "h-9 px-3 py-1.5 text-sm",
        lg: "h-11 px-5 py-2.5 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
