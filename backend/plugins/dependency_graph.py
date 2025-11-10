"""Dependency analysis plugin for building import graphs and clustering files.

This plugin provides pure functions for analyzing code dependencies and creating
file clusters based on import relationships.
"""

from typing import Any, Dict, List, Optional
from typing_extensions import Annotated
from pydantic import Field

from backend.services.dependency_analyzer import DependencyAnalyzer


def analyze_dependencies(
    repo_root: Annotated[str, Field(description="Path to repository root directory")],
    files: Annotated[List[str], Field(description="List of relative file paths to analyze")],
    primary_language: Annotated[Optional[str], Field(description="Primary language (python, javascript, typescript, go)")] = None,
) -> Dict[str, List[str]]:
    """Build import/dependency graph for code files.

    Analyzes import statements across multiple languages and builds a graph showing
    which files depend on which other files. This is useful for understanding
    code organization and planning refactoring or documentation.

    Supported languages:
    - Python (.py): Parses `import` and `from ... import` statements using AST
    - JavaScript (.js, .jsx, .mjs, .cjs): Parses `import`/`require` using regex
    - TypeScript (.ts, .tsx): Parses `import` statements using regex
    - Go (.go): Parses `import` declarations using regex

    Args:
        repo_root: Absolute path to the repository root directory
        files: List of relative file paths to analyze (relative to repo_root)
        primary_language: Optional primary language hint (defaults to "python")

    Returns:
        Dictionary mapping file paths to lists of files they import/depend on.
        Only includes files that have dependencies.

    Example:
        {
            "src/main.py": ["src/utils.py", "src/config.py"],
            "src/utils.py": ["src/helpers.py"],
            "src/config.py": []
        }
    """
    analyzer = DependencyAnalyzer(repo_root=repo_root, primary_language=primary_language)
    return analyzer.build_import_graph(files)


def cluster_dependencies(
    repo_root: Annotated[str, Field(description="Path to repository root directory")],
    files: Annotated[List[str], Field(description="List of relative file paths to analyze")],
    primary_language: Annotated[Optional[str], Field(description="Primary language")] = None,
) -> List[Dict[str, List[str]]]:
    """Cluster files into connected components based on import relationships.

    This function groups files that depend on each other (directly or transitively)
    into clusters. Files in the same cluster are related through imports.
    Useful for:
    - Identifying independent modules
    - Planning documentation chapters
    - Organizing code reviews
    - Understanding system architecture

    Args:
        repo_root: Absolute path to the repository root directory
        files: List of relative file paths to analyze
        primary_language: Optional primary language hint

    Returns:
        List of cluster dictionaries, where each cluster is:
        {
            "cluster_N": ["file1.py", "file2.py", ...]
        }
        Clusters are ordered by size (largest first) for better narrative flow.

    Example:
        [
            {"cluster_1": ["api/routes.py", "api/handlers.py", "api/middleware.py"]},
            {"cluster_2": ["db/models.py", "db/migrations.py"]},
            {"cluster_3": ["utils/helpers.py"]}
        ]
    """
    analyzer = DependencyAnalyzer(repo_root=repo_root, primary_language=primary_language)
    return analyzer.plan_episodes(files)


def identify_architectural_layers(
    repo_root: Annotated[str, Field(description="Path to repository root directory")],
    files: Annotated[List[str], Field(description="List of relative file paths to analyze")],
    primary_language: Annotated[Optional[str], Field(description="Primary language")] = None,
) -> Dict[str, Any]:
    """Identify architectural layers (API, business logic, data access, etc.) from file paths.

    Uses path heuristics to classify files into architectural layers:
    - API: api/, routes/, controllers/, endpoints/, handlers/, views/
    - Business Logic: services/, domain/, business/, core/, logic/
    - Data Access: models/, db/, database/, repositories/, entities/
    - Infrastructure: utils/, helpers/, common/, shared/, lib/
    - Configuration: config/, settings/, env/
    - Testing: tests/, test/, *.test.*, *.spec.*

    Args:
        repo_root: Absolute path to the repository root directory
        files: List of relative file paths to analyze
        primary_language: Optional primary language hint

    Returns:
        Dictionary mapping layer names to their representative clusters:
        {
            "API": {
                "files": ["api/routes.py", "api/handlers.py"],
                "cluster_index": 1
            },
            "Business Logic": {
                "files": ["services/user.py", "domain/models.py"],
                "cluster_index": 2
            },
            ...
        }
    """
    analyzer = DependencyAnalyzer(repo_root=repo_root, primary_language=primary_language)
    graph = analyzer.build_import_graph(files)
    clusters = analyzer.cluster_graph(graph)
    layers = analyzer.identify_architectural_layers(clusters)

    # Convert ClusterPlan objects to serializable dictionaries
    result = {}
    for layer_name, cluster in layers.items():
        result[layer_name] = {
            "files": sorted(list(cluster.files)),
            "cluster_index": cluster.index,
            "architectural_layer": cluster.architectural_layer,
        }

    return result


def build_python_import_graph(
    repo_root: Annotated[str, Field(description="Path to repository root directory")],
    files: Annotated[List[str], Field(description="List of Python file paths (*.py)")],
) -> Dict[str, List[str]]:
    """Build import graph for Python files only using AST parsing.

    This is a specialized version of analyze_dependencies that only processes
    Python files and uses the AST parser for more accurate import detection.

    Args:
        repo_root: Absolute path to the repository root directory
        files: List of relative Python file paths (should be *.py files)

    Returns:
        Dictionary mapping Python files to their imports

    Example:
        {
            "src/main.py": ["src.utils", "src.config"],
            "src/utils.py": ["src.helpers"],
        }
    """
    analyzer = DependencyAnalyzer(repo_root=repo_root, primary_language="python")
    return analyzer.build_python_import_graph(files)
