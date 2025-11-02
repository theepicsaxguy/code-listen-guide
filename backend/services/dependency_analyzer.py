"""Minimal dependency analyzer service for Episode planning.

This is an MVP implementation providing:
 - Basic Python import graph extraction via ast
 - Naive connected-component clustering over file dependency graph
 - Simple heuristic episode planning (clusters ordered by size)

Future enhancements (planned):
 - Multi-language parsing (TS/JS, Go, Rust, etc.)
 - Architectural layer detection (API, domain, persistence)
 - Graph centrality metrics to inform ordering
 - Intelligent merging/splitting for duration targets
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Iterable
import ast
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClusterPlan:
    files: Set[str]
    index: int

    def to_dict(self) -> Dict[str, List[str]]:
        return {f"cluster_{self.index}": sorted(self.files)}


class DependencyAnalyzer:
    def __init__(self, repo_root: str, primary_language: str | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.primary_language = primary_language or "python"

    # ----------------------------- Public API ----------------------------- #
    def build_python_import_graph(self, files: Iterable[str]) -> Dict[str, List[str]]:
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
        graph = self.build_python_import_graph(files)
        clusters = self.cluster_graph(graph)
        plans: List[Dict[str, List[str]]] = []
        for cluster in clusters:
            plans.append(cluster.to_dict())
        return plans

    # --------------------------- Internal Helpers ------------------------- #
    def _parse_python_imports(self, path: Path) -> List[str]:
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


__all__ = ["DependencyAnalyzer", "ClusterPlan"]
