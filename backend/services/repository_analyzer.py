"""
Repository analysis service for code structure extraction.

This service provides two analysis modes:
1. Docling Pipeline (recommended): Advanced parsing with Docling
2. Tree-sitter Parser (fallback): Basic parsing for unsupported files

The Docling pipeline provides:
- Rich document parsing (code, markdown, JSON, YAML)
- Content cleaning and normalization
- Semantic tagging and classification
- Dependency graph generation
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import shutil

try:
    from git import Repo
    HAS_GIT = True
except ImportError:
    HAS_GIT = False

try:
    from backend.services.docling_pipeline import DoclingPipeline
    HAS_DOCLING_PIPELINE = True
except ImportError:
    HAS_DOCLING_PIPELINE = False

from backend.tools.code_parser_tools import build_code_map

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """
    Analyzes GitHub repositories to extract code structure.

    Supports two analysis modes:
    1. Docling Pipeline (default): Advanced parsing with content cleaning and tagging
    2. Tree-sitter (fallback): Basic AST parsing
    """

    def __init__(
        self,
        repo_url: str,
        git_ref: str = "main",
        use_docling: bool = True,
        max_repo_size_mb: int = 500,
    ):
        """
        Initialize repository analyzer.

        Args:
            repo_url: GitHub repository URL
            git_ref: Git branch or tag to analyze
            use_docling: Use Docling pipeline if available
            max_repo_size_mb: Maximum repository size to analyze
        """
        self.repo_url = repo_url
        self.git_ref = git_ref
        self.use_docling = use_docling and HAS_DOCLING_PIPELINE
        self.max_repo_size_mb = max_repo_size_mb
        self.temp_dir: Optional[Path] = None

        # Initialize Docling pipeline if requested
        if self.use_docling:
            try:
                self.docling_pipeline = DoclingPipeline(
                    enable_code_enrichment=True,
                    enable_formula_enrichment=False,
                )
                logger.info("Initialized Docling pipeline for analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize Docling: {e}. Falling back to tree-sitter")
                self.use_docling = False

    async def clone_repository(self) -> Path:
        """
        Clone repository to temporary directory.

        Returns:
            Path to cloned repository

        Raises:
            RuntimeError: If git is not available or clone fails
            ValueError: If repository is too large
        """
        if not HAS_GIT:
            raise RuntimeError("GitPython not installed. Install with: pip install gitpython")

        try:
            # Create temporary directory
            self.temp_dir = Path(tempfile.mkdtemp(prefix="repo_analysis_"))
            logger.info(f"Cloning {self.repo_url} to {self.temp_dir}")

            # Clone with depth=1 for speed (shallow clone)
            repo = Repo.clone_from(
                self.repo_url,
                self.temp_dir,
                branch=self.git_ref,
                depth=1,
            )

            # Check repository size
            repo_size_mb = self._get_directory_size(self.temp_dir) / (1024 * 1024)
            if repo_size_mb > self.max_repo_size_mb:
                raise ValueError(
                    f"Repository size ({repo_size_mb:.1f}MB) exceeds "
                    f"maximum allowed ({self.max_repo_size_mb}MB)"
                )

            logger.info(
                f"Successfully cloned repository (size: {repo_size_mb:.1f}MB, "
                f"commit: {repo.head.commit.hexsha[:8]})"
            )

            return self.temp_dir

        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            self.cleanup()
            raise

    async def analyze_structure(self, repo_path: Path) -> Dict:
        """
        Analyze repository structure and collect metadata.

        Returns:
            Dictionary with file listings, language detection, and statistics
        """
        logger.info(f"Analyzing repository structure at {repo_path}")

        files_metadata = []
        languages = set()
        total_size = 0
        file_count = 0

        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip ignored paths
            if self._should_ignore(file_path):
                continue

            file_count += 1
            file_size = file_path.stat().st_size
            total_size += file_size

            # Detect language
            language = self._detect_language(file_path)
            if language:
                languages.add(language)

            files_metadata.append({
                "path": str(file_path.relative_to(repo_path)),
                "size_bytes": file_size,
                "language": language,
            })

        return {
            "files": files_metadata,
            "languages": list(languages),
            "total_size_bytes": total_size,
            "file_count": file_count,
            "repository_path": str(repo_path),
        }

    async def parse_codebase(self, repo_path: Path) -> Dict:
        """
        Parse codebase to extract code structure.

        Uses Docling pipeline if available, otherwise falls back to tree-sitter.

        Returns:
            Comprehensive analysis with parsed code, dependencies, and tags
        """
        if self.use_docling:
            logger.info("Parsing codebase with Docling pipeline")
            return await self.docling_pipeline.process_pipeline(repo_path)
        else:
            logger.info("Parsing codebase with tree-sitter (fallback)")
            return build_code_map(str(repo_path))

    async def analyze_full(self) -> Dict:
        """
        Perform complete repository analysis: clone, analyze structure, and parse.

        Returns:
            Complete analysis data including:
            - repository metadata
            - file structure
            - parsed code with tags
            - dependency graph
            - entry points
        """
        try:
            # Clone repository
            repo_path = await self.clone_repository()

            # Analyze structure
            structure = await self.analyze_structure(repo_path)

            # Parse codebase
            parsed = await self.parse_codebase(repo_path)

            # Combine results
            return {
                "repository_url": self.repo_url,
                "git_ref": self.git_ref,
                "analysis_mode": "docling" if self.use_docling else "tree-sitter",
                "structure": structure,
                "parsed": parsed,
            }

        finally:
            # Always cleanup
            self.cleanup()

    def _get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes."""
        total = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total

    def _should_ignore(self, path: Path) -> bool:
        """
        Check if file/directory should be ignored.

        Note: Future enhancement could read .gitignore for custom patterns.
        """
        ignore_patterns = [
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".next",
            "target",
            "bin",
            "obj",
        ]
        return any(pattern in str(path) for pattern in ignore_patterns)

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect programming language from file extension.

        Note: Extend extension_map as needed for additional languages.
        """
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".go": "go",
            ".java": "java",
            ".cs": "csharp",
            ".rb": "ruby",
            ".php": "php",
            ".rs": "rust",
        }
        return extension_map.get(file_path.suffix.lower())

    def cleanup(self):
        """Clean up temporary directory."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
