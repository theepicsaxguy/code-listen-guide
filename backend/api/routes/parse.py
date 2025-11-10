"""Parse API routes for repository analysis."""

import asyncio
import logging
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, get_db
from backend.api.schemas.parse import (
    FileMetadata,
    ParsedFile,
    ParseErrorResponse,
    ParseRepositoryRequest,
    ParseRepositoryResponse,
    RepositorySummary,
)
from backend.models.user import User
from backend.services.chonkie_pipeline import chonkiePipeline
from backend.tools.git_tools import clone_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/parse", tags=["parse"])

# Maximum concurrent file reads to prevent overwhelming the system
MAX_CONCURRENT_FILE_READS = 10


async def _read_file_async(file_path: Path) -> tuple[str, str]:
    """
    Read a file asynchronously.
    
    Returns:
        Tuple of (file_path, content) or (file_path, "") on error
    """
    try:
        def _read_sync(path: Path) -> str:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        content = await asyncio.to_thread(_read_sync, file_path)
        return (str(file_path), content)
    except Exception as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return (str(file_path), "")


@router.post("/repository", operation_id="parseRepository", response_model=ParseRepositoryResponse)
async def parse_repository(
    request: ParseRepositoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Parse a GitHub repository and return structured analysis results.

    This endpoint clones the specified repository, parses all files using either
    the chonkie pipeline (advanced) or tree-sitter (fallback), and returns
    comprehensive analysis results including file content, metadata, and summaries.

    Security:
    - Requires authenticated user
    - Enforces git safeguards (allowed hosts, size limits, timeouts)
    - Validates GitHub URL format

    Performance:
    - Synchronous processing with 180s timeout (enforced)
    - Suitable for repositories up to 500MB (configurable)
    - Average processing time: 5-15 seconds for typical repos

    Use Cases:
    - Agent workflows requiring code analysis
    - Pre-job repository validation
    - Code structure exploration
    - Documentation generation

    Returns structured data ready for LLM consumption or further processing.
    """
    start_time = time.time()
    repo_path = None

    try:
        logger.info(
            f"User {current_user.id} parsing repository: {request.repo_url} "
            f"(ref: {request.git_ref})"
        )

        # Step 1: Clone repository with git safeguards
        try:
            repo_path = await asyncio.to_thread(clone_repository, request.repo_url)
            logger.info(f"Repository cloned to: {repo_path}")
        except Exception as e:
            logger.error(f"Git clone failed for {request.repo_url}: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Failed to clone repository: {str(e)}",
                    "error_type": "git",
                },
            )

        # Step 2: Parse repository with chonkie pipeline
        try:
            logger.info(
                f"Parsing repository with chonkie pipeline "
                f"(code_enrichment={request.enable_code_enrichment}, "
                f"formula_enrichment={request.enable_formula_enrichment}, "
                f"table_extraction={request.enable_table_extraction})"
            )
            chonkie = chonkiePipeline(
                enable_code_enrichment=request.enable_code_enrichment,
                enable_formula_enrichment=request.enable_formula_enrichment,
                enable_table_extraction=request.enable_table_extraction,
            )
            analysis_result = await asyncio.wait_for(
                chonkie.process_pipeline(Path(repo_path)),
                timeout=180.0,  # 3 minute timeout for large repos
            )
        except asyncio.TimeoutError:
            logger.error(f"chonkie parsing timeout for {request.repo_url}")
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "Repository parsing timed out (180s limit)",
                    "error_type": "timeout",
                    "details": {
                        "suggestion": "Repository may be too large for parsing. Try a smaller repository or specific branch."
                    },
                },
            )
        except Exception as e:
            logger.error(f"chonkie parsing failed for {request.repo_url}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": f"Failed to parse repository with chonkie: {str(e)}",
                    "error_type": "parsing",
                },
            )

        # Step 3: Process results into response format
        modules: Dict[str, ParsedFile] = {}
        total_files = 0
        total_size = 0
        languages = set()
        frameworks = set()
        patterns = set()
        entry_points = []
        warnings = []
        successful_parses = 0

        # Extract modules from analysis result
        # Both chonkie and tree-sitter return {modules: {...}}
        raw_modules = analysis_result.get("modules", {})

        # Collect files that need to be read from disk (batch processing)
        files_to_read: List[tuple[str, Path]] = []
        filtered_modules: Dict[str, Dict] = {}

        # First pass: filter and collect files that need reading
        for file_path, file_data in raw_modules.items():
            # Apply include/exclude filters if specified
            if request.include_patterns and not _matches_patterns(
                file_path, request.include_patterns
            ):
                continue

            if request.exclude_patterns and _matches_patterns(
                file_path, request.exclude_patterns
            ):
                continue

            # Store filtered module data
            filtered_modules[file_path] = file_data

            # Collect files that need to be read from disk
            content = file_data.get("content", "")
            if not content and repo_path:
                file_full_path = Path(repo_path) / file_path
                if file_full_path.exists():
                    files_to_read.append((file_path, file_full_path))

        # Batch read files with concurrency limit
        file_contents: Dict[str, str] = {}
        if files_to_read:
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_FILE_READS)
            
            async def _read_with_semaphore(file_path_str: str, file_path_obj: Path) -> tuple[str, str]:
                async with semaphore:
                    return await _read_file_async(file_path_obj)
            
            # Read all files concurrently (with semaphore limiting)
            read_tasks = [
                _read_with_semaphore(file_path_str, file_path_obj)
                for file_path_str, file_path_obj in files_to_read
            ]
            results = await asyncio.gather(*read_tasks)
            
            # Store results in dictionary
            for file_path_str, content in results:
                file_contents[file_path_str] = content

        # Second pass: process filtered modules with content
        for file_path, file_data in filtered_modules.items():
            # Get content from file_data or from batch read results
            content = file_data.get("content", "") or file_contents.get(file_path, "")

            # Apply file size filter
            file_size = len(content.encode("utf-8"))
            if request.max_file_size_kb and file_size > request.max_file_size_kb * 1024:
                warnings.append(f"Skipped {file_path}: exceeds size limit")
                continue

            total_files += 1
            total_size += file_size

            # Extract metadata
            language = file_data.get("language")
            if language:
                languages.add(language)

            tags = file_data.get("tags", [])
            file_summary = file_data.get("summary")
            complexity = file_data.get("complexity")
            visibility = file_data.get("visibility")

            # Extract frameworks and patterns from tags
            for tag in tags:
                if tag.startswith("framework:"):
                    frameworks.add(tag.split(":", 1)[1])
                elif tag.startswith("pattern:"):
                    patterns.add(tag.split(":", 1)[1])

            # Check if entry point
            if "entry_point" in tags or "purpose:entry_point" in tags:
                entry_points.append(file_path)

            # Extract ALL metadata from file_data
            file_metadata = file_data.get("metadata", {})

            # Build metadata with ALL fields from CodeAnalyzer
            metadata = FileMetadata(
                path=file_path,
                language=language,
                size_bytes=file_size,
                tags=tags,
                summary=file_summary,
                complexity=complexity,
                visibility=visibility,
                # Chunking metadata
                num_chunks=file_metadata.get("num_chunks"),
                total_tokens=file_metadata.get("total_tokens"),
                avg_chunk_size=file_metadata.get("avg_chunk_size"),
                # Rich metadata from CodeAnalyzer
                file_size_mb=file_metadata.get("file_size_mb"),
                function_count=file_metadata.get("function_count") or file_metadata.get("total_functions"),
                class_count=file_metadata.get("class_count") or file_metadata.get("total_classes"),
                import_count=file_metadata.get("import_count") or file_metadata.get("total_imports"),
                export_count=file_metadata.get("export_count") or file_metadata.get("total_exports"),
                # Code metrics
                total_lines=file_metadata.get("total_lines"),
                code_lines=file_metadata.get("code_lines"),
                comment_lines=file_metadata.get("comment_lines"),
                blank_lines=file_metadata.get("blank_lines"),
                cyclomatic_complexity=file_metadata.get("cyclomatic_complexity"),
                cognitive_complexity=file_metadata.get("cognitive_complexity"),
                maintainability_index=file_metadata.get("maintainability_index"),
                comment_ratio=file_metadata.get("comment_ratio"),
                # Additional metadata
                has_tests=file_metadata.get("has_tests"),
                entry_point=file_metadata.get("entry_point"),
                framework=file_metadata.get("framework"),
                patterns=file_metadata.get("patterns"),
                # Cleaning metadata
                original_lines=file_metadata.get("original_lines"),
                cleaned_lines=file_metadata.get("cleaned_lines"),
                lines_removed=file_metadata.get("lines_removed"),
                cleaning_applied=file_metadata.get("cleaning_applied"),
            )

            # Build parsed file
            content = file_data.get("content", "")
            raw_content = file_data.get("raw_content")
            chunks = file_data.get("chunks")  # Get the chunks data

            if content:
                successful_parses += 1

            modules[file_path] = ParsedFile(
                path=file_path,
                language=language,
                content=content,
                raw_content=raw_content,
                chunks=chunks,  # Include chunks in response
                metadata=metadata,
            )

        # Calculate success rate
        parse_success_rate = (
            (successful_parses / total_files * 100) if total_files > 0 else 0.0
        )

        # Add warnings from analysis
        if "warnings" in analysis_result:
            warnings.extend(analysis_result["warnings"])

        # Build summary
        summary = RepositorySummary(
            total_files=total_files,
            total_size_bytes=total_size,
            languages=sorted(list(languages)),
            frameworks=sorted(list(frameworks)),
            patterns=sorted(list(patterns)),
            entry_points=entry_points,
            parse_success_rate=round(parse_success_rate, 2),
            warnings=warnings,
        )

        # Calculate execution time
        execution_time = time.time() - start_time

        logger.info(
            f"Successfully parsed {request.repo_url}: "
            f"{total_files} files in {execution_time:.2f}s"
        )

        return ParseRepositoryResponse(
            repository_url=request.repo_url,
            git_ref=request.git_ref,
            commit_sha=None,  # Could be extracted from git log if needed
            modules=modules,
            summary=summary,
            execution_time_seconds=round(execution_time, 2),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error parsing {request.repo_url}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Internal server error: {str(e)}",
                "error_type": "internal",
            },
        )
    finally:
        # Cleanup cloned repository
        if repo_path:
            try:
                # repo_path is like /tmp/cba_repo_xxx/repo
                # We need to remove the parent sandbox directory
                sandbox_dir = Path(repo_path).parent
                await asyncio.to_thread(shutil.rmtree, sandbox_dir, ignore_errors=True)
                logger.info(f"Cleaned up temporary directory: {sandbox_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup repository: {e}")


def _matches_patterns(file_path: str, patterns: List[str]) -> bool:
    """Check if a file path matches any of the given glob patterns."""
    from fnmatch import fnmatch

    return any(fnmatch(file_path, pattern) for pattern in patterns)
