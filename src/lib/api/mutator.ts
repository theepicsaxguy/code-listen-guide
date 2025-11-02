/**
 * Custom fetch instance for Orval-generated API client.
 * 
 * Handles:
 * - Base URL from environment variable
 * - Authorization token injection
 * - Content-Type headers
 * 
 * No business logic - pure request configuration only.
 */

const getBaseUrl = (): string => {
  const env = import.meta.env as { [key: string]: string | undefined };
  const baseUrl = env.VITE_API_BASE_URL || env.VITE_API_BASE_PATH || 'http://localhost:8000/api/v1';
  
  // Normalize: remove trailing slash, ensure proper format
  const normalized = baseUrl.replace(/\/+$/, '');
  return normalized;
};

export const customInstance = async <T>(
  config: RequestInit & { url: string },
  options?: RequestInit,
): Promise<T> => {
  const baseUrl = getBaseUrl();
  
  // Construct full URL
  const url = config.url.startsWith('http') 
    ? config.url 
    : `${baseUrl}${config.url.startsWith('/') ? '' : '/'}${config.url}`;

  // Get auth token from localStorage
  const token = localStorage.getItem('auth_token');
  
  // Merge headers
  const headers = new Headers({
    'Content-Type': 'application/json',
    ...(options?.headers as HeadersInit),
    ...(config.headers as HeadersInit),
  });

  // Add authorization header if token exists
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Make request
  const response = await fetch(url, {
    ...options,
    ...config,
    headers,
    credentials: 'include',
  });

  // Handle empty responses (204 No Content, etc.)
  if (response.status === 204 || response.status === 205) {
    return undefined as T;
  }

  const contentLength = response.headers.get('Content-Length');
  if (contentLength !== null && Number.parseInt(contentLength, 10) === 0) {
    return undefined as T;
  }

  // Handle error responses
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    
    // Handle FastAPI validation errors (422)
    if (response.status === 422 && Array.isArray(error.detail)) {
      const fieldErrors = error.detail.map((err: any) => {
        const field = err.loc?.slice(1).join('.') || 'field';
        return `${field}: ${err.msg || err.ctx?.error || 'Invalid value'}`;
      }).join(', ');
      throw new Error(fieldErrors);
    }
    
    // Handle other error formats
    const errorMessage = typeof error.detail === 'string' 
      ? error.detail 
      : error.message || `HTTP ${response.status}`;
    throw new Error(errorMessage);
  }

  // Parse JSON response
  const text = await response.text();
  if (text.trim() === '') {
    return undefined as T;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error('Invalid JSON response');
  }
};

