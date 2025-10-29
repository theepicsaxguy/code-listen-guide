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


class ParsedFile(BaseModel):
    """Complete parsed file with content and metadata."""

    path: str = Field(..., description="Relative path of the file")
    language: Optional[str] = Field(None, description="Programming language")
    content: str = Field(..., description="Parsed/cleaned file content")
    raw_content: Optional[str] = Field(
        None, description="Original file content before cleaning"
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
