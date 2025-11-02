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
  // Note: The orval/esbuild warning about import.meta is expected and harmless.
  // import.meta.env is available at runtime in Vite, which handles this correctly.
  // The mutator file is not compiled by orval - it's just referenced by the generated code.
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
  let url: string;
  if (config.url.startsWith('http')) {
    // Already a full URL
    url = config.url;
  } else if (config.url.startsWith('/api/v1')) {
    // URL already includes /api/v1, so just prepend the domain
    const baseUrlWithoutPath = baseUrl.replace(/\/api\/v1\/?$/, '');
    url = `${baseUrlWithoutPath}${config.url}`;
  } else {
    // Relative URL, prepend base URL
    url = `${baseUrl}${config.url.startsWith('/') ? '' : '/'}${config.url}`;
  }

  // Get auth token from localStorage
  const token = localStorage.getItem('auth_token');
  
  // Extract data/body from config
  const requestBody = (config as any).data || (config as any).body || null;
  
  // Determine content type from headers or body type
  // Headers can be a Headers object, Record<string, string>, or array of tuples
  let contentTypeFromHeaders: string | null = null;
  
  if (config.headers) {
    if (config.headers instanceof Headers) {
      contentTypeFromHeaders = config.headers.get('Content-Type') || config.headers.get('content-type');
    } else if (typeof config.headers === 'object') {
      const headersObj = config.headers as Record<string, string>;
      contentTypeFromHeaders = headersObj['Content-Type'] || headersObj['content-type'] || null;
    }
  }
  
  if (!contentTypeFromHeaders && options?.headers) {
    if (options.headers instanceof Headers) {
      contentTypeFromHeaders = options.headers.get('Content-Type') || options.headers.get('content-type');
    } else if (typeof options.headers === 'object') {
      const headersObj = options.headers as Record<string, string>;
      contentTypeFromHeaders = headersObj['Content-Type'] || headersObj['content-type'] || null;
    }
  }
  
  const isFormUrlEncoded = contentTypeFromHeaders === 'application/x-www-form-urlencoded';
  const isURLSearchParams = requestBody instanceof URLSearchParams;
  
  // Merge headers
  const headers = new Headers();
  
  // Set Content-Type - preserve if already set (especially for form-urlencoded)
  if (isFormUrlEncoded) {
    headers.set('Content-Type', 'application/x-www-form-urlencoded');
  } else if (contentTypeFromHeaders) {
    headers.set('Content-Type', contentTypeFromHeaders as string);
  } else {
    headers.set('Content-Type', 'application/json');
  }
  
  // Add other headers from options and config
  if (options?.headers) {
    const optsHeaders = new Headers(options.headers as HeadersInit);
    optsHeaders.forEach((value, key) => {
      if (key.toLowerCase() !== 'content-type' || !isFormUrlEncoded) {
        headers.set(key, value);
      }
    });
  }
  
  if (config.headers) {
    const configHeaders = new Headers(config.headers as HeadersInit);
    configHeaders.forEach((value, key) => {
      if (key.toLowerCase() !== 'content-type' || !isFormUrlEncoded) {
        headers.set(key, value);
      }
    });
  }

  // Add authorization header if token exists
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Prepare fetch config (exclude data/body from config, handle separately)
  const { data: _data, body: _body, ...fetchConfig } = config as any;
  
  // Serialize body based on content type
  let serializedBody: string | undefined = undefined;
  if (requestBody) {
    if (typeof requestBody === 'string') {
      serializedBody = requestBody;
    } else if (isURLSearchParams || isFormUrlEncoded) {
      // For form-urlencoded, convert URLSearchParams to string
      serializedBody = requestBody instanceof URLSearchParams 
        ? requestBody.toString() 
        : (typeof requestBody === 'string' ? requestBody : new URLSearchParams(requestBody as any).toString());
    } else {
      // JSON serialization for other types
      serializedBody = JSON.stringify(requestBody);
    }
  }
  
  // Make request
  const response = await fetch(url, {
    ...options,
    ...fetchConfig,
    headers,
    credentials: 'include',
    body: serializedBody,
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

