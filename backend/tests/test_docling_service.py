"""
Tests for Docling pipeline service.

These tests verify the parse, clean, and tag functionality of the Docling pipeline.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import sys

# Mock docling before import
docling_mock = MagicMock()
sys.modules["docling"] = docling_mock
sys.modules["docling.document_converter"] = MagicMock()
sys.modules["docling.datamodel.base_models"] = MagicMock()
sys.modules["docling.datamodel.pipeline_options"] = MagicMock()

from backend.services.docling_pipeline import DoclingPipeline, ContentType, TagCategory


@pytest.mark.docling
@pytest.mark.unit
class TestDoclingPipeline:
    """Test Docling pipeline functionality."""

    @pytest.fixture
    def mock_docling_converter(self):
        """Create a mock Docling converter."""
        converter = MagicMock()

        # Mock document result
        mock_doc = MagicMock()
        mock_doc.export_to_markdown.return_value = "# Test Document\n\nContent here"
        mock_doc.main_text = MagicMock()
        mock_doc.main_text.items = []

        mock_result = MagicMock()
        mock_result.document = mock_doc

        converter.convert.return_value = mock_result
        return converter

    @pytest.fixture
    def pipeline(self, mock_docling_converter):
        """Create a DoclingPipeline instance with mocked converter."""
        with patch("backend.services.docling_pipeline.HAS_DOCLING", True):
            with patch(
                "backend.services.docling_pipeline.DocumentConverter",
                return_value=mock_docling_converter,
            ):
                pipeline = DoclingPipeline(
                    enable_code_enrichment=True, enable_formula_enrichment=False
                )
                pipeline.converter = mock_docling_converter
                return pipeline

    def test_init_with_docling_available(self, mock_docling_converter):
        """Test initialization when Docling is available."""
        with patch("backend.services.docling_pipeline.HAS_DOCLING", True):
            with patch(
                "backend.services.docling_pipeline.DocumentConverter",
                return_value=mock_docling_converter,
            ):
                pipeline = DoclingPipeline()
                assert pipeline.enable_code_enrichment is True
                assert pipeline.enable_formula_enrichment is False

    def test_init_without_docling_raises_error(self):
        """Test initialization fails when Docling is not available."""
        with patch("backend.services.docling_pipeline.HAS_DOCLING", False):
            with pytest.raises(RuntimeError, match="Docling is not installed"):
                DoclingPipeline()

    def test_detect_content_type_code(self, pipeline):
        """Test content type detection for code files."""
        assert pipeline._detect_content_type(Path("test.py")) == ContentType.CODE
        assert pipeline._detect_content_type(Path("app.js")) == ContentType.CODE
        assert pipeline._detect_content_type(Path("main.ts")) == ContentType.CODE

    def test_detect_content_type_documentation(self, pipeline):
        """Test content type detection for documentation files."""
        assert (
            pipeline._detect_content_type(Path("README.md"))
            == ContentType.DOCUMENTATION
        )
        assert (
            pipeline._detect_content_type(Path("docs.rst")) == ContentType.DOCUMENTATION
        )

    def test_detect_content_type_configuration(self, pipeline):
        """Test content type detection for configuration files."""
        assert (
            pipeline._detect_content_type(Path("config.json"))
            == ContentType.CONFIGURATION
        )
        assert (
            pipeline._detect_content_type(Path("settings.yaml"))
            == ContentType.CONFIGURATION
        )
        assert (
            pipeline._detect_content_type(Path("Dockerfile"))
            == ContentType.CONFIGURATION
        )

    @pytest.mark.asyncio
    async def test_parse_file_success(self, pipeline, tmp_path):
        """Test successful file parsing."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        result = await pipeline.parse_file(test_file)

        assert result["file_path"] == str(test_file)
        assert result["content_type"] == ContentType.CODE
        assert "content" in result
        assert "metadata" in result
        assert result["metadata"]["file_name"] == "test.py"

    @pytest.mark.asyncio
    async def test_parse_file_not_found(self, pipeline):
        """Test parsing non-existent file."""
        with pytest.raises(FileNotFoundError):
            await pipeline.parse_file(Path("/nonexistent/file.py"))

    @pytest.mark.asyncio
    async def test_clean_content_removes_excessive_whitespace(self, pipeline):
        """Test content cleaning removes excessive whitespace."""
        parsed_data = {"content": "line1\n\n\n\n\nline2", "metadata": {}}

        cleaned = await pipeline.clean_content(parsed_data)

        # Should reduce excessive blank lines
        assert cleaned["content"].count("\n\n\n\n") == 0

    @pytest.mark.asyncio
    async def test_clean_content_detects_minified_code(self, pipeline):
        """Test that minified code is detected and marked."""
        # Create content that looks minified (very long lines)
        minified_content = "a" * 300 + "\n" + "b" * 300 + "\n" + "c" * 300

        parsed_data = {"content": minified_content, "metadata": {}}

        cleaned = await pipeline.clean_content(parsed_data)

        assert cleaned["metadata"].get("is_minified") is True

    @pytest.mark.asyncio
    async def test_tag_content_detects_language(self, pipeline):
        """Test language detection in tagging."""
        cleaned_data = {"file_path": "test.py", "content": "import os\nprint('hello')"}

        tagged = await pipeline.tag_content(cleaned_data)

        assert "tags" in tagged
        assert TagCategory.LANGUAGE in tagged["tags"]
        assert "Python" in tagged["tags"][TagCategory.LANGUAGE]

    @pytest.mark.asyncio
    async def test_tag_content_detects_frameworks(self, pipeline):
        """Test framework detection in tagging."""
        cleaned_data = {
            "file_path": "app.py",
            "content": "from fastapi import FastAPI\napp = FastAPI()",
        }

        tagged = await pipeline.tag_content(cleaned_data)

        assert TagCategory.FRAMEWORK in tagged["tags"]
        assert "FastAPI" in tagged["tags"][TagCategory.FRAMEWORK]

    @pytest.mark.asyncio
    async def test_tag_content_assesses_complexity(self, pipeline):
        """Test complexity assessment."""
        # Short file - low complexity
        short_data = {"file_path": "short.py", "content": "print('hello')\n" * 10}
        tagged_short = await pipeline.tag_content(short_data)
        assert tagged_short["tags"][TagCategory.COMPLEXITY] == "low"

        # Long file - high complexity
        long_data = {"file_path": "long.py", "content": "print('hello')\n" * 250}
        tagged_long = await pipeline.tag_content(long_data)
        assert tagged_long["tags"][TagCategory.COMPLEXITY] == "high"

    @pytest.mark.asyncio
    async def test_tag_content_classifies_purpose(self, pipeline):
        """Test purpose classification."""
        test_file_data = {
            "file_path": "test_module.py",
            "content": "def test_something(): pass",
        }
        tagged = await pipeline.tag_content(test_file_data)
        assert tagged["tags"][TagCategory.PURPOSE] == "test"

        config_file_data = {"file_path": "config.yaml", "content": "key: value"}
        tagged_config = await pipeline.tag_content(config_file_data)
        assert tagged_config["tags"][TagCategory.PURPOSE] == "configuration"

    def test_should_exclude_patterns(self, pipeline):
        """Test file exclusion logic."""
        repo_path = Path("/repo")

        # Should exclude node_modules
        assert (
            pipeline._should_exclude(
                Path("/repo/node_modules/package/file.js"),
                repo_path,
                ["node_modules", ".git"],
            )
            is True
        )

        # Should not exclude regular files
        assert (
            pipeline._should_exclude(
                Path("/repo/src/main.py"), repo_path, ["node_modules", ".git"]
            )
            is False
        )

    def test_should_include_patterns(self, pipeline):
        """Test file inclusion logic."""
        # Should include Python files
        assert pipeline._should_include(Path("test.py"), ["*.py", "*.js"]) is True

        # Should not include excluded types
        assert pipeline._should_include(Path("test.exe"), ["*.py", "*.js"]) is False

    def test_detect_language_mapping(self, pipeline):
        """Test language detection for various file extensions."""
        test_cases = [
            (Path("test.py"), "Python"),
            (Path("app.js"), "JavaScript"),
            (Path("main.ts"), "TypeScript"),
            (Path("Main.java"), "Java"),
            (Path("server.go"), "Go"),
        ]

        for file_path, expected_lang in test_cases:
            result = pipeline._detect_language(file_path, "")
            assert expected_lang in result

    def test_detect_frameworks_multiple(self, pipeline):
        """Test detection of multiple frameworks in single file."""
        content = """
        from fastapi import FastAPI
        import React from 'react'
        from django.conf import settings
        """

        frameworks = pipeline._detect_frameworks(content)

        assert "FastAPI" in frameworks
        assert "React" in frameworks or "Django" in frameworks

    def test_detect_patterns(self, pipeline):
        """Test design pattern detection."""
        # Async pattern
        async_content = "async def fetch(): await get_data()"
        assert "Async/Await" in pipeline._detect_patterns(async_content)

        # Generator pattern
        generator_content = "def gen(): yield item"
        assert "Generator" in pipeline._detect_patterns(generator_content)

        # OOP pattern
        oop_content = "class MyClass:\n    def __init__(self):\n        pass"
        assert "Object-Oriented" in pipeline._detect_patterns(oop_content)

    def test_classify_visibility(self, pipeline):
        """Test visibility classification."""
        # Private file
        assert pipeline._classify_visibility(Path("_internal.py"), "") == "private"

        # Public file with exports
        assert (
            pipeline._classify_visibility(
                Path("api.py"), "export function doSomething()"
            )
            == "public"
        )

        # Internal file
        assert pipeline._classify_visibility(Path("utils.py"), "") == "internal"

    def test_is_likely_minified(self, pipeline):
        """Test minified code detection."""
        # Regular code - not minified
        regular_code = "def function():\n    return True\n\ndef another():\n    pass"
        assert pipeline._is_likely_minified(regular_code) is False

        # Minified code - very long lines
        minified_code = "x=" + "a" * 300 + ";y=" + "b" * 300
        assert pipeline._is_likely_minified(minified_code) is True

    def test_normalize_whitespace(self, pipeline):
        """Test whitespace normalization."""
        content = "line1    multiple    spaces\nline2  here"
        normalized = pipeline._normalize_whitespace(content)

        # Should reduce multiple spaces to single
        assert "   " not in normalized

    def test_remove_excessive_blank_lines(self, pipeline):
        """Test removal of excessive blank lines."""
        content = "line1\n\n\n\n\n\nline2"
        cleaned = pipeline._remove_excessive_blank_lines(content)

        # Should have max 3 consecutive newlines
        assert "\n\n\n\n" not in cleaned

    def test_identify_entry_points(self, pipeline):
        """Test entry point identification."""
        files = [
            {"file_path": "/repo/main.py"},
            {"file_path": "/repo/app.py"},
            {"file_path": "/repo/index.js"},
            {"file_path": "/repo/utils.py"},
        ]

        entry_points = pipeline._identify_entry_points(files, Path("/repo"))

        assert "/repo/main.py" in entry_points
        assert "/repo/app.py" in entry_points
        assert "/repo/index.js" in entry_points
        assert "/repo/utils.py" not in entry_points


@pytest.mark.docling
@pytest.mark.slow
@pytest.mark.integration
class TestDoclingPipelineIntegration:
    """Integration tests for Docling pipeline (requires Docling installation)."""

    @pytest.mark.skip(reason="Requires Docling installation and real files")
    @pytest.mark.asyncio
    async def test_full_pipeline_execution(self, tmp_path):
        """Test complete pipeline on a real directory."""
        # Create test repository structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "README.md").write_text("# Test Repo")

        pipeline = DoclingPipeline()
        result = await pipeline.process_pipeline(tmp_path)

        assert "files" in result
        assert "summary" in result
        assert result["summary"]["total_files"] > 0
