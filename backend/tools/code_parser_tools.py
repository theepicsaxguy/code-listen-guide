"""
Code parsing tools for repository analysis.

This module provides tools for parsing and analyzing code repositories.
"""

from pathlib import Path
from typing import Dict, Any


def _ai_parse_repository(repo_path: str) -> dict:
    """
    Parse repository structure and extract code information.
    
    Args:
        repo_path: Path to the cloned repository directory
    
    Returns:
        Dictionary with analysis results including:
        - languages: List of programming languages detected
        - file_count: Total number of code files
        - structure: Directory structure overview
        - dependencies: Detected dependencies (if applicable)
    """
    try:
        repo = Path(repo_path)
        
        if not repo.exists() or not repo.is_dir():
            return {
                "error": f"Repository path does not exist: {repo_path}",
                "analysis": {}
            }
        
        # Count files by extension
        extensions = {}
        total_files = 0
        
        for file_path in repo.rglob("*"):
            if file_path.is_file() and ".git" not in file_path.parts:
                ext = file_path.suffix.lower()
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
                    total_files += 1
        
        # Map extensions to languages
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React",
            ".tsx": "React/TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".sh": "Shell",
            ".sql": "SQL",
            ".md": "Markdown",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".xml": "XML",
            ".html": "HTML",
            ".css": "CSS",
        }
        
        languages = {}
        for ext, count in extensions.items():
            lang = language_map.get(ext, ext)
            languages[lang] = languages.get(lang, 0) + count
        
        # Get directory structure (top level only)
        structure = []
        for item in repo.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_dir():
                structure.append(f"{item.name}/")
            else:
                structure.append(item.name)
        
        # Try to detect dependencies from common files
        dependencies = []
        
        # Python
        requirements_file = repo / "requirements.txt"
        if requirements_file.exists():
            dependencies.append("Python dependencies found in requirements.txt")
        
        # Node.js
        package_json = repo / "package.json"
        if package_json.exists():
            dependencies.append("Node.js dependencies found in package.json")
        
        # Go
        go_mod = repo / "go.mod"
        if go_mod.exists():
            dependencies.append("Go dependencies found in go.mod")
        
        # Rust
        cargo_toml = repo / "Cargo.toml"
        if cargo_toml.exists():
            dependencies.append("Rust dependencies found in Cargo.toml")
        
        analysis = {
            "languages": languages,
            "file_count": total_files,
            "extension_breakdown": extensions,
            "structure": structure,
            "dependencies": dependencies,
            "repo_name": repo.name,
        }
        
        return {"analysis": analysis}
        
    except Exception as e:
        return {
            "error": str(e),
            "analysis": {}
        }
