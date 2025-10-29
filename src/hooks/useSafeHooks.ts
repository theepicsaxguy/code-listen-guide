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
  const [result, setResult] = useState<{ params: T | null; isValid: boolean; missing: string[] }>({
    params: null,
    isValid: false,
    missing: [],
  });

  useEffect(() => {
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

    setResult({
      params: missing.length === 0 ? (validated as T) : null,
      isValid: missing.length === 0,
      missing,
    });
  }, [params, required]);

  return result;
}

/**
 * Hook for safe component mounting detection (prevents state updates on unmounted components)
 */
export function useMounted(): () => boolean {
  const mountedRef = useRef(false);
  const isMounted = useRef(() => mountedRef.current);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return isMounted.current;
}

/**
 * Safe async effect that won't update state if component is unmounted
 */
export function useSafeAsyncEffect(
  effect: (isMounted: () => boolean) => Promise<void> | void,
  deps: React.DependencyList
): void {
  const isMounted = useMounted();

  useEffect(() => {
    const runEffect = async () => {
      try {
        await effect(isMounted);
      } catch (error) {
        if (isMounted()) {
          console.error('Async effect error:', error);
        }
      }
    };

    runEffect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
