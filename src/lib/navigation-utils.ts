/**
 * Safe navigation utilities to prevent navigation with invalid parameters
 */

import { NavigateFunction } from 'react-router-dom';

/**
 * Safely navigate to a route with validated parameters
 */
export function safeNavigate(
  navigate: NavigateFunction,
  path: string,
  options?: { replace?: boolean; state?: any }
): void {
  try {
    // Validate path is not empty
    if (!path || typeof path !== 'string' || path.trim() === '') {
      console.error('Navigation attempted with invalid path:', path);
      navigate('/', { replace: true });
      return;
    }

    navigate(path, options);
  } catch (error) {
    console.error('Navigation error:', error);
    // Fallback to home page on navigation errors
    navigate('/', { replace: true });
  }
}

/**
 * Build a route path with validated parameters
 */
export function buildRoutePath(
  template: string,
  params: Record<string, string | number | null | undefined>
): string {
  let path = template;

  for (const [key, value] of Object.entries(params)) {
    const placeholder = `:${key}`;
    
    if (path.includes(placeholder)) {
      if (value === null || value === undefined || value === '') {
        console.error(`Missing required route parameter: ${key}`);
        return '/';
      }
      
      path = path.replace(placeholder, encodeURIComponent(String(value)));
    }
  }

  // Check if any placeholders remain unfilled
  if (path.includes(':')) {
    console.error('Route has unfilled parameters:', path);
    return '/';
  }

  return path;
}

/**
 * Safely navigate with dynamic route parameters
 */
export function navigateWithParams(
  navigate: NavigateFunction,
  template: string,
  params: Record<string, string | number | null | undefined>,
  options?: { replace?: boolean; state?: any }
): void {
  const path = buildRoutePath(template, params);
  safeNavigate(navigate, path, options);
}
