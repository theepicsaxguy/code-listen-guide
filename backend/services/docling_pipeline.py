"""chonkie Pipeline Service for parsing, cleaning, and tagging codebases.

This service integrates chonkie for semantic text chunking and code analysis.

Key features:
- Parse code files and extract content
- Semantic chunking using chonkie's intelligent chunking algorithms
- Clean and normalize extracted content
- Tag content with semantic classifications
- Extract metadata and structure information
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

try:
    from chonkie import SemanticChunker, TokenChunker
    HAS_CHONKIE = True
except ImportError:
    HAS_CHONKIE = False
    logger.warning("chonkie not available. Install with: pip install chonkie")


class ContentType(str, Enum):
    """Types of content that can be parsed."""

    CODE = "code"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    DATA = "data"
    UNKNOWN = "unknown"


class TagCategory(str, Enum):
    """Categories for content tagging."""

    LANGUAGE = "language"
    FRAMEWORK = "framework"
    PATTERN = "pattern"
    COMPLEXITY = "complexity"
    VISIBILITY = "visibility"
    PURPOSE = "purpose"


class chonkiePipeline:
    """
    Main pipeline for processing codebases with chonkie.

    This pipeline provides three main operations:
    1. Parse: Extract structured content from files
    2. Clean: Normalize and filter content
    3. Tag: Add semantic metadata and classifications
    """

    def __init__(
        self,
        enable_code_enrichment: bool = True,
        enable_formula_enrichment: bool = False,
        enable_table_extraction: bool = True,
        artifacts_path: Optional[str] = None,
    ):
        """
        Initialize chonkie pipeline.

        Args:
            enable_code_enrichment: Enable advanced code understanding
            enable_formula_enrichment: Enable formula/equation parsing
            enable_table_extraction: Enable table extraction from documents
            artifacts_path: Path to chonkie model artifacts (for offline usage)
        """
        if not HAS_CHONKIE:
            raise RuntimeError(
                "chonkie is not installed. Install with: pip install chonkie"
            )

        self.enable_code_enrichment = enable_code_enrichment
        self.enable_formula_enrichment = enable_formula_enrichment
        self.enable_table_extraction = enable_table_extraction
        self.artifacts_path = artifacts_path

        # Initialize converter with options
        self._init_converter()

    def _init_converter(self):
        """Initialize chonkie chunker with configured options."""
        # chonkie is a text chunking library, not a document converter
        # We'll use TokenChunker for simple, reliable chunking
        # SemanticChunker can be enabled later with model2vec for better results
        self.chunker = TokenChunker(chunk_size=512)

    async def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a single file using chonkie for semantic chunking.

        Args:
            file_path: Path to file to parse

        Returns:
            Dictionary containing:
            - content: Extracted text content
            - chunks: Semantically chunked text segments
            - metadata: File metadata and properties
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Determine content type
            content_type = self._detect_content_type(file_path)

            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Chunk the content using chonkie
            chunks = self.chunker.chunk(content)

            # Extract structured data
            parsed_data = {
                "file_path": str(file_path),
                "content_type": content_type,
                "content": content,
                "chunks": [{"text": chunk.text, "index": i} for i, chunk in enumerate(chunks)],
                "metadata": {
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "file_type": file_path.suffix,
                    "num_chunks": len(chunks),
                },
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return {
                "file_path": str(file_path),
                "error": str(e),
                "content": None,
            }

    async def parse_codebase(
        self,
        repo_path: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Parse an entire codebase directory.

        Args:
            repo_path: Path to repository root
            include_patterns: File patterns to include (e.g., ["*.py", "*.md"])
            exclude_patterns: Directories/files to exclude

        Returns:
            Dictionary with:
            - files: List of parsed file data
            - summary: Aggregated statistics
            - dependency_graph: Relationships between files
            - entry_points: Identified entry points
        """
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository not found: {repo_path}")

        # Default patterns
        if include_patterns is None:
            include_patterns = [
                "*.py",
                "*.js",
                "*.ts",
                "*.tsx",
                "*.jsx",
                "*.md",
                "*.rst",
                "*.txt",
                "*.json",
                "*.yaml",
                "*.yml",
                "*.toml",
                "README*",
                "LICENSE*",
            ]

        if exclude_patterns is None:
            exclude_patterns = [
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
                "*.pyc",
                "*.pyo",
                "*.so",
                "*.dylib",
                "*.dll",
            ]

        parsed_files = []
        total_files = 0
        parsed_count = 0
        failed_count = 0

        # Walk through repository
        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Check exclusions
            if self._should_exclude(file_path, repo_path, exclude_patterns):
                continue

            # Check inclusions
            if not self._should_include(file_path, include_patterns):
                continue

            total_files += 1

            # Parse file
            parsed = await self.parse_file(file_path)

            if "error" not in parsed:
                parsed_count += 1
            else:
                failed_count += 1

            parsed_files.append(parsed)

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(parsed_files)

        # Identify entry points
        entry_points = self._identify_entry_points(parsed_files, repo_path)

        return {
            "repository_path": str(repo_path),
            "files": parsed_files,
            "summary": {
                "total_files": total_files,
                "successfully_parsed": parsed_count,
                "failed_to_parse": failed_count,
                "parse_success_rate": (
                    parsed_count / total_files * 100 if total_files > 0 else 0
                ),
            },
            "dependency_graph": dependency_graph,
            "entry_points": entry_points,
        }

    async def clean_content(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize parsed content.

        Operations:
        - Remove redundant whitespace
        - Normalize code formatting
        - Filter out generated/minified code
        - Remove binary content
        - Standardize line endings

        Args:
            parsed_data: Data from parse_file or parse_codebase

        Returns:
            Cleaned version of parsed_data
        """
        cleaned = parsed_data.copy()

        # Clean content text
        if "content" in cleaned and cleaned["content"]:
            content = cleaned["content"]

            # Normalize whitespace
            content = self._normalize_whitespace(content)

            # Remove excessive blank lines
            content = self._remove_excessive_blank_lines(content)

            # Filter out potential minified code
            if self._is_likely_minified(content):
                cleaned["metadata"]["is_minified"] = True
                cleaned["content"] = "[Minified content - skipped for readability]"
            else:
                cleaned["content"] = content

        # Clean code blocks
        if "code_blocks" in cleaned:
            cleaned["code_blocks"] = [
                self._clean_code_block(block) for block in cleaned["code_blocks"]
            ]

        return cleaned

    async def tag_content(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add semantic tags and classifications to content.

        Tags include:
        - Programming language
        - Framework/library usage
        - Design patterns
        - Code complexity
        - Visibility (public/private API)
        - Purpose (test, config, documentation, etc.)

        Args:
            cleaned_data: Data from clean_content

        Returns:
            Tagged version of cleaned_data with "tags" field added
        """
        tagged = cleaned_data.copy()
        tags = {}

        file_path = Path(tagged.get("file_path", ""))
        content = tagged.get("content", "")

        # Language detection
        tags[TagCategory.LANGUAGE] = self._detect_language(file_path, content)

        # Framework detection
        tags[TagCategory.FRAMEWORK] = self._detect_frameworks(content)

        # Pattern detection
        tags[TagCategory.PATTERN] = self._detect_patterns(content)

        # Complexity assessment
        tags[TagCategory.COMPLEXITY] = self._assess_complexity(content)

        # Visibility classification
        tags[TagCategory.VISIBILITY] = self._classify_visibility(file_path, content)

        # Purpose classification
        tags[TagCategory.PURPOSE] = self._classify_purpose(file_path, content)

        tagged["tags"] = tags
        return tagged

    async def process_pipeline(
        self,
        repo_path: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run complete pipeline: parse -> clean -> tag.

        This is the main entry point for processing a codebase.

        Args:
            repo_path: Path to repository
            include_patterns: File patterns to include
            exclude_patterns: Patterns to exclude

        Returns:
            Fully processed codebase data with parsing, cleaning, and tagging
        """
        logger.info(f"Starting chonkie pipeline for: {repo_path}")

        # Step 1: Parse
        logger.info("Step 1/3: Parsing codebase...")
        parsed = await self.parse_codebase(
            repo_path, include_patterns, exclude_patterns
        )

        # Step 2: Clean each file
        logger.info("Step 2/3: Cleaning content...")
        cleaned_files = []
        for file_data in parsed["files"]:
            if "error" not in file_data:
                cleaned = await self.clean_content(file_data)
                cleaned_files.append(cleaned)
            else:
                cleaned_files.append(file_data)

        # Step 3: Tag each file
        logger.info("Step 3/3: Tagging content...")
        tagged_files = []
        for file_data in cleaned_files:
            if "error" not in file_data:
                tagged = await self.tag_content(file_data)
                tagged_files.append(tagged)
            else:
                tagged_files.append(file_data)

        # Update result
        result = parsed.copy()
        result["files"] = tagged_files

        logger.info(
            f"Pipeline complete. Processed {result['summary']['successfully_parsed']} "
            f"of {result['summary']['total_files']} files"
        )

        return result

    # Helper methods

    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Detect the type of content in a file."""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        # Code files
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".java",
            ".go",
            ".rs",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".rb",
            ".php",
        }
        if suffix in code_extensions:
            return ContentType.CODE

        # Documentation
        doc_extensions = {".md", ".rst", ".txt", ".adoc"}
        if suffix in doc_extensions or "readme" in name or "changelog" in name:
            return ContentType.DOCUMENTATION

        # Configuration
        config_extensions = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
        if suffix in config_extensions or name in {"dockerfile", ".gitignore"}:
            return ContentType.CONFIGURATION

        # Data
        data_extensions = {".csv", ".xml", ".sql"}
        if suffix in data_extensions:
            return ContentType.DATA

        return ContentType.UNKNOWN

    def _extract_structure(self, doc) -> Dict[str, Any]:
        """Extract document structure (headings, sections)."""
        # This would extract the hierarchical structure from the document
        # For now, return a placeholder
        return {
            "sections": [],
            "headings": [],
            "depth": 0,
        }

    def _extract_code_blocks(self, doc) -> List[Dict[str, Any]]:
        """Extract code blocks from document."""
        code_blocks = []
        # Iterate through document items and find code blocks
        for item in doc.main_text.items:
            if hasattr(item, "code_language"):
                code_blocks.append(
                    {
                        "language": getattr(item, "code_language", "unknown"),
                        "content": item.text,
                    }
                )
        return code_blocks

    def _extract_tables(self, doc) -> List[Dict[str, Any]]:
        """Extract tables from document."""
        tables = []
        for item in doc.main_text.items:
            if item.__class__.__name__ == "TableItem":
                tables.append(
                    {
                        "rows": getattr(item, "num_rows", 0),
                        "cols": getattr(item, "num_cols", 0),
                    }
                )
        return tables

    def _extract_images(self, doc) -> List[Dict[str, Any]]:
        """Extract image metadata."""
        images = []
        for item in doc.main_text.items:
            if item.__class__.__name__ == "PictureItem":
                images.append(
                    {
                        "caption": getattr(item, "caption", ""),
                    }
                )
        return images

    def _extract_formulas(self, doc) -> List[str]:
        """Extract mathematical formulas."""
        formulas = []
        for item in doc.main_text.items:
            if hasattr(item, "formula"):
                formulas.append(item.text)
        return formulas

    def _should_exclude(
        self, file_path: Path, repo_path: Path, patterns: List[str]
    ) -> bool:
        """Check if file should be excluded."""
        relative = file_path.relative_to(repo_path)
        path_str = str(relative)

        for pattern in patterns:
            if pattern in path_str:
                return True
        return False

    def _should_include(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file matches include patterns."""
        from fnmatch import fnmatch

        for pattern in patterns:
            if fnmatch(file_path.name, pattern):
                return True
        return False

    def _build_dependency_graph(
        self, files: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Build dependency graph from parsed files.

        Note: Currently returns empty graph. Future enhancement: parse imports/dependencies.
        """
        graph = {}
        return graph

    def _identify_entry_points(
        self, files: List[Dict[str, Any]], repo_path: Path
    ) -> List[str]:
        """Identify likely entry points in the codebase."""
        entry_points = []

        for file_data in files:
            file_path = Path(file_data.get("file_path", ""))
            name = file_path.name.lower()

            # Common entry point patterns
            if name in {"main.py", "app.py", "index.js", "index.ts", "server.py"}:
                entry_points.append(str(file_path))
            elif name == "__main__.py" or name.startswith("cli"):
                entry_points.append(str(file_path))

        return entry_points

    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in content."""
        import re

        # Replace multiple spaces with single space (except at line start)
        lines = content.split("\n")
        normalized = [re.sub(r"(?<!^)  +", " ", line) for line in lines]
        return "\n".join(normalized)

    def _remove_excessive_blank_lines(self, content: str) -> str:
        """Remove excessive blank lines (more than 2 consecutive)."""
        import re

        return re.sub(r"\n{4,}", "\n\n\n", content)

    def _is_likely_minified(self, content: str) -> bool:
        """Detect if content is likely minified code."""
        if not content:
            return False

        lines = content.split("\n")
        if len(lines) < 5:
            return False

        # Check average line length (minified code has very long lines)
        avg_length = sum(len(line) for line in lines) / len(lines)
        if avg_length > 200:
            return True

        # Check for lack of indentation variety
        indents = set(len(line) - len(line.lstrip()) for line in lines if line.strip())
        if len(indents) < 2:
            return True

        return False

    def _clean_code_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single code block."""
        cleaned = block.copy()
        if "content" in cleaned:
            cleaned["content"] = self._normalize_whitespace(cleaned["content"])
        return cleaned

    def _detect_language(self, file_path: Path, content: str) -> List[str]:
        """Detect programming languages used."""
        languages = []
        suffix = file_path.suffix.lower()

        lang_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".jsx": "JavaScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
        }

        if suffix in lang_map:
            languages.append(lang_map[suffix])

        return languages

    def _detect_frameworks(self, content: str) -> List[str]:
        """Detect frameworks/libraries used."""
        frameworks = []

        # Simple keyword-based detection
        framework_keywords = {
            "React": ["import React", "from 'react'"],
            "Vue": ["import Vue", "from 'vue'"],
            "Angular": ["@angular/", "import { Component }"],
            "FastAPI": ["from fastapi", "FastAPI()"],
            "Django": ["from django", "django."],
            "Flask": ["from flask", "Flask(__name__)"],
            "Express": ["require('express')", "from 'express'"],
        }

        for framework, keywords in framework_keywords.items():
            if any(keyword in content for keyword in keywords):
                frameworks.append(framework)

        return frameworks

    def _detect_patterns(self, content: str) -> List[str]:
        """Detect design patterns in code."""
        patterns = []

        # Simple pattern detection
        if "class" in content and "def __init__" in content:
            patterns.append("Object-Oriented")
        if "async def" in content or "await " in content:
            patterns.append("Async/Await")
        if "yield" in content:
            patterns.append("Generator")

        return patterns

    def _assess_complexity(self, content: str) -> str:
        """Assess code complexity level."""
        if not content:
            return "unknown"

        lines = [l for l in content.split("\n") if l.strip()]
        num_lines = len(lines)

        # Simple heuristic based on line count
        if num_lines < 50:
            return "low"
        elif num_lines < 200:
            return "medium"
        else:
            return "high"

    def _classify_visibility(self, file_path: Path, content: str) -> str:
        """Classify API visibility (public/private)."""
        name = file_path.name

        # Files starting with _ or in __pycache__ are typically private
        if name.startswith("_") or "__pycache__" in str(file_path):
            return "private"

        # Check for public API indicators
        if "export" in content or "__all__" in content:
            return "public"

        return "internal"

    def _classify_purpose(self, file_path: Path, content: str) -> str:
        """Classify file purpose."""
        name = file_path.name.lower()

        if "test" in name or "spec" in name:
            return "test"
        if "config" in name or name.endswith((".json", ".yaml", ".yml", ".toml")):
            return "configuration"
        if "readme" in name or name.endswith(".md"):
            return "documentation"
        if "main" in name or "app" in name:
            return "entry_point"
        if "util" in name or "helper" in name:
            return "utility"

        return "implementation"
