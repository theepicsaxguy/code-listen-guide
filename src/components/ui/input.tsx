import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Input Component
 * Professional developer tools form input
 * 
 * Specifications:
 * - Background: bg-surface (elevated surface)
 * - Border: border border-border
 * - Focus: ring-2 ring-primary/50
 * - No rounded corners on containers (only buttons/inputs)
 */

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-control border border-border bg-surface px-4 py-2 text-sm text-foreground",
          "placeholder:text-muted-foreground",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-0",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "transition-standard",
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
