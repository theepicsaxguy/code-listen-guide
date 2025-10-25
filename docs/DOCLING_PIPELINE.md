# Docling Pipeline Documentation

## Overview

The Docling Pipeline is a comprehensive system for parsing, cleaning, and tagging codebases using IBM's Docling toolkit. It provides advanced document understanding capabilities beyond basic AST parsing, enabling the creation of rich, semantically-annotated code representations for the audiobook generation workflow.

## Architecture

The pipeline consists of three main components:

### 1. DoclingPipeline (`backend/services/docling_pipeline.py`)

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

High-level service that combines git operations with the Docling pipeline:

**Features:**
- Git repository cloning
- Repository size validation
- Dual-mode analysis (Docling or tree-sitter fallback)
- Automatic cleanup of temporary directories

### 3. Tree-sitter Fallback (`backend/tools/code_parser_tools.py`)

Basic parser used when Docling is unavailable or for specific file types:

**Supports:**
- Python, JavaScript, TypeScript
- Function and class extraction
- Import statement detection

## Installation

### Prerequisites

```bash
# Install Docling and dependencies
pip install docling==2.17.0 docling-core==2.6.2

# Install git support
pip install gitpython==3.1.45
```

### Optional: Model Prefetching

For offline usage or air-gapped environments:

```bash
# Download Docling models
docling-tools models download

# Or set custom artifacts path
export DOCLING_ARTIFACTS_PATH="/path/to/models"
```

## Usage

### Basic Usage

```python
from backend.services.repository_analyzer import RepositoryAnalyzer

# Analyze a GitHub repository
analyzer = RepositoryAnalyzer(
    repo_url="https://github.com/user/repo",
    git_ref="main",
    use_docling=True,
)

result = await analyzer.analyze_full()
```

### Direct Pipeline Usage

```python
from backend.services.docling_pipeline import DoclingPipeline
from pathlib import Path

# Initialize pipeline
pipeline = DoclingPipeline(
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
python -m backend.examples.test_docling_pipeline https://github.com/user/repo

# Test with local directory
python -m backend.examples.test_docling_pipeline /path/to/repo

# Test specific branch
python -m backend.examples.test_docling_pipeline https://github.com/user/repo develop
```

## Pipeline Stages

### Stage 1: Parse

**Purpose:** Extract structured content from files

**Operations:**
- Document conversion with Docling
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

**Example:**
```python
# Before cleaning
def    foo( ):
    return     42



def bar():
    pass

# After cleaning
def foo():
    return 42

def bar():
    pass
```

### Stage 3: Tag

**Purpose:** Add semantic metadata and classifications

**Tag Categories:**

1. **Language**: Programming languages used
   ```python
   tags["language"] = ["Python", "JavaScript"]
   ```

2. **Framework**: Detected frameworks/libraries
   ```python
   tags["framework"] = ["FastAPI", "React"]
   ```

3. **Pattern**: Design patterns identified
   ```python
   tags["pattern"] = ["Object-Oriented", "Async/Await"]
   ```

4. **Complexity**: Code complexity level
   ```python
   tags["complexity"] = "medium"  # low, medium, high
   ```

5. **Visibility**: API visibility
   ```python
   tags["visibility"] = "public"  # public, private, internal
   ```

6. **Purpose**: File purpose
   ```python
   tags["purpose"] = "implementation"  # test, config, documentation, etc.
   ```

## Configuration

### DoclingPipeline Options

```python
pipeline = DoclingPipeline(
    enable_code_enrichment=True,     # Advanced code understanding
    enable_formula_enrichment=False,  # Math formula parsing
    artifacts_path=None,              # Custom model path (for offline)
)
```

### RepositoryAnalyzer Options

```python
analyzer = RepositoryAnalyzer(
    repo_url="https://github.com/user/repo",
    git_ref="main",
    use_docling=True,        # Use Docling (True) or tree-sitter (False)
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

## Output Format

### Complete Analysis Result

```json
{
  "repository_url": "https://github.com/user/repo",
  "git_ref": "main",
  "analysis_mode": "docling",
  "structure": {
    "files": [...],
    "languages": ["Python", "JavaScript"],
    "total_size_bytes": 1234567,
    "file_count": 42
  },
  "parsed": {
    "repository_path": "/tmp/repo_analysis_xyz",
    "files": [
      {
        "file_path": "src/main.py",
        "content_type": "code",
        "content": "...",
        "tags": {
          "language": ["Python"],
          "framework": ["FastAPI"],
          "pattern": ["Object-Oriented"],
          "complexity": "medium",
          "visibility": "public",
          "purpose": "entry_point"
        },
        "code_blocks": [...],
        "metadata": {...}
      }
    ],
    "summary": {
      "total_files": 42,
      "successfully_parsed": 40,
      "failed_to_parse": 2,
      "parse_success_rate": 95.2
    },
    "dependency_graph": {...},
    "entry_points": ["src/main.py", "src/cli.py"]
  }
}
```

## Integration with Audiobook Workflow

The Docling pipeline integrates with the audiobook generation workflow as follows:

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
│  - Run Docling │
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

### Event payloads during audiobook generation

Each workflow stage streams `ChatMessage` objects that wrap `TextContent` blocks. The
runtime forwards the resolved `.text` from those messages through `emit_job_event`,
so downstream listeners receive plain strings for outline previews, chapter script
progress, audio URLs, and the final bundle metadata. This keeps the event contract
stable even as agents emit richer content internally.

## Troubleshooting

### Common Issues

#### 1. Docling Not Installed

**Error:**
```
RuntimeError: Docling is not installed
```

**Solution:**
```bash
pip install docling==2.17.0 docling-core==2.6.2
```

#### 2. GitPython Missing

**Error:**
```
RuntimeError: GitPython not installed
```

**Solution:**
```bash
pip install gitpython==3.1.45
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

#### 4. Automatic Fallback

If Docling initialization fails, the system automatically falls back to tree-sitter:

```
WARNING: Failed to initialize Docling: [error]. Falling back to tree-sitter
```

This is expected behavior and ensures the pipeline continues working even without Docling.

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
   pipeline = DoclingPipeline(
       enable_code_enrichment=True,
       enable_formula_enrichment=False,  # Faster
   )
   ```

3. **Use shallow clones** (already default):
   ```python
   # Repository is cloned with depth=1 for speed
   ```

## Development

### Adding New Content Types

To support a new content type:

1. Add to `ContentType` enum in `docling_pipeline.py`:
   ```python
   class ContentType(str, Enum):
       NEW_TYPE = "new_type"
   ```

2. Update `_detect_content_type()` method:
   ```python
   if suffix in {".ext"}:
       return ContentType.NEW_TYPE
   ```

### Adding New Tag Categories

To add a new tagging dimension:

1. Add to `TagCategory` enum:
   ```python
   class TagCategory(str, Enum):
       NEW_CATEGORY = "new_category"
   ```

2. Implement detection in `tag_content()`:
   ```python
   tags[TagCategory.NEW_CATEGORY] = self._detect_new_category(content)
   ```

3. Add detection method:
   ```python
   def _detect_new_category(self, content: str) -> Any:
       # Detection logic
       return detected_value
   ```

### Testing

Run the test suite:

```bash
# Test with sample repository
python -m backend.examples.test_docling_pipeline https://github.com/psf/requests

# Test with local directory
python -m backend.examples.test_docling_pipeline ./backend

# Run automated tests (when available)
pytest backend/tests/test_docling_pipeline.py
```

## References

- [Docling Documentation](https://ds4sd.github.io/docling/)
- [Docling GitHub](https://github.com/DS4SD/docling)
- [Docling Paper](https://arxiv.org/abs/2408.09869)
- [Project Plan](../plans/docling-parser-plan.md)
- [Sample Reference](../samples/docling.md)

## Future Enhancements

Planned improvements:

1. **Full Dependency Graph**: Complete import/export tracking
2. **Call Graph Analysis**: Function-level call relationships
3. **Semantic Clustering**: ML-based file grouping
4. **Incremental Processing**: Only parse changed files
5. **Parallel Processing**: Multi-threaded file parsing
6. **Custom Enrichments**: Plugin system for custom tags
7. **Output Formats**: Export to DocTags, JSON-LD, etc.

## Support

For issues or questions:

1. Check this documentation
2. Review examples in `backend/examples/`
3. Open an issue on GitHub
4. Reference the Docling documentation for toolkit-specific questions
