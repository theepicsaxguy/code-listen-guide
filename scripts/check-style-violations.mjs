import { readdir, readFile } from 'node:fs/promises';
import { extname, join } from 'node:path';

const TARGET_EXTENSIONS = new Set(['.ts', '.tsx', '.css', '.md', '.mdx']);
const FORBIDDEN_PATTERNS = [
  { regex: /bg-gradient-(?:primary|card|stat)/, message: 'Found banned gradient utility class' },
  { regex: /shadow-glow/, message: 'Found banned glow shadow class' },
  { regex: /hover-glow/, message: 'Found banned glow hover class' },
  { regex: /card-elevation/, message: 'Found banned elevation helper class' },
  { regex: /text-white\b/, message: 'Found banned white text utility' },
  { regex: /border-white\b/, message: 'Found banned white border utility' },
  { regex: /bg-white\b/, message: 'Found banned white background utility' },
  { regex: /bg-gray-(?:7|8|9)\d?\b/, message: 'Found banned gray background utility' },
  { regex: /border-gray-7\d\b/, message: 'Found banned gray border utility' },
];
const HEX_COLOR_REGEX = /#(?:[0-9a-fA-F]{3,8})\b/;

const violations = [];

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue;
    if (entry.name === 'node_modules' || entry.name === 'build') continue;
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      await walk(fullPath);
      continue;
    }
    if (!TARGET_EXTENSIONS.has(extname(entry.name))) continue;
    const content = await readFile(fullPath, 'utf8');
    FORBIDDEN_PATTERNS.forEach(({ regex, message }) => {
      if (regex.test(content)) {
        violations.push({ file: fullPath, message });
      }
    });
    if (HEX_COLOR_REGEX.test(content)) {
      // allow hash anchors in markdown links
      const filtered = content.replace(/https?:\/\/[^\s)]+/g, '');
      if (HEX_COLOR_REGEX.test(filtered)) {
        violations.push({ file: fullPath, message: 'Found raw hex color literal' });
      }
    }
  }
}

const roots = ['src'];
const extraFiles = ['tailwind.config.ts', 'src/index.css'];

for (const root of roots) {
  try {
    await walk(root);
  } catch (error) {
    if (error.code !== 'ENOENT') {
      throw error;
    }
  }
}

for (const file of extraFiles) {
  try {
    const content = await readFile(file, 'utf8');
    FORBIDDEN_PATTERNS.forEach(({ regex, message }) => {
      if (regex.test(content)) {
        violations.push({ file, message });
      }
    });
    if (HEX_COLOR_REGEX.test(content.replace(/https?:\/\/[^\s)]+/g, ''))) {
      violations.push({ file, message: 'Found raw hex color literal' });
    }
  } catch (error) {
    if (error.code !== 'ENOENT') {
      throw error;
    }
  }
}

if (violations.length > 0) {
  console.error('Style violations detected:');
  for (const violation of violations) {
    console.error(` - ${violation.file}: ${violation.message}`);
  }
  process.exit(1);
}
