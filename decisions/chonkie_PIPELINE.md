# chonkie Pipeline Documentation

## Overview

The chonkie Pipeline is a comprehensive system for parsing, cleaning, and tagging codebases using IBM's chonkie toolkit. It provides advanced document understanding capabilities beyond basic AST parsing, enabling the creation of rich, semantically-annotated code representations for the audiobook generation workflow.

## Architecture

The pipeline consists of three main components:

### 1. chonkiePipeline (`backend/services/chonkie_pipeline.py`)

The core pipeline service that orchestrates the three-stage process:

```
┌─────────┐    ┌──────────┐    ┌─────────┐
│  Parse  │ -> │  Clean   │ -> │   Tag   │
└─────────┘    └──────────┘    └─────────┘
```

**Capabilities:**
- Multi-format document parsing (code, markdown, JSON, YAML, etc.)
- Code enrichment with language detection
- Content normalization and cleaning
- Semantic tagging and classification
- Dependency graph generation
- Entry point identification

### 2. RepositoryAnalyzer (`backend/services/repository_analyzer.py`)

High-level service that combines git operations with the chonkie pipeline.

**Features:**
- Git repository cloning
- Repository size validation
- Chonkie-based code analysis
- Automatic cleanup of temporary directories

## Installation

### Prerequisites

```bash
# Install chonkie and dependencies
pip install chonkie==1.4.0

# Install git support
pip install gitpython
```

### Optional: Model Prefetching

For offline usage or air-gapped environments:

```bash
# Download chonkie models
chonkie-tools models download

# Or set custom artifacts path
export chonkie_ARTIFACTS_PATH="/path/to/models"
```

## Usage

### Basic Usage

```python
from backend.services.repository_analyzer import RepositoryAnalyzer

# Analyze a GitHub repository
analyzer = RepositoryAnalyzer(
    repo_url="https://github.com/user/repo",
    git_ref="main",
    use_chonkie=True,
)

result = await analyzer.analyze_full()
```

### Direct Pipeline Usage

```python
from backend.services.chonkie_pipeline import chonkiePipeline
from pathlib import Path

# Initialize pipeline
pipeline = chonkiePipeline(
    enable_code_enrichment=True,
    enable_formula_enrichment=False,
)

# Parse a single file
file_result = await pipeline.parse_file(Path("script.py"))

# Process entire codebase
codebase_result = await pipeline.process_pipeline(Path("/repo"))
```

### Command Line Testing

```bash
# Test with a GitHub repository
python -m backend.examples.test_chonkie_pipeline https://github.com/user/repo

# Test with local directory
python -m backend.examples.test_chonkie_pipeline /path/to/repo

# Test specific branch
python -m backend.examples.test_chonkie_pipeline https://github.com/user/repo develop
```

## Pipeline Stages

### Stage 1: Parse

**Purpose:** Extract structured content from files

**Operations:**
- Document conversion with chonkie
- Code block extraction
- Table and image detection
- Formula parsing (if enabled)
- Structure extraction (headings, sections)

**Output:**
```json
{
  "file_path": "src/main.py",
  "content_type": "code",
  "content": "markdown formatted content",
  "structure": { "sections": [], "headings": [] },
  "code_blocks": [
    { "language": "python", "content": "..." }
  ],
  "metadata": { "file_name": "main.py", "file_size": 1234 }
}
```

### Stage 2: Clean

**Purpose:** Normalize and filter content

**Operations:**
- Whitespace normalization
- Excessive blank line removal
- Minified code detection
- Binary content filtering
- Code block cleaning

### Stage 3: Tag

**Purpose:** Add semantic metadata and classifications

**Tag Categories:**

1. **Language**: Programming languages used
2. **Framework**: Detected frameworks/libraries
3. **Pattern**: Design patterns identified
4. **Complexity**: Code complexity level (low, medium, high)
5. **Visibility**: API visibility (public, private, internal)
6. **Purpose**: File purpose (test, config, documentation, implementation, etc.)

## Configuration

### chonkiePipeline Options

```python
pipeline = chonkiePipeline(
    enable_code_enrichment=True,     # Advanced code understanding
    enable_formula_enrichment=False,  # Math formula parsing
    enable_table_extraction=True,     # Extract tables from docs
    artifacts_path=None,              # Custom model path (for offline)
)
```

### RepositoryAnalyzer Options

```python
analyzer = RepositoryAnalyzer(
    repo_url="https://github.com/user/repo",
    git_ref="main",
    use_chonkie=True,        # Use chonkie for parsing
    max_repo_size_mb=500,    # Maximum repository size
)
```

### File Filtering

**Include Patterns** (default):
```python
include_patterns = [
    "*.py", "*.js", "*.ts", "*.tsx", "*.jsx",  # Code
    "*.md", "*.rst", "*.txt",                   # Docs
    "*.json", "*.yaml", "*.yml", "*.toml",      # Config
    "README*", "LICENSE*"                        # Meta
]
```

**Exclude Patterns** (default):
```python
exclude_patterns = [
    ".git", "node_modules", "__pycache__",
    ".venv", "venv", "dist", "build",
    "*.pyc", "*.pyo", "*.so"
]
```

## Integration with Audiobook Workflow

The chonkie pipeline integrates with the audiobook generation workflow:

```
┌────────────────┐
│ User submits   │
│ repository URL │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Analyzer Agent │ (uses RepositoryAnalyzer)
│  - Clone repo  │
│  - Run chonkie │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Outline Agent  │ (consumes tagged data)
│  - Group files │
│  - Plan chpts  │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Script Agent   │ (uses tags for context)
│  - Generate    │
│    narration   │
└────────────────┘
```

**Key Benefits:**
1. **Richer Context**: Tags help outline agent group related files
2. **Smart Filtering**: Minified/generated code automatically skipped
3. **Entry Points**: Narration can start from identified entry points
4. **Complexity Awareness**: Adjust narration depth based on complexity tags

## Troubleshooting

### Common Issues

#### 1. chonkie Not Installed

**Error:**
```
RuntimeError: chonkie is not installed
```

**Solution:**
```bash
pip install chonkie==1.4.0
```

#### 2. GitPython Missing

**Error:**
```
RuntimeError: GitPython not installed
```

**Solution:**
```bash
pip install gitpython
```

#### 3. Repository Too Large

**Error:**
```
ValueError: Repository size (750MB) exceeds maximum allowed (500MB)
```

**Solution:**
```python
analyzer = RepositoryAnalyzer(
    repo_url="...",
    max_repo_size_mb=1000,  # Increase limit
)
```

### Performance Optimization

**For Large Repositories:**

1. **Adjust file patterns** to parse only relevant files:
   ```python
   result = await pipeline.process_pipeline(
       repo_path,
       include_patterns=["*.py", "*.md"],  # Python and docs only
   )
   ```

2. **Disable formula enrichment** if not needed:
   ```python
   pipeline = chonkiePipeline(
       enable_code_enrichment=True,
       enable_formula_enrichment=False,  # Faster
   )
   ```

## Testing

Run tests with pytest:

```bash
# Run chonkie tests
pytest -m chonkie -v

# Run all tests
pytest -v
```

Test with example script:

```bash
# Test with sample repository
python -m backend.examples.test_chonkie_pipeline https://github.com/psf/requests

# Test with local directory
python -m backend.examples.test_chonkie_pipeline ./backend
```

## References

- [chonkie Documentation](https://ds4sd.github.io/chonkie/)
- [chonkie GitHub](https://github.com/DS4SD/chonkie)
- [Project Plan](../Plan.md)
- [Sample Reference](../samples/chonkie.md)

## Support

For issues or questions:

1. Check this documentation
2. Review examples in `backend/examples/`
3. Open an issue on GitHub
4. Reference the chonkie documentation for toolkit-specific questions
