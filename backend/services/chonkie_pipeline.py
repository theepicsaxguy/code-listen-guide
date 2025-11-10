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

try:
    from backend.services.code_analyzer import CodeAnalyzer
    HAS_CODE_ANALYZER = True
except ImportError:
    HAS_CODE_ANALYZER = False
    logger.warning("CodeAnalyzer not available. Install tree-sitter for rich metadata extraction.")


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

        # Initialize code analyzer for rich metadata extraction
        self.code_analyzer = None
        if HAS_CODE_ANALYZER and enable_code_enrichment:
            try:
                self.code_analyzer = CodeAnalyzer()
                logger.info("CodeAnalyzer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize CodeAnalyzer: {e}")

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

            # Extract detailed chunk information
            chunk_details = []
            for i, chunk in enumerate(chunks):
                chunk_info = {
                    "index": i,
                    "text": chunk.text,
                    "token_count": getattr(chunk, 'token_count', len(chunk.text.split())),
                    "start_index": getattr(chunk, 'start_index', 0),
                    "end_index": getattr(chunk, 'end_index', len(chunk.text)),
                }
                chunk_details.append(chunk_info)

            # Extract code enrichment data if enabled
            functions = []
            classes = []
            imports = []
            exports = []
            call_graph = {}
            code_metrics = {}
            documentation = {}
            dependencies = {}
            code_metadata = {}

            language = "unknown"
            if self.enable_code_enrichment and content_type == ContentType.CODE:
                language = self._detect_language(file_path)

                # Use CodeAnalyzer for comprehensive metadata extraction
                if self.code_analyzer:
                    try:
                        analysis = self.code_analyzer.analyze_file(file_path, content)
                        functions = analysis.get("functions", [])
                        classes = analysis.get("classes", [])
                        imports = analysis.get("imports", [])
                        exports = analysis.get("exports", [])
                        call_graph = analysis.get("call_graph", {})
                        code_metrics = analysis.get("metrics", {})
                        documentation = analysis.get("documentation", {})
                        dependencies = analysis.get("dependencies", {})
                        code_metadata = analysis.get("metadata", {})
                        language = analysis.get("language", language)
                    except Exception as e:
                        logger.warning(f"CodeAnalyzer failed for {file_path}: {e}")
                        # Fallback to basic Python enrichment
                        if language == "python":
                            enrichment = self._enrich_python_code(content, str(file_path))
                            functions = enrichment.get("functions", [])
                            classes = enrichment.get("classes", [])
                            imports = enrichment.get("imports", [])
                            exports = enrichment.get("exports", [])
                elif language == "python":
                    # Fallback to basic Python enrichment if CodeAnalyzer not available
                    enrichment = self._enrich_python_code(content, str(file_path))
                    functions = enrichment.get("functions", [])
                    classes = enrichment.get("classes", [])
                    imports = enrichment.get("imports", [])
                    exports = enrichment.get("exports", [])

            # Extract structured data
            parsed_data = {
                "file_path": str(file_path),
                "content_type": content_type,
                "content": content,
                "raw_content": content,  # For API compatibility
                "chunks": chunk_details,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "exports": exports,
                "call_graph": call_graph,
                "dependencies": dependencies,
                "documentation": documentation,
                "metadata": {
                    # Basic file info
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 3),
                    "file_type": file_path.suffix,
                    "language": language,

                    # Chunking info
                    "num_chunks": len(chunks),
                    "total_tokens": sum(c.get('token_count', 0) for c in chunk_details),
                    "avg_chunk_size": sum(c.get('token_count', 0) for c in chunk_details) / len(chunks) if chunks else 0,

                    # Code structure counts
                    "function_count": len(functions),
                    "class_count": len(classes),
                    "import_count": len(imports),
                    "export_count": len(exports) if isinstance(exports, list) else 0,

                    # Code metrics (from CodeAnalyzer)
                    **code_metrics,

                    # Additional metadata from CodeAnalyzer
                    **code_metadata,
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

        # Default patterns - include ALL common code and config files
        if include_patterns is None:
            include_patterns = [
                # Python
                "*.py", "*.pyx", "*.pyd",
                # JavaScript/TypeScript
                "*.js", "*.jsx", "*.ts", "*.tsx", "*.mjs", "*.cjs",
                # Web
                "*.html", "*.htm", "*.css", "*.scss", "*.sass", "*.less",
                "*.vue", "*.svelte",
                # Documentation
                "*.md", "*.rst", "*.txt", "*.adoc",
                # Config
                "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg",
                "*.xml", "*.env", ".env*",
                # Other languages
                "*.java", "*.kt", "*.kts",  # Java/Kotlin
                "*.go",  # Go
                "*.rs",  # Rust
                "*.rb",  # Ruby
                "*.php",  # PHP
                "*.cpp", "*.c", "*.h", "*.hpp", "*.cc",  # C/C++
                "*.cs",  # C#
                "*.swift",  # Swift
                "*.sh", "*.bash", "*.zsh",  # Shell
                "*.sql",  # SQL
                "*.r", "*.R",  # R
                # Special files
                "Makefile", "Dockerfile", "*.dockerfile",
                "README*", "LICENSE*", "CHANGELOG*",
                ".gitignore", ".dockerignore",
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
                "total_functions": dependency_graph.get("summary", {}).get("total_functions", 0),
                "total_classes": dependency_graph.get("summary", {}).get("total_classes", 0),
                "total_imports": dependency_graph.get("summary", {}).get("total_imports", 0),
                "entry_points": entry_points,
            },
            "dependency_graph": dependency_graph,
        }

    async def clean_content(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize parsed content.

        Operations:
        - Remove redundant whitespace
        - Normalize code formatting
        - Remove comments (optional, for LLM processing)
        - Remove debug/console statements
        - Filter out generated/minified code
        - Remove binary content
        - Standardize line endings
        - Normalize indentation

        Args:
            parsed_data: Data from parse_file or parse_codebase

        Returns:
            Cleaned version of parsed_data
        """
        cleaned = parsed_data.copy()

        # Clean content text
        if "content" in cleaned and cleaned["content"]:
            content = cleaned["content"]
            content_type = cleaned.get("content_type", ContentType.UNKNOWN)

            # Filter out potential minified code early
            if self._is_likely_minified(content):
                if "metadata" not in cleaned:
                    cleaned["metadata"] = {}
                cleaned["metadata"]["is_minified"] = True
                cleaned["content"] = "[Minified content - skipped for readability]"
                cleaned["metadata"]["cleaned_reason"] = "minified"
                return cleaned

            # Apply cleaning steps
            original_lines = len(content.split('\n'))

            # Step 1: Normalize whitespace
            content = self._normalize_whitespace(content)

            # Step 2: Remove excessive blank lines
            content = self._remove_excessive_blank_lines(content)

            # Step 3: Remove trailing whitespace
            content = self._remove_trailing_whitespace(content)

            # Step 4: For code files, apply code-specific cleaning
            if content_type == ContentType.CODE:
                language = cleaned.get("metadata", {}).get("language", "unknown")

                # Remove comments (makes diff more meaningful)
                content = self._remove_comments(content, language)

                # Remove debug/console statements
                content = self._remove_debug_statements(content, language)

                # Remove empty functions/classes
                content = self._remove_empty_blocks(content, language)

            # Step 5: Normalize line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')

            # Track cleaning stats
            cleaned_lines = len(content.split('\n'))
            if "metadata" not in cleaned:
                cleaned["metadata"] = {}

            cleaned["metadata"]["original_lines"] = original_lines
            cleaned["metadata"]["cleaned_lines"] = cleaned_lines
            cleaned["metadata"]["lines_removed"] = original_lines - cleaned_lines
            cleaned["metadata"]["cleaning_applied"] = True

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
        tags = []

        file_path = Path(tagged.get("file_path", ""))
        content = tagged.get("content", "")

        # Language detection
        language = self._detect_language(file_path)
        if language != "unknown":
            tags.append(f"language:{language}")

        # Framework detection
        frameworks = self._detect_frameworks(content)
        tags.extend([f"framework:{fw}" for fw in frameworks])

        # Pattern detection
        patterns = self._detect_patterns(content)
        tags.extend([f"pattern:{p}" for p in patterns])

        # Complexity assessment
        complexity = self._assess_complexity(content)
        tags.append(f"complexity:{complexity}")

        # Visibility classification
        visibility = self._classify_visibility(file_path, content)
        tags.append(f"visibility:{visibility}")

        # Purpose classification
        purpose = self._classify_purpose(file_path, content)
        tags.append(f"purpose:{purpose}")

        tagged["tags"] = tags

        # Also store individual fields for easier access
        tagged["language"] = language if language != "unknown" else None
        tagged["summary"] = f"{purpose.capitalize()} file"
        tagged["complexity"] = complexity
        tagged["visibility"] = visibility
        
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

        # Convert files array to modules dict for API compatibility
        modules = {}
        for file_data in tagged_files:
            if "error" not in file_data:
                file_path = file_data.get("file_path", "")
                # Make path relative to repo_path
                try:
                    rel_path = str(Path(file_path).relative_to(repo_path))
                except ValueError:
                    rel_path = file_path
                
                modules[rel_path] = file_data
        
        result["modules"] = modules

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

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".swift": "swift",
            ".sh": "shell",
            ".bash": "shell",
        }
        return language_map.get(suffix, "unknown")

    def _enrich_python_code(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Enrich Python code with AST-based analysis.

        Extracts:
        - Functions (name, line numbers, parameters, calls)
        - Classes (name, methods, inheritance)
        - Imports (modules, items, types)
        - Exports (public functions/classes)
        """
        import ast

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return {"functions": [], "classes": [], "imports": [], "exports": []}

        functions = []
        classes = []
        imports = []
        exports = []

        # Extract functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_info = {
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "parameters": [arg.arg for arg in node.args.args],
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "is_private": node.name.startswith("_"),
                    "decorators": [],
                    "calls": [],
                }

                # Extract decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        func_info["decorators"].append(decorator.id)
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        func_info["decorators"].append(decorator.func.id)

                # Extract function calls within this function
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            func_info["calls"].append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            # Handle method calls like obj.method()
                            if isinstance(child.func.value, ast.Name):
                                func_info["calls"].append(f"{child.func.value.id}.{child.func.attr}")

                # Extract docstring
                docstring = ast.get_docstring(node)
                if docstring:
                    func_info["docstring"] = docstring[:200]  # Limit length

                functions.append(func_info)

                # Add to exports if public (not starting with _)
                if not node.name.startswith("_"):
                    exports.append({
                        "name": node.name,
                        "type": "function",
                        "line": node.lineno
                    })

        # Extract classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "methods": [],
                    "inherits_from": [],
                    "is_private": node.name.startswith("_"),
                }

                # Extract base classes
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        class_info["inherits_from"].append(base.id)
                    elif isinstance(base, ast.Attribute):
                        class_info["inherits_from"].append(base.attr)

                # Extract methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        class_info["methods"].append(item.name)

                # Extract docstring
                docstring = ast.get_docstring(node)
                if docstring:
                    class_info["docstring"] = docstring[:200]

                classes.append(class_info)

                # Add to exports if public
                if not node.name.startswith("_"):
                    exports.append({
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno
                    })

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "module": alias.name,
                        "type": self._classify_import(alias.name),
                        "items": [alias.asname if alias.asname else alias.name],
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_info = {
                        "module": node.module,
                        "type": self._classify_import(node.module),
                        "items": [alias.name for alias in node.names],
                        "line": node.lineno
                    }

                    # Try to resolve local imports
                    if import_info["type"] == "local":
                        import_info["resolved_path"] = self._resolve_python_import(
                            node.module, file_path
                        )

                    imports.append(import_info)

        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports
        }

    def _classify_import(self, module_name: str) -> str:
        """Classify import as standard library, third-party, or local."""
        if module_name.startswith("."):
            return "local"

        # Common standard library modules
        stdlib_modules = {
            "os", "sys", "json", "ast", "logging", "pathlib", "re", "datetime",
            "collections", "itertools", "functools", "typing", "enum", "abc",
            "asyncio", "threading", "multiprocessing", "subprocess", "argparse",
            "urllib", "http", "email", "unittest", "pytest"
        }

        base_module = module_name.split(".")[0]
        if base_module in stdlib_modules:
            return "standard_library"

        return "third_party"

    def _resolve_python_import(self, module_path: str, current_file: str) -> str:
        """Attempt to resolve a relative Python import to an absolute path."""
        # This is a simplified resolution - a full implementation would need
        # to handle Python's import system more comprehensively
        if module_path.startswith("."):
            # Relative import
            current_dir = Path(current_file).parent
            parts = module_path.strip(".").split(".")
            target_path = current_dir / "/".join(parts)
            return f"{target_path}.py"
        return module_path

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
    ) -> Dict[str, Any]:
        """
        Build dependency graph from parsed files.

        Returns a dictionary with:
        - files: file-to-file dependencies
        - functions: function call graph
        """
        graph = {
            "files": {},
            "functions": {},
            "summary": {
                "total_files": len(files),
                "total_functions": 0,
                "total_classes": 0,
                "total_imports": 0
            }
        }

        # Build symbol table for function resolution
        symbol_table = {}
        for file_data in files:
            file_path = file_data.get("file_path", "")

            # Register functions
            for func in file_data.get("functions", []):
                func_key = f"{file_path}::{func['name']}"
                symbol_table[func_key] = {
                    "file": file_path,
                    "type": "function",
                    "data": func
                }
                graph["summary"]["total_functions"] += 1

            # Register classes
            for cls in file_data.get("classes", []):
                cls_key = f"{file_path}::{cls['name']}"
                symbol_table[cls_key] = {
                    "file": file_path,
                    "type": "class",
                    "data": cls
                }
                graph["summary"]["total_classes"] += 1

        # Build file dependencies
        for file_data in files:
            file_path = file_data.get("file_path", "")
            imports = file_data.get("imports", [])

            file_deps = {
                "imports_from": [],
                "imported_by": [],
                "import_count": len(imports)
            }

            # Track which files this file imports from
            for imp in imports:
                if imp.get("type") == "local" and imp.get("resolved_path"):
                    file_deps["imports_from"].append(imp["resolved_path"])

            graph["files"][file_path] = file_deps
            graph["summary"]["total_imports"] += len(imports)

        # Build reverse relationships (imported_by)
        for file_path, deps in graph["files"].items():
            for imported_file in deps["imports_from"]:
                if imported_file in graph["files"]:
                    graph["files"][imported_file]["imported_by"].append(file_path)

        # Build function call graph
        for file_data in files:
            file_path = file_data.get("file_path", "")

            for func in file_data.get("functions", []):
                func_key = f"{file_path}::{func['name']}"
                graph["functions"][func_key] = {
                    "file": file_path,
                    "calls": [],
                    "called_by": []
                }

                # Add direct function calls (within same file for now)
                for call in func.get("calls", []):
                    # Try to resolve to a full path
                    if "::" not in call:
                        # Check if it's in the same file
                        same_file_key = f"{file_path}::{call}"
                        if same_file_key in symbol_table:
                            graph["functions"][func_key]["calls"].append(same_file_key)

        # Build reverse call graph (called_by)
        for func_key, func_data in graph["functions"].items():
            for called_func in func_data["calls"]:
                if called_func in graph["functions"]:
                    graph["functions"][called_func]["called_by"].append(func_key)

        return graph

    def _identify_entry_points(
        self, files: List[Dict[str, Any]], repo_path: Path
    ) -> List[Dict[str, Any]]:
        """Identify likely entry points in the codebase."""
        entry_points = []

        for file_data in files:
            file_path = file_data.get("file_path", "")
            name = Path(file_path).name.lower()
            content = file_data.get("content", "")
            functions = file_data.get("functions", [])

            reasons = []
            is_entry = False

            # Check for common entry point filenames
            if name in {"main.py", "app.py", "index.js", "index.ts", "server.py", "__main__.py"}:
                is_entry = True
                reasons.append("entry_point_filename")

            # Check for CLI patterns
            if name.startswith("cli") or "command" in name:
                is_entry = True
                reasons.append("cli_pattern")

            # Check for main function
            for func in functions:
                if func.get("name") in ["main", "__main__"]:
                    is_entry = True
                    reasons.append("has_main_function")

            # Check for if __name__ == "__main__"
            if '__name__ == "__main__"' in content or "__name__ == '__main__'" in content:
                is_entry = True
                reasons.append("has_main_guard")

            # Check for API route decorators (Flask, FastAPI, etc.)
            for func in functions:
                decorators = func.get("decorators", [])
                if any(dec in ["route", "app", "get", "post", "put", "delete", "api"] for dec in decorators):
                    is_entry = True
                    reasons.append("has_api_routes")
                    break

            # Check for test files
            if "test" in name or any(func.get("name", "").startswith("test_") for func in functions):
                is_entry = True
                reasons.append("is_test_file")

            if is_entry:
                entry_points.append({
                    "file": file_path,
                    "reasons": reasons
                })

        return entry_points

    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in content."""
        import re

        # Replace tabs with spaces
        content = content.replace('\t', '    ')

        # Replace multiple spaces with single space (except at line start for indentation)
        lines = content.split("\n")
        normalized = []
        for line in lines:
            # Preserve leading spaces (indentation), normalize rest
            stripped = line.lstrip()
            if stripped:
                leading_spaces = len(line) - len(stripped)
                # Normalize the non-indentation part
                normalized_line = ' ' * leading_spaces + re.sub(r'  +', ' ', stripped)
                normalized.append(normalized_line)
            else:
                normalized.append(line)

        return "\n".join(normalized)

    def _remove_trailing_whitespace(self, content: str) -> str:
        """Remove trailing whitespace from all lines."""
        lines = content.split("\n")
        return "\n".join(line.rstrip() for line in lines)

    def _remove_comments(self, content: str, language: str) -> str:
        """Remove comments from code."""
        import re

        lines = content.split('\n')
        cleaned_lines = []

        # Language-specific comment patterns
        if language in ['python']:
            for line in lines:
                # Remove inline comments but preserve docstrings
                if '"""' in line or "'''" in line:
                    cleaned_lines.append(line)  # Keep docstrings
                elif '#' in line:
                    # Check if # is inside a string
                    if line.strip().startswith('#'):
                        continue  # Skip full-line comments
                    else:
                        # Remove inline comments
                        cleaned_lines.append(line.split('#')[0].rstrip())
                else:
                    cleaned_lines.append(line)

        elif language in ['javascript', 'typescript', 'tsx', 'java', 'cpp', 'csharp', 'go', 'rust']:
            in_block_comment = False
            for line in lines:
                # Handle block comments /* */
                if '/*' in line:
                    in_block_comment = True
                    # Remove everything after /*
                    line = line.split('/*')[0]

                if in_block_comment:
                    if '*/' in line:
                        in_block_comment = False
                        # Take everything after */
                        line = line.split('*/', 1)[1] if '*/' in line else ''
                    else:
                        continue  # Skip lines inside block comments

                # Handle single-line comments //
                if '//' in line:
                    if line.strip().startswith('//'):
                        continue  # Skip full-line comments
                    else:
                        # Remove inline comments
                        line = line.split('//')[0].rstrip()

                if line.strip():  # Only add non-empty lines
                    cleaned_lines.append(line)

        else:
            return content  # Return original if language not supported

        return '\n'.join(cleaned_lines)

    def _remove_debug_statements(self, content: str, language: str) -> str:
        """Remove console.log, print, debugger statements."""
        import re

        lines = content.split('\n')
        cleaned_lines = []

        debug_patterns = {
            'python': [
                r'^\s*print\s*\(',
                r'^\s*pprint\s*\(',
                r'^\s*logger\.debug\s*\(',
            ],
            'javascript': [
                r'^\s*console\.log\s*\(',
                r'^\s*console\.debug\s*\(',
                r'^\s*console\.info\s*\(',
                r'^\s*debugger\s*;',
            ],
            'typescript': [
                r'^\s*console\.log\s*\(',
                r'^\s*console\.debug\s*\(',
                r'^\s*console\.info\s*\(',
                r'^\s*debugger\s*;',
            ],
        }

        patterns = debug_patterns.get(language, [])

        for line in lines:
            is_debug = False
            for pattern in patterns:
                if re.match(pattern, line):
                    is_debug = True
                    break

            if not is_debug:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _remove_empty_blocks(self, content: str, language: str) -> str:
        """Remove empty functions, classes, etc."""
        import re

        # This is a simplified version - could be enhanced with tree-sitter
        lines = content.split('\n')
        cleaned_lines = []

        # Simple heuristic: remove function/class definitions followed immediately by 'pass' or empty
        if language == 'python':
            skip_next = False
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue

                # Check if this is a def/class line followed by just 'pass'
                if line.strip().startswith(('def ', 'class ')) and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line == 'pass' and (i + 2 >= len(lines) or not lines[i + 2].strip().startswith(' ')):
                        # Skip this def/class and the pass line
                        skip_next = True
                        continue

                cleaned_lines.append(line)

        else:
            return content  # Return original for non-Python

        return '\n'.join(cleaned_lines)

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
