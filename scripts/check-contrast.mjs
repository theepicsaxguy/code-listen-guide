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

function parseHsl(hslString) {
  // Parse hsl(220 15% 10%) format
  const match = hslString.match(/hsl\((\d+)\s+(\d+)%\s+(\d+)%\)/);
  if (match) {
    return [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
  }
  // Fallback: try parsing space-separated format
  const parts = hslString.trim().split(/\s+/);
  if (parts.length === 3) {
    return parts.map(p => parseInt(p.replace('%', '')));
  }
  throw new Error(`Invalid HSL format: ${hslString}`);
}

function contrastRatio(colorA, colorB) {
  const [h1, s1, l1] = parseHsl(colorA);
  const [h2, s2, l2] = parseHsl(colorB);
  const lumA = relativeLuminance(hslToRgb(h1, s1, l1));
  const lumB = relativeLuminance(hslToRgb(h2, s2, l2));
  const lighter = Math.max(lumA, lumB);
  const darker = Math.min(lumA, lumB);
  return (lighter + 0.05) / (darker + 0.05);
}

async function main() {
  // Read from index.css where @theme defines colors
  const css = await readFile('src/index.css', 'utf8');
  const tokens = { dark: {}, light: {} };
  
  // Extract colors from @theme block (dark theme defaults)
  const themeMatch = css.match(/@theme\s*\{([\s\S]+?)\n\}/);
  if (!themeMatch) {
    throw new Error('Could not find @theme block in index.css');
  }
  
  const themeContent = themeMatch[1];
  
  // Extract dark theme colors (default in @theme)
  const darkColorMatches = [...themeContent.matchAll(/--color-([\w-]+):\s*hsl\(([^)]+)\)/g)];
  for (const match of darkColorMatches) {
    tokens.dark[match[1]] = `hsl(${match[2]})`;
  }
  
  // Extract light theme colors from [data-theme="light"] block
  const lightThemeMatch = css.match(/\[data-theme="light"\]\s*\{([\s\S]+?)\n\s*\}/);
  if (lightThemeMatch) {
    const lightContent = lightThemeMatch[1];
    const lightColorMatches = [...lightContent.matchAll(/--color-([\w-]+):\s*hsl\(([^)]+)\)/g)];
    for (const match of lightColorMatches) {
      tokens.light[match[1]] = `hsl(${match[2]})`;
    }
  }
  
  // Fill in any missing light theme tokens with dark theme values
  for (const key in tokens.dark) {
    if (!tokens.light[key]) {
      tokens.light[key] = tokens.dark[key];
    }
  }
  
  // Map token names to CSS variable names
  const tokenMap = {
    text: 'foreground',
    background: 'background',
    surface: 'surface',
    muted: 'muted-foreground',
    primary: 'primary',
    border: 'border',
  };
  
  const getTokenValue = (theme, tokenName) => {
    const mappedToken = tokenMap[tokenName] || tokenName;
    return theme[mappedToken];
  };
  
  const ensureTokens = (theme, required) => {
    return required.every((token) => {
      const value = getTokenValue(theme, token);
      return typeof value === 'string' && value.length > 0;
    });
  };
  
  const checks = [
    { tokens: ['text', 'background'], minimum: 4.5, description: 'text on background' },
    { tokens: ['text', 'surface'], minimum: 4.5, description: 'text on surface' },
    { tokens: ['muted', 'surface'], minimum: 4.5, description: 'muted text on surface' },
    { tokens: ['primary', 'background'], minimum: 3, description: 'primary on background (UI element, 3:1 minimum)' },
    { tokens: ['border', 'surface'], minimum: 3, description: 'border on surface' },
  ];
  
  const failures = [];
  for (const { tokens: tokenPair, minimum, description } of checks) {
    const [tokenA, tokenB] = tokenPair;
    
    if (!ensureTokens(tokens.light, tokenPair) || !ensureTokens(tokens.dark, tokenPair)) {
      failures.push(`Missing tokens for ${description} (looking for ${tokenPair.map(t => tokenMap[t] || t).join(', ')})`);
      continue;
    }
    
    const lightA = getTokenValue(tokens.light, tokenA);
    const lightB = getTokenValue(tokens.light, tokenB);
    const darkA = getTokenValue(tokens.dark, tokenA);
    const darkB = getTokenValue(tokens.dark, tokenB);
    
    const lightRatio = contrastRatio(lightA, lightB);
    const darkRatio = contrastRatio(darkA, darkB);
    
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
  
  console.log('All contrast checks passed!');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
