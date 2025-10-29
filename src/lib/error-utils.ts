/**
 * Utility functions for safe error handling and data access
 */

/**
 * Safely extract error message from unknown error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }
  
  return 'An unexpected error occurred';
}

/**
 * Safely get FormData values with validation
 */
export function getFormValue(formData: FormData, key: string): string | null {
  const value = formData.get(key);
  
  if (value === null) {
    return null;
  }
  
  if (typeof value === 'string') {
    return value.trim() || null;
  }
  
  // File objects
  return null;
}

/**
 * Require a FormData value (throws if missing)
 */
export function requireFormValue(formData: FormData, key: string): string {
  const value = getFormValue(formData, key);
  
  if (!value) {
    throw new Error(`Missing required form field: ${key}`);
  }
  
  return value;
}

/**
 * Safely access nested object properties
 */
export function safeGet<T>(
  obj: unknown,
  path: string,
  defaultValue: T
): T {
  try {
    const keys = path.split('.');
    let result: any = obj;
    
    for (const key of keys) {
      if (result === null || result === undefined) {
        return defaultValue;
      }
      result = result[key];
    }
    
    return result ?? defaultValue;
  } catch {
    return defaultValue;
  }
}

/**
 * Safely copy to clipboard with permission handling
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    // Check if clipboard API is available
    if (!navigator.clipboard) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return success;
    }
    
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
}

/**
 * Type guard for checking if value is defined
 */
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

/**
 * Safe array access
 */
export function getArrayItem<T>(
  array: T[] | null | undefined,
  index: number,
  defaultValue: T | null = null
): T | null {
  if (!array || !Array.isArray(array) || index < 0 || index >= array.length) {
    return defaultValue;
  }
  return array[index] ?? defaultValue;
}

/**
 * Validate and sanitize navigation parameters
 */
export function safeNavigationParam(param: unknown): string | null {
  if (typeof param === 'string' && param.trim()) {
    return param.trim();
  }
  return null;
}
