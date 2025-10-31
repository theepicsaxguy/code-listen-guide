import { readFile } from 'node:fs/promises';

function hslToRgb(h, s, l) {
  s /= 100;
  l /= 100;
  const k = n => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = n => l - a * Math.max(-1, Math.min(Math.min(k(n) - 3, 9 - k(n)), 1));
  return [f(0), f(8), f(4)];
}

function relativeLuminance([r, g, b]) {
  const transform = (channel) => {
    if (channel <= 0.03928) {
      return channel / 12.92;
    }
    return ((channel + 0.055) / 1.055) ** 2.4;
  };
  const [rl, gl, bl] = [transform(r), transform(g), transform(b)];
  return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl;
}

function contrastRatio(colorA, colorB) {
  const [h1, s1, l1] = colorA.split(' ').map(Number);
  const [h2, s2, l2] = colorB.split(' ').map(Number);
  const lumA = relativeLuminance(hslToRgb(h1, s1, l1));
  const lumB = relativeLuminance(hslToRgb(h2, s2, l2));
  const lighter = Math.max(lumA, lumB);
  const darker = Math.min(lumA, lumB);
  return (lighter + 0.05) / (darker + 0.05);
}

async function main() {
  const css = await readFile('src/styles/design-tokens.css', 'utf8');
  const tokens = { dark: {}, light: {} };
  let current = null;
  let depth = 0;
  for (const rawLine of css.split('\n')) {
    const line = rawLine.trim();
    if (line.startsWith('[data-theme="dark"')) {
      current = 'dark';
    } else if (line.startsWith('[data-theme="light"')) {
      current = 'light';
    }

    if (line.includes('{')) {
      depth += 1;
    }
    if (line.includes('}')) {
      depth = Math.max(depth - 1, 0);
      if (depth === 0) {
        current = null;
      }
    }

    if (!current) {
      continue;
    }

    const match = line.match(/--([\w-]+):\s*([^;]+);/);
    if (match) {
      tokens[current][match[1]] = match[2].trim();
    }
  }

  const light = tokens.light;
  const dark = Object.keys(tokens.dark).length > 0 ? tokens.dark : tokens.light;

  const ensureTokens = (theme, required) => required.every((token) => typeof theme[token] === 'string');

  const checks = [
    { tokens: ['text', 'background'], minimum: 4.5, description: 'text on background' },
    { tokens: ['text', 'surface'], minimum: 4.5, description: 'text on surface' },
    { tokens: ['muted', 'surface'], minimum: 4.5, description: 'muted text on surface' },
    { tokens: ['primary', 'surface'], minimum: 4.5, description: 'primary on surface' },
    { tokens: ['border', 'surface'], minimum: 3, description: 'border on surface' },
  ];

  const failures = [];
  for (const { tokens, minimum, description } of checks) {
    if (!ensureTokens(light, tokens) || !ensureTokens(dark, tokens)) {
      failures.push(`Missing tokens for ${description}`);
      continue;
    }
    const lightRatio = contrastRatio(light[tokens[0]], light[tokens[1]]);
    const darkRatio = contrastRatio(dark[tokens[0]], dark[tokens[1]]);
    if (lightRatio < minimum) {
      failures.push(`Light theme ${description} contrast ${lightRatio.toFixed(2)} < ${minimum}`);
    }
    if (darkRatio < minimum) {
      failures.push(`Dark theme ${description} contrast ${darkRatio.toFixed(2)} < ${minimum}`);
    }
  }

  if (failures.length > 0) {
    console.error('Contrast violations detected:');
    failures.forEach((failure) => console.error(` - ${failure}`));
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
