"""Schemas for parsing API endpoints."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ParseRepositoryRequest(BaseModel):
    """Request schema for parsing a GitHub repository."""

    repo_url: str = Field(
        ...,
        description="GitHub repository URL (HTTPS or SSH format)",
        examples=["https://github.com/user/repo", "git@github.com:user/repo.git"],
    )
    git_ref: str = Field(
        default="main",
        description="Git branch, tag, or commit to parse",
        examples=["main", "develop", "v1.0.0"],
    )
    include_patterns: Optional[List[str]] = Field(
        default=None,
        description="File patterns to include (e.g., ['*.py', '*.ts'])",
        examples=[["*.py", "*.js"], ["src/**/*.ts"]],
    )
    exclude_patterns: Optional[List[str]] = Field(
        default=None,
        description="File patterns to exclude (e.g., ['*test*.py', '*.min.js'])",
        examples=[["*test*.py", "*.min.js"]],
    )
    max_file_size_kb: Optional[int] = Field(
        default=500,
        description="Maximum file size in KB to parse",
        ge=1,
        le=5000,
    )
    enable_code_enrichment: bool = Field(
        default=True,
        description="Enable code enrichment in chonkie (extracts functions, classes, etc.)",
    )
    enable_formula_enrichment: bool = Field(
        default=False,
        description="Enable formula enrichment in chonkie (useful for scientific papers)",
    )
    enable_table_extraction: bool = Field(
        default=True,
        description="Enable table extraction from documents",
    )

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        """Validate that the repo URL is a valid GitHub URL."""
        from backend.utils.validators import validate_github_url

        validate_github_url(v)
        return v


class FileMetadata(BaseModel):
    """Metadata for a parsed file."""

    path: str = Field(..., description="Relative path of the file in the repository")
    language: Optional[str] = Field(
        None, description="Detected programming language"
    )
    size_bytes: int = Field(..., description="File size in bytes")
    tags: List[str] = Field(
        default_factory=list,
        description="Tags like 'framework:fastapi', 'pattern:async', 'purpose:test'",
    )
    summary: Optional[str] = Field(None, description="Brief summary of the file")
    complexity: Optional[str] = Field(
        None, description="Complexity level: low, medium, high"
    )
    visibility: Optional[str] = Field(
        None, description="Visibility: public, private, internal"
    )
    num_chunks: Optional[int] = Field(
        None, description="Number of chunks the file was split into"
    )
    total_tokens: Optional[int] = Field(
        None, description="Total tokens across all chunks"
    )
    avg_chunk_size: Optional[float] = Field(
        None, description="Average chunk size in tokens"
    )

    # Rich metadata from CodeAnalyzer
    file_size_mb: Optional[float] = Field(None, description="File size in MB")
    function_count: Optional[int] = Field(None, description="Number of functions")
    class_count: Optional[int] = Field(None, description="Number of classes")
    import_count: Optional[int] = Field(None, description="Number of imports")
    export_count: Optional[int] = Field(None, description="Number of exports")

    # Code metrics
    total_lines: Optional[int] = Field(None, description="Total lines including blanks")
    code_lines: Optional[int] = Field(None, description="Lines of code")
    comment_lines: Optional[int] = Field(None, description="Lines of comments")
    blank_lines: Optional[int] = Field(None, description="Blank lines")
    cyclomatic_complexity: Optional[int] = Field(None, description="Cyclomatic complexity")
    cognitive_complexity: Optional[int] = Field(None, description="Cognitive complexity")
    maintainability_index: Optional[float] = Field(None, description="Maintainability index (0-171)")
    comment_ratio: Optional[float] = Field(None, description="Ratio of comment lines to total lines")

    # Additional metadata
    has_tests: Optional[bool] = Field(None, description="Whether file contains tests")
    entry_point: Optional[bool] = Field(None, description="Whether file is an entry point")
    framework: Optional[str] = Field(None, description="Detected framework")
    patterns: Optional[List[str]] = Field(None, description="Detected design patterns")

    # Cleaning metadata
    original_lines: Optional[int] = Field(None, description="Lines before cleaning")
    cleaned_lines: Optional[int] = Field(None, description="Lines after cleaning")
    lines_removed: Optional[int] = Field(None, description="Lines removed during cleaning")
    cleaning_applied: Optional[bool] = Field(None, description="Whether cleaning was applied")


class ChunkDetail(BaseModel):
    """Details about a specific chunk of text."""

    index: int = Field(..., description="Chunk index (0-based)")
    text: str = Field(..., description="The chunked text content")
    token_count: int = Field(..., description="Number of tokens in this chunk")
    start_index: int = Field(..., description="Start character index in original content")
    end_index: int = Field(..., description="End character index in original content")


class ParsedFile(BaseModel):
    """Complete parsed file with content and metadata."""

    path: str = Field(..., description="Relative path of the file")
    language: Optional[str] = Field(None, description="Programming language")
    content: str = Field(..., description="Parsed/cleaned file content")
    raw_content: Optional[str] = Field(
        None, description="Original file content before cleaning"
    )
    chunks: Optional[List[ChunkDetail]] = Field(
        None, description="Detailed chunk information for this file"
    )
    metadata: FileMetadata = Field(..., description="File metadata and analysis")


class RepositorySummary(BaseModel):
    """Summary statistics for the parsed repository."""

    total_files: int = Field(..., description="Total number of files parsed")
    total_size_bytes: int = Field(..., description="Total size of all parsed files")
    languages: List[str] = Field(
        default_factory=list, description="List of detected languages"
    )
    frameworks: List[str] = Field(
        default_factory=list, description="List of detected frameworks"
    )
    patterns: List[str] = Field(
        default_factory=list, description="List of detected patterns"
    )
    entry_points: List[str] = Field(
        default_factory=list, description="Detected entry point files"
    )
    parse_success_rate: float = Field(
        ..., description="Percentage of files successfully parsed", ge=0.0, le=100.0
    )
    warnings: List[str] = Field(
        default_factory=list, description="Warnings encountered during parsing"
    )


class ParseRepositoryResponse(BaseModel):
    """Response schema for repository parsing."""

    repository_url: str = Field(..., description="The GitHub repository URL")
    git_ref: str = Field(..., description="The git reference that was parsed")
    commit_sha: Optional[str] = Field(
        None, description="The actual commit SHA that was parsed"
    )
    modules: Dict[str, ParsedFile] = Field(
        ..., description="Dictionary of parsed files keyed by path"
    )
    summary: RepositorySummary = Field(
        ..., description="Summary statistics for the repository"
    )
    execution_time_seconds: float = Field(
        ..., description="Time taken to complete the parsing", ge=0.0
    )


class ParseErrorResponse(BaseModel):
    """Error response for parsing failures."""

    error: str = Field(..., description="Error message")
    error_type: str = Field(
        ..., description="Type of error: 'validation', 'git', 'parsing', 'timeout'"
    )
    details: Optional[Dict] = Field(None, description="Additional error details")
