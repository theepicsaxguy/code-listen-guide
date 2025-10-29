/**
 * Centralized theme configuration for Codebase Audiobook
 *
 * Brand colors: Electric Purple & Cyan on dark background
 * All admin pages and components should use these constants for consistency
 */

export const theme = {
  // Status colors - used for badges, indicators, etc.
  status: {
    success: {
      bg: "bg-green-500/10",
      text: "text-green-500",
      border: "border-green-500/20",
      icon: "text-green-500",
    },
    error: {
      bg: "bg-red-500/10",
      text: "text-red-500",
      border: "border-red-500/20",
      icon: "text-red-500",
    },
    warning: {
      bg: "bg-yellow-500/10",
      text: "text-yellow-500",
      border: "border-yellow-500/20",
      icon: "text-yellow-500",
    },
    info: {
      bg: "bg-blue-500/10",
      text: "text-blue-500",
      border: "border-blue-500/20",
      icon: "text-blue-500",
    },
    pending: {
      bg: "bg-gray-500/10",
      text: "text-gray-400",
      border: "border-gray-500/20",
      icon: "text-gray-500",
    },
  },

  // Card variants - using explicit gray colors for consistency
  card: {
    default: "bg-gray-900 border border-gray-800 shadow-sm",
    elevated: "bg-gray-900 border border-gray-800 shadow-lg hover:shadow-purple-500/10 transition-shadow duration-300",
    ghost: "bg-transparent border-0",
  },

  // Table styling - using explicit gray colors
  table: {
    container: "bg-gray-900 border border-gray-800 rounded-lg shadow-sm overflow-hidden",
    header: "bg-gray-800/50",
    row: "border-b border-gray-800 transition-colors hover:bg-gray-800/30",
  },

  // Input styling
  input: {
    default: "bg-input border-border text-foreground",
  },

  // Typography
  heading: {
    h1: "text-3xl font-bold text-white",
    h2: "text-2xl font-semibold text-white",
    h3: "text-xl font-semibold text-white",
    description: "text-gray-400 mt-1",
  },

  // Background colors
  background: {
    page: "bg-gray-950",
    card: "bg-gray-900",
    sidebar: "bg-gray-900",
  },

  // Border colors
  border: {
    default: "border-gray-800",
    subtle: "border-gray-800/50",
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
