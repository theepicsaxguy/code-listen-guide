import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Input Component
 * WCAG AA compliant form input with proper focus states
 * 
 * Specifications:
 * - Height: 40px (h-10) to match Button
 * - Background: bg-input (not white)
 * - Border: 1px border-border, no shadows
 * - Focus: 2px ring-ring at 3:1 contrast
 * - No bright inner shadows or white outlines
 */

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-control border border-border bg-input px-4 py-2 text-base text-foreground ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors transition-standard",
          className,
        )}
        ref={ref}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";

export { Input };
