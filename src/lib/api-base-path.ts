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

const fromUrl = (raw: string): string => {
  const url = new URL(raw);
  const path = normalizePath(url.pathname || '/');
  return path === '/' ? DEFAULT_API_PATH : path;
};

const fromHostLike = (raw: string): string => {
  try {
    return fromUrl(`http://${raw}`);
  } catch (error) {
    throw new Error('VITE_API_BASE_PATH must be a path beginning with "/"');
  }
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
    return fromUrl(raw);
  }
  if (!raw.startsWith('/')) {
    if (raw.includes(':')) {
      return fromHostLike(raw);
    }
    throw new Error('VITE_API_BASE_PATH must be a path beginning with "/"');
  }
  return normalizePath(raw);
};
