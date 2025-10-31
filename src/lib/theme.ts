/**
 * Centralized theme configuration for Codebase Audiobook
 *
 * Uses token-based Tailwind classes from src/index.css.
 * All colors reference CSS variables for consistency.
 */

export const theme = {
  // Status colors - using semantic token classes
  status: {
    success: {
      bg: "bg-success/10",
      text: "text-success",
      border: "",
      icon: "text-success",
    },
    error: {
      bg: "bg-danger/10",
      text: "text-danger",
      border: "border-danger/20",
      icon: "text-danger",
    },
    warning: {
      bg: "bg-warning/10",
      text: "text-warning",
      border: "border-warning/20",
      icon: "text-warning",
    },
    info: {
      bg: "bg-primary/10",
      text: "text-primary",
      border: "border-primary/20",
      icon: "text-primary",
    },
    pending: {
      bg: "bg-muted/50",
      text: "text-muted-foreground",
      border: "border-muted",
      icon: "text-muted-foreground",
    },
  },

  // Card variants - using token-based classes
  card: {
    default: "bg-card shadow-sm",
    elevated: "bg-card shadow-md hover:shadow-lg transition-shadow duration-300",
    ghost: "bg-transparent",
  },

  // Table styling - using token-based classes
  table: {
    container: "bg-card rounded-lg shadow-sm overflow-hidden",
    header: "bg-muted/50",
    row: "transition-colors hover:bg-muted/30",
  },

  // Input styling
  input: {
    default: "bg-input text-foreground",
  },

  // Typography - using token-based foreground
  heading: {
    h1: "text-3xl font-bold text-foreground",
    h2: "text-2xl font-semibold text-foreground",
    h3: "text-xl font-semibold text-foreground",
    description: "text-muted-foreground mt-1",
  },

  // Background colors - using token-based classes
  background: {
    page: "bg-background",
    card: "bg-card",
    sidebar: "bg-card",
  },

  // Border colors - using token-based classes
  border: {
    default: "",
    subtle: "",
  },
} as const;

/**
 * Get status-specific classes for badges, icons, etc.
 */
export function getStatusClasses(status: string) {
  const normalized = status.toLowerCase();

  switch (normalized) {
    case "completed":
    case "success":
    case "active":
      return theme.status.success;

    case "failed":
    case "error":
    case "suspended":
      return theme.status.error;

    case "waiting_approval":
    case "warning":
      return theme.status.warning;

    case "analyzing":
    case "scripting":
    case "synthesizing":
    case "post_processing":
    case "processing":
    case "running":
      return theme.status.info;

    case "pending":
    case "queued":
    default:
      return theme.status.pending;
  }
}

/**
 * Format currency consistently across the app
 */
export function formatCurrency(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

/**
 * Format numbers with locale support
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}
