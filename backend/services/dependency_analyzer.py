"""Minimal dependency analyzer service for Episode planning.

This is an MVP implementation providing:
 - Basic Python import graph extraction via ast
 - JavaScript/TypeScript import extraction via regex
 - Go import extraction via regex
 - Naive connected-component clustering over file dependency graph
 - Simple heuristic episode planning (clusters ordered by size)

Future enhancements (planned):
 - Tree-sitter integration for more robust parsing
 - Architectural layer detection (API, domain, persistence)
 - Graph centrality metrics to inform ordering
 - Intelligent merging/splitting for duration targets
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Iterable
import ast
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClusterPlan:
    files: Set[str]
    index: int
    architectural_layer: str | None = None

    def to_dict(self) -> Dict[str, List[str]]:
        return {f"cluster_{self.index}": sorted(self.files)}


class DependencyAnalyzer:
    def __init__(self, repo_root: str, primary_language: str | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.primary_language = primary_language or "python"

    # ----------------------------- Public API ----------------------------- #
    def build_import_graph(self, files: Iterable[str]) -> Dict[str, List[str]]:
        """Build import graph for all supported languages.
        
        Supports:
        - Python (.py)
        - JavaScript (.js, .jsx, .mjs, .cjs)
        - TypeScript (.ts, .tsx)
        - Go (.go)
        """
        graph: Dict[str, List[str]] = {}
        for rel in files:
            abs_path = self.repo_root / rel
            if not abs_path.exists():
                continue
            
            try:
                imports = []
                if rel.endswith('.py'):
                    imports = self._parse_python_imports(abs_path)
                elif rel.endswith(('.js', '.jsx', '.mjs', '.cjs')):
                    imports = self._parse_javascript_imports(abs_path)
                elif rel.endswith(('.ts', '.tsx')):
                    imports = self._parse_typescript_imports(abs_path)
                elif rel.endswith('.go'):
                    imports = self._parse_go_imports(abs_path)
                
                if imports:
                    graph[rel] = imports
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("Failed parsing imports for %s: %s", rel, e)
        return graph
    
    def build_python_import_graph(self, files: Iterable[str]) -> Dict[str, List[str]]:
        """Build import graph for Python files only (legacy method)."""
        graph: Dict[str, List[str]] = {}
        for rel in files:
            if not rel.endswith('.py'):
                continue
            abs_path = self.repo_root / rel
            if not abs_path.exists():
                continue
            try:
                graph[rel] = self._parse_python_imports(abs_path)
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("Failed parsing imports for %s: %s", rel, e)
        return graph

    def cluster_graph(self, graph: Dict[str, List[str]]) -> List[ClusterPlan]:
        # Undirected connectivity for naive grouping
        adjacency: Dict[str, Set[str]] = {n: set(deps) for n, deps in graph.items()}
        for node, deps in graph.items():
            for dep in deps:
                adjacency.setdefault(dep, set()).add(node)

        visited: Set[str] = set()
        clusters: List[ClusterPlan] = []

        def dfs(start: str, acc: Set[str]):
            if start in visited:
                return
            visited.add(start)
            acc.add(start)
            for nxt in adjacency.get(start, ()):  # breadth/ depth hybrid trivial
                dfs(nxt, acc)

        for node in adjacency:
            if node not in visited:
                acc: Set[str] = set()
                dfs(node, acc)
                clusters.append(ClusterPlan(files=acc, index=len(clusters) + 1))

        # Order largest to smallest for provisional narrative flow
        clusters.sort(key=lambda c: (-len(c.files), c.index))
        # Reindex after sort
        for i, c in enumerate(clusters, start=1):
            c.index = i
        return clusters

    def plan_episodes(self, files: List[str], target_max_files: int | None = None) -> List[Dict[str, List[str]]]:
        graph = self.build_import_graph(files)
        clusters = self.cluster_graph(graph)
        clusters = self._merge_small_clusters(clusters, graph, min_size=2)
        plans: List[Dict[str, List[str]]] = []
        for cluster in clusters:
            plans.append(cluster.to_dict())
        return plans

    def identify_architectural_layers(self, clusters: List[ClusterPlan]) -> Dict[str, ClusterPlan]:
        """Identify architectural layers for clusters using path heuristics.

        Heuristic mapping of common directory / filename conventions to
        architectural concerns. A cluster may contain files spanning more than
        one layer. We (a) record the list of matched layers internally and (b)
        select a *primary* layer based on specificity priority for the
        `architectural_layer` attribute. The returned mapping exposes the most
        representative cluster per layer (largest cluster assigned that layer).

        Layer detection directories / patterns:
          API: api/, routes/, controllers/, endpoints/, handlers/, views/
          Business Logic: services/, domain/, business/, core/, logic/, use_cases/, usecases/
          Data Access: models/, db/, database/, repositories/, dao/, entities/, schemas/
          Infrastructure: utils/, helpers/, common/, shared/, lib/, infrastructure/
          Configuration: config/, settings/, env/
          Testing: tests/, test/, __tests__/, spec/, *.test.*, *.spec.*

        Specificity (priority) order for assigning a primary layer:
            API > Business Logic > Data Access > Infrastructure > Configuration > Testing

        (Items earlier in the list have higher precedence.)

        Args:
            clusters: dependency clusters to classify

        Returns:
            Dict[layer_name, ClusterPlan] mapping each layer to the *largest*
            cluster whose primary layer resolved to that name. Layers with no
            matching clusters are omitted. An additional "Uncategorized" key
            may exist if at least one cluster failed to match any heuristic.
        """
        # Priority list (index used for comparison; lower index => higher priority)
        priority = [
            "API",
            "Business Logic",
            "Data Access",
            "Infrastructure",
            "Configuration",
            "Testing",
        ]

        # Directory / filename fragments per layer (all lowercase comparisons)
        layer_dir_map: Dict[str, List[str]] = {
            "API": ["api/", "routes/", "controllers/", "endpoints/", "handlers/", "views/"],
            "Business Logic": ["services/", "domain/", "business/", "core/", "logic/", "use_cases/", "usecases/"],
            "Data Access": ["models/", "db/", "database/", "repositories/", "dao/", "entities/", "schemas/"],
            "Infrastructure": ["utils/", "helpers/", "common/", "shared/", "lib/", "infrastructure/"],
            "Configuration": ["config/", "settings/", "env/"],
            "Testing": ["tests/", "test/", "__tests__/", "spec/"],
        }

        # Pattern indicators for test files by filename (not necessarily directory based)
        test_file_indicators = [".test.", ".spec."]

        # Result mapping (largest cluster per layer). Using Dict[str, ClusterPlan]
        result: Dict[str, ClusterPlan] = {}

        def choose_primary(matched: Set[str]) -> str:
            if not matched:
                return "Uncategorized"
            # Return the first layer encountered in priority ordering
            for layer_name in priority:
                if layer_name in matched:
                    return layer_name
            # Fallback shouldn't occur but guard anyway
            return sorted(matched)[0]

        for cluster in clusters:
            matched_layers: Set[str] = set()
            for file_path in cluster.files:
                p = file_path.replace('\\', '/').lower()
                # Test filename patterns (independent of directory)
                if any(ind in p for ind in test_file_indicators):
                    matched_layers.add("Testing")
                # Directory / path fragments
                for layer_name, fragments in layer_dir_map.items():
                    for frag in fragments:
                        if frag in p:
                            matched_layers.add(layer_name)
                            break
            primary = choose_primary(matched_layers)
            cluster.architectural_layer = primary

            # Update result mapping to retain the *largest* cluster per layer
            if primary not in result or len(cluster.files) > len(result[primary].files):
                result[primary] = cluster

        return result

    # --------------------------- Internal Helpers ------------------------- #
    def _parse_python_imports(self, path: Path) -> List[str]:
        """Parse Python imports using AST."""
        src = path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(src)
        imports: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        # Filter stdlib-ish heuristics: keep relative intra-repo style modules
        filtered: List[str] = []
        for name in imports:
            if '/' in name or '.' in name:
                filtered.append(name.replace('.', '/'))
        return filtered

    def _parse_javascript_imports(self, path: Path) -> List[str]:
        """Parse JavaScript/JSX imports using regex.
        
        Detects:
        - import { X } from 'module'
        - import X from 'module'
        - import * as X from 'module'
        - const X = require('module')
        - export { X } from 'module'
        """
        src = path.read_text(encoding='utf-8', errors='ignore')
        imports: List[str] = []
        
        # ES6 import statements
        # Match: import ... from 'module' or import ... from "module"
        es6_pattern = r"import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)(?:\s*,\s*(?:\{[^}]*\}|\w+))*\s+from\s+)?['\"]([^'\"]+)['\"]"
        for match in re.finditer(es6_pattern, src):
            imports.append(match.group(1))
        
        # CommonJS require
        # Match: require('module') or require("module")
        require_pattern = r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
        for match in re.finditer(require_pattern, src):
            imports.append(match.group(1))
        
        # Export from statements
        # Match: export ... from 'module'
        export_pattern = r"export\s+(?:\{[^}]*\}|\*)\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(export_pattern, src):
            imports.append(match.group(1))
        
        # Filter to keep only relative imports (starting with . or ..)
        filtered: List[str] = []
        for imp in imports:
            if imp.startswith('.'):
                # Normalize path: remove .js, .jsx, etc., convert to forward slashes
                normalized = imp.replace('\\', '/')
                # Remove file extensions
                for ext in ['.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx']:
                    if normalized.endswith(ext):
                        normalized = normalized[:-len(ext)]
                        break
                filtered.append(normalized)
        
        return filtered

    def _parse_typescript_imports(self, path: Path) -> List[str]:
        """Parse TypeScript/TSX imports using regex.
        
        TypeScript uses the same import syntax as JavaScript, so we delegate
        to the JavaScript parser.
        """
        return self._parse_javascript_imports(path)

    def _parse_go_imports(self, path: Path) -> List[str]:
        """Parse Go imports using regex.
        
        Detects:
        - import "package"
        - import alias "package"
        - import ( ... ) blocks
        """
        src = path.read_text(encoding='utf-8', errors='ignore')
        imports: List[str] = []
        
        # Single line import: import "package" or import alias "package"
        single_pattern = r'import\s+(?:\w+\s+)?"([^"]+)"'
        for match in re.finditer(single_pattern, src):
            imports.append(match.group(1))
        
        # Multi-line import block
        # Match: import ( ... )
        block_pattern = r'import\s*\(\s*((?:[^)]*\n?)*)\s*\)'
        for match in re.finditer(block_pattern, src, re.MULTILINE):
            block_content = match.group(1)
            # Extract package paths from the block
            # Format: "package" or alias "package"
            package_pattern = r'(?:\w+\s+)?"([^"]+)"'
            for pkg_match in re.finditer(package_pattern, block_content):
                imports.append(pkg_match.group(1))
        
        # Filter to keep only local imports (those that start with the module path)
        # Go convention: relative imports are discouraged, but we can detect
        # imports that don't start with standard library or third-party indicators
        filtered: List[str] = []
        stdlib_prefixes = ['fmt', 'os', 'io', 'net', 'http', 'strings', 'time', 'context', 'sync', 'errors']
        for imp in imports:
            # Keep imports that have slashes (likely project imports)
            # or are relative (starting with .)
            if '/' in imp or imp.startswith('.'):
                # Skip obvious third-party (github.com, golang.org, etc.)
                if not any(imp.startswith(prefix) for prefix in ['github.com', 'golang.org', 'google.golang.org', 'gopkg.in']):
                    filtered.append(imp)
        
        return filtered

    # -------------------------- Cluster Refinement ----------------------- #
    def _merge_small_clusters(
        self,
        clusters: List[ClusterPlan],
        graph: Dict[str, List[str]],
        min_size: int = 2,
    ) -> List[ClusterPlan]:
        """Merge undersized clusters into the most connected neighbor.

        Heuristic rationale:
        - Single-file (or tiny) clusters rarely provide enough narrative depth.
        - Merge target chosen by maximum bidirectional edge weight (imports between files).
        - After each merge, clusters are re-sorted by size for stable ordering.

        This remains intentionally simple until richer architectural signals are added.
        """
        if not clusters:
            return clusters

        # Build a quick lookup from file -> cluster index
        def cluster_index_map(cls: List[ClusterPlan]) -> Dict[str, int]:
            mapping: Dict[str, int] = {}
            for i, c in enumerate(cls):
                for f in c.files:
                    mapping[f] = i
            return mapping

        def inter_cluster_weight(c1: ClusterPlan, c2: ClusterPlan) -> int:
            weight = 0
            for f in c1.files:
                deps = set(graph.get(f, []))
                weight += len([d for d in deps if d in c2.files])
            for f in c2.files:
                deps = set(graph.get(f, []))
                weight += len([d for d in deps if d in c1.files])
            return weight

        changed = True
        while changed:
            changed = False
            # Identify smallest clusters below threshold
            small = [c for c in clusters if len(c.files) < min_size]
            if not small:
                break
            for sc in small:
                # Find best merge candidate (exclude itself)
                candidates = [c for c in clusters if c is not sc]
                if not candidates:
                    continue
                best = max(candidates, key=lambda c: inter_cluster_weight(sc, c))
                # Merge files
                best.files.update(sc.files)
                clusters.remove(sc)
                changed = True
            # Re-sort and reindex if any merge happened
            if changed:
                clusters.sort(key=lambda c: (-len(c.files), c.index))
                for i, c in enumerate(clusters, start=1):
                    c.index = i
        return clusters


__all__ = ["DependencyAnalyzer", "ClusterPlan"]
