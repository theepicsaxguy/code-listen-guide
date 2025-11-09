/**
 * React hooks for safe data fetching and state management
 */

import { useEffect, useRef, useState } from 'react';

/**
 * Hook to safely access route parameters with validation
 */
export function useSafeParams<T extends Record<string, string>>(
  params: Partial<T>,
  required: (keyof T)[]
): { params: T | null; isValid: boolean; missing: string[] } {
  // Compute validation during render instead of in effect
  const missing: string[] = [];
  const validated: Record<string, string> = {};

  for (const key of required) {
    const value = params[key];
    if (!value || typeof value !== 'string' || value.trim() === '') {
      missing.push(String(key));
    } else {
      validated[String(key)] = value;
    }
  }

  return {
    params: missing.length === 0 ? (validated as T) : null,
    isValid: missing.length === 0,
    missing,
  };
}

/**
 * Hook for safe component mounting detection (prevents state updates on unmounted components)
 */
export function useMounted(): React.MutableRefObject<boolean> {
  const mountedRef = useRef(false);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return mountedRef;
}

/**
 * Safe async effect that won't update state if component is unmounted
 */
export function useSafeAsyncEffect(
  effect: (isMounted: React.MutableRefObject<boolean>) => Promise<void> | void,
  deps: React.DependencyList
): void {
  const isMountedRef = useMounted();

  useEffect(() => {
    const runEffect = async () => {
      try {
        await effect(isMountedRef);
      } catch (error) {
        if (isMountedRef.current) {
          console.error('Async effect error:', error);
        }
      }
    };

    runEffect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
