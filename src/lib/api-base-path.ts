const DEFAULT_API_PATH = '/api/v1';
const ABSOLUTE_URL_PATTERN = /^[a-zA-Z][a-zA-Z\d+\-.]*:\/\//;

const stripTrailingSlash = (value: string): string => {
  if (value === '/') {
    return value;
  }
  return value.replace(/\/+$/, '');
};

const ensureLeadingSlash = (value: string): string => {
  if (value.startsWith('/')) {
    return value;
  }
  return `/${value}`;
};

const normalizePath = (value: string): string => {
  const withLeadingSlash = ensureLeadingSlash(value);
  const trimmed = stripTrailingSlash(withLeadingSlash);
  return trimmed === '' ? '/' : trimmed;
};

const normalizeRelative = (value: string): string => {
  const normalized = normalizePath(value);
  return normalized === '/' ? '' : normalized;
};

const normalizeAbsolute = (raw: string): string => {
  const candidate = ABSOLUTE_URL_PATTERN.test(raw) ? raw : `http://${raw}`;
  const url = new URL(candidate);
  const normalizedPath = normalizePath(url.pathname || '/');
  const path = normalizedPath === '/' ? '' : normalizedPath;
  return `${url.origin}${path}`;
};

const pickRawValue = (): string => {
  const env = import.meta.env as { [key: string]: string | undefined };
  const candidate = env.VITE_API_BASE_PATH ?? env.VITE_API_BASE_URL;
  return (candidate ?? DEFAULT_API_PATH).trim();
};

export const resolveApiBasePath = (): string => {
  const raw = pickRawValue();
  if (raw === '') {
    throw new Error('VITE_API_BASE_PATH cannot be empty');
  }
  if (ABSOLUTE_URL_PATTERN.test(raw)) {
    return normalizeAbsolute(raw);
  }
  if (!raw.startsWith('/')) {
    return normalizeAbsolute(raw);
  }
  const relative = normalizeRelative(raw);
  return relative;
};
