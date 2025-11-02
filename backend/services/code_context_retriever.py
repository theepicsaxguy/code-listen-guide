"""Code context retrieval service for episodes.

Retrieves file contents and code snippets for episode dialogue generation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CodeContextRetriever:
    """Retrieves code context for episode file clusters."""

    def __init__(self, repo_root: str) -> None:
        """Initialize retriever with repository root path."""
        self.repo_root = Path(repo_root)

    def get_file_content(self, file_path: str, max_lines: int = 200) -> Optional[str]:
        """Read file content, limiting to first N lines for token efficiency.
        
        Args:
            file_path: Relative path from repo root
            max_lines: Maximum number of lines to read
            
        Returns:
            File content as string, or None if file doesn't exist
        """
        full_path = self.repo_root / file_path
        if not full_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            lines = full_path.read_text(encoding='utf-8', errors='ignore').splitlines()
            if len(lines) > max_lines:
                content = '\n'.join(lines[:max_lines])
                return f"{content}\n... (truncated, {len(lines)} total lines)"
            return '\n'.join(lines)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None

    def get_cluster_context(
        self,
        file_clusters: Dict[str, List[str]],
        max_files_per_cluster: int = 5,
        max_lines_per_file: int = 150,
    ) -> Dict[str, List[Dict[str, str]]]:
        """Get code context for all files in clusters.
        
        Args:
            file_clusters: Dictionary mapping cluster names to file lists
            max_files_per_cluster: Limit files per cluster to avoid token bloat
            max_lines_per_file: Limit lines per file
            
        Returns:
            Dictionary mapping cluster names to lists of {file, content} dicts
        """
        context: Dict[str, List[Dict[str, str]]] = {}
        
        for cluster_name, files in file_clusters.items():
            # Limit files per cluster
            files_to_read = files[:max_files_per_cluster]
            cluster_content = []
            
            for file_path in files_to_read:
                content = self.get_file_content(file_path, max_lines=max_lines_per_file)
                if content:
                    cluster_content.append({
                        "file": file_path,
                        "content": content,
                    })
            
            if cluster_content:
                context[cluster_name] = cluster_content
        
        return context

    def get_episode_code_snippets(
        self,
        episode_file_clusters: Dict[str, List[str]],
        dependency_graph: Optional[Dict[str, List[str]]] = None,
    ) -> List[str]:
        """Get curated code snippets for episode dialogue generation.
        
        Returns a flat list of formatted code snippets suitable for LLM context.
        Each snippet includes file path and content preview.
        
        Args:
            episode_file_clusters: Episode's file clusters
            dependency_graph: Optional dependency graph for context
            
        Returns:
            List of formatted code snippets (strings)
        """
        snippets: List[str] = []
        context = self.get_cluster_context(episode_file_clusters)
        
        for cluster_name, files_with_content in context.items():
            for file_info in files_with_content:
                snippet = f"File: {file_info['file']}\n```\n{file_info['content']}\n```"
                snippets.append(snippet)
        
        return snippets


def retrieve_episode_code_context(
    repo_root: str,
    episode_file_clusters: Dict[str, List[str]],
    dependency_graph: Optional[Dict[str, List[str]]] = None,
) -> List[str]:
    """Convenience function to retrieve code context for an episode.
    
    Args:
        repo_root: Repository root path
        episode_file_clusters: Episode's file clusters
        dependency_graph: Optional dependency graph
        
    Returns:
        List of formatted code snippets
    """
    retriever = CodeContextRetriever(repo_root)
    return retriever.get_episode_code_snippets(episode_file_clusters, dependency_graph)


__all__ = ["CodeContextRetriever", "retrieve_episode_code_context"]
