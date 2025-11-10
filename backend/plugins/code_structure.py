"""Code structure analysis plugin using tree-sitter.

This plugin provides pure functions for analyzing code structure and extracting
rich metadata from source files.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from typing_extensions import Annotated
from pydantic import Field

from backend.services.code_analyzer import CodeAnalyzer


def analyze_code_structure(
    file_path: Annotated[str, Field(description="Path to the code file to analyze")],
    content: Annotated[Optional[str], Field(description="Optional file content (if not provided, will read from file_path)")] = None,
) -> Dict[str, Any]:
    """Analyze code structure using tree-sitter for deep metadata extraction.

    This function performs comprehensive analysis on a code file and returns rich metadata including:
    - Functions with signatures, parameters, return types, decorators, complexity
    - Classes with base classes, methods, properties, inheritance
    - Imports and exports with module resolution
    - Call graphs showing function invocation relationships
    - Code metrics (LOC, cyclomatic complexity, comment ratio)
    - Documentation extraction (docstrings, comments)
    - Dependencies and references

    Supports: Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, C#

    Args:
        file_path: Absolute path to the code file to analyze
        content: Optional file content string. If not provided, reads from file_path

    Returns:
        Dictionary containing:
        - language: Detected programming language
        - functions: List of function metadata (name, parameters, complexity, etc.)
        - classes: List of class metadata (name, methods, inheritance, etc.)
        - imports: List of import statements with module and items
        - exports: List of exported symbols
        - call_graph: Dictionary mapping functions to their callers/callees
        - metrics: Code statistics (lines, complexity, comments, etc.)
        - documentation: Extracted docstrings and comments
        - dependencies: Module dependency information
        - metadata: Additional file-level metadata

    Example return structure:
        {
            "language": "python",
            "functions": [
                {
                    "name": "process_data",
                    "line_start": 42,
                    "line_end": 67,
                    "parameters": [{"name": "data", "type": "Dict[str, Any]"}],
                    "return_type": "bool",
                    "docstring": "Process incoming data...",
                    "complexity": 5,
                    "is_async": False,
                    "calls": ["validate_data", "save_result"]
                }
            ],
            "classes": [...],
            "imports": [...],
            "call_graph": {...},
            "metrics": {
                "total_lines": 150,
                "code_lines": 120,
                "comment_lines": 20,
                "blank_lines": 10,
                "cyclomatic_complexity": 15,
                "function_count": 8,
                "class_count": 2
            }
        }
    """
    analyzer = CodeAnalyzer()
    return analyzer.analyze_file(Path(file_path), content)


def analyze_code_file_by_language(
    file_path: Annotated[str, Field(description="Path to the code file")],
    language: Annotated[str, Field(description="Programming language (python, javascript, typescript, go, rust, java, cpp, csharp)")],
    content: Annotated[Optional[str], Field(description="Optional file content")] = None,
) -> Dict[str, Any]:
    """Analyze code structure with explicit language specification.

    Use this when you know the language and want to bypass language detection.
    Useful for files without extensions or with ambiguous extensions.

    Args:
        file_path: Path to the code file
        language: Programming language identifier
        content: Optional file content

    Returns:
        Same structure as analyze_code_structure
    """
    analyzer = CodeAnalyzer()

    # Override language detection by temporarily replacing the file extension
    original_path = Path(file_path)

    # Map language names to file extensions for tree-sitter
    language_extensions = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "go": ".go",
        "rust": ".rs",
        "java": ".java",
        "cpp": ".cpp",
        "csharp": ".cs",
        "c": ".c",
    }

    extension = language_extensions.get(language.lower(), original_path.suffix)

    # Create a temporary path with the correct extension for language detection
    temp_path = original_path.with_suffix(extension)

    result = analyzer.analyze_file(temp_path, content)
    result["language"] = language.lower()
    result["original_path"] = str(original_path)

    return result


def detect_file_language(
    file_path: Annotated[str, Field(description="Path to the code file")],
) -> str:
    """Detect the programming language of a file based on extension and content.

    Args:
        file_path: Path to the code file

    Returns:
        Language identifier string (e.g., 'python', 'javascript', 'typescript')
        Returns 'unknown' if language cannot be detected
    """
    analyzer = CodeAnalyzer()
    return analyzer.detect_language(Path(file_path)) or "unknown"
