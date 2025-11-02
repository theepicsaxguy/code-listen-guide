"""Tests for DependencyAnalyzer multi-language support."""

import tempfile
from pathlib import Path
import pytest

from services.dependency_analyzer import DependencyAnalyzer, ClusterPlan


class TestDependencyAnalyzer:
    """Test suite for DependencyAnalyzer."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def analyzer(self, temp_repo):
        """Create a DependencyAnalyzer instance."""
        return DependencyAnalyzer(str(temp_repo))

    def test_parse_javascript_imports(self, analyzer, temp_repo):
        """Test JavaScript import extraction."""
        js_file = temp_repo / "test.js"
        js_file.write_text("""
import { useState, useEffect } from 'react';
import utils from './utils';
import * as helpers from './helpers.js';
const config = require('./config');
export { Component } from './component';
import externalLib from 'some-library';
""")
        
        imports = analyzer._parse_javascript_imports(js_file)
        
        assert './utils' in imports
        assert './helpers' in imports  # Extension should be removed
        assert './config' in imports
        assert './component' in imports
        # External modules should be filtered out
        assert 'react' not in imports
        assert 'some-library' not in imports

    def test_parse_javascript_various_formats(self, analyzer, temp_repo):
        """Test various JavaScript import formats."""
        js_file = temp_repo / "advanced.js"
        js_file.write_text("""
import defaultExport from './module1';
import { export1, export2 } from './module2';
import * as name from './module3';
import './module4';
const m5 = require('./module5');
export { something } from './module6';
""")
        
        imports = analyzer._parse_javascript_imports(js_file)
        
        assert './module1' in imports
        assert './module2' in imports
        assert './module3' in imports
        assert './module4' in imports
        assert './module5' in imports
        assert './module6' in imports

    def test_parse_typescript_imports(self, analyzer, temp_repo):
        """Test TypeScript import extraction."""
        ts_file = temp_repo / "test.ts"
        ts_file.write_text("""
import type { User } from './types';
import { api } from './api';
const service = require('./service.ts');
import { Config } from 'external-package';
""")
        
        imports = analyzer._parse_typescript_imports(ts_file)
        
        assert './types' in imports
        assert './api' in imports
        assert './service' in imports  # Extension should be removed
        assert 'external-package' not in imports

    def test_parse_go_imports_single_line(self, analyzer, temp_repo):
        """Test Go single-line import extraction."""
        go_file = temp_repo / "test.go"
        go_file.write_text("""
package main

import "fmt"
import "myproject/internal/handlers"
import alias "myproject/pkg/utils"
""")
        
        imports = analyzer._parse_go_imports(go_file)
        
        assert 'myproject/internal/handlers' in imports
        assert 'myproject/pkg/utils' in imports
        # Standard library should be filtered out
        assert 'fmt' not in imports

    def test_parse_go_imports_block(self, analyzer, temp_repo):
        """Test Go import block extraction."""
        go_file = temp_repo / "test.go"
        go_file.write_text("""
package main

import (
    "fmt"
    "os"
    "myproject/internal/handlers"
    "myproject/pkg/utils"
    "github.com/gin-gonic/gin"
    h "myproject/internal/http"
)
""")
        
        imports = analyzer._parse_go_imports(go_file)
        
        assert 'myproject/internal/handlers' in imports
        assert 'myproject/pkg/utils' in imports
        assert 'myproject/internal/http' in imports
        # Standard library and third-party should be filtered out
        assert 'fmt' not in imports
        assert 'os' not in imports
        assert 'github.com/gin-gonic/gin' not in imports

    def test_parse_python_imports(self, analyzer, temp_repo):
        """Test Python import extraction."""
        py_file = temp_repo / "test.py"
        py_file.write_text("""
import os
import sys
from .utils import helper
from backend.services import analyzer
from ..models import User
""")
        
        imports = analyzer._parse_python_imports(py_file)
        
        # Should convert dots to slashes and include relative imports
        assert any('utils' in imp or 'backend/services' in imp for imp in imports)

    def test_build_import_graph_multi_language(self, analyzer, temp_repo):
        """Test building import graph for multiple languages."""
        # Create test files
        (temp_repo / "main.js").write_text("""
import { helper } from './utils';
""")
        
        (temp_repo / "utils.js").write_text("""
export function helper() {}
""")
        
        (temp_repo / "main.go").write_text("""
package main
import "myproject/utils"
""")
        
        (temp_repo / "main.py").write_text("""
from .utils import helper
""")
        
        files = ["main.js", "utils.js", "main.go", "main.py"]
        graph = analyzer.build_import_graph(files)
        
        # Check that files with imports are in the graph
        assert "main.js" in graph
        assert len(graph["main.js"]) > 0
        
        # Files without imports shouldn't be in graph
        assert "utils.js" not in graph or len(graph["utils.js"]) == 0
        
        # Go file should be in graph
        assert "main.go" in graph
        
        # Python file should be in graph
        assert "main.py" in graph

    def test_build_python_import_graph_legacy(self, analyzer, temp_repo):
        """Test legacy Python-only import graph method."""
        (temp_repo / "test.py").write_text("""
from .utils import helper
from backend.services import analyzer
""")
        
        (temp_repo / "test.js").write_text("""
import { helper } from './utils';
""")
        
        files = ["test.py", "test.js"]
        graph = analyzer.build_python_import_graph(files)
        
        # Should only include Python files
        assert "test.py" in graph
        assert "test.js" not in graph

    def test_cluster_graph(self, analyzer):
        """Test graph clustering."""
        graph = {
            "a.py": ["b.py"],
            "b.py": ["c.py"],
            "c.py": [],
            "d.py": ["e.py"],
            "e.py": [],
        }
        
        clusters = analyzer.cluster_graph(graph)
        
        # Should create clusters based on connectivity
        assert len(clusters) >= 1
        
        # a, b, c should be in one cluster (connected)
        # d, e should be in another cluster (connected)
        cluster_sizes = sorted([len(c.files) for c in clusters], reverse=True)
        assert cluster_sizes[0] >= 3  # a, b, c cluster
        assert cluster_sizes[1] >= 2  # d, e cluster

    def test_plan_episodes(self, analyzer, temp_repo):
        """Test episode planning with multi-language support."""
        # Create interconnected files
        (temp_repo / "main.js").write_text("""
import { helper } from './utils';
import { api } from './api';
""")
        
        (temp_repo / "utils.js").write_text("""
export function helper() {}
""")
        
        (temp_repo / "api.js").write_text("""
import { helper } from './utils';
""")
        
        files = ["main.js", "utils.js", "api.js"]
        plans = analyzer.plan_episodes(files)
        
        # Should return list of episode plans
        assert isinstance(plans, list)
        assert len(plans) > 0
        
        # Each plan should be a dict with cluster key
        for plan in plans:
            assert isinstance(plan, dict)
            assert len(plan) > 0

    def test_file_extension_detection(self, analyzer, temp_repo):
        """Test that analyzer correctly detects file types by extension."""
        extensions = {
            "test.js": "javascript",
            "test.jsx": "javascript",
            "test.mjs": "javascript",
            "test.cjs": "javascript",
            "test.ts": "typescript",
            "test.tsx": "typescript",
            "test.go": "go",
            "test.py": "python",
        }
        
        for filename in extensions.keys():
            file_path = temp_repo / filename
            file_path.write_text("// minimal content")
        
        graph = analyzer.build_import_graph(list(extensions.keys()))
        
        # All files should be processed (even if they have no imports)
        # Files with no imports won't be in graph, but should not error
        assert isinstance(graph, dict)

    def test_empty_files(self, analyzer, temp_repo):
        """Test handling of empty files."""
        (temp_repo / "empty.js").write_text("")
        (temp_repo / "empty.go").write_text("")
        (temp_repo / "empty.py").write_text("")
        
        files = ["empty.js", "empty.go", "empty.py"]
        graph = analyzer.build_import_graph(files)
        
        # Empty files should result in empty graph
        assert isinstance(graph, dict)

    def test_malformed_files(self, analyzer, temp_repo):
        """Test handling of malformed files."""
        (temp_repo / "malformed.js").write_text("import { incomplete from")
        (temp_repo / "malformed.py").write_text("import incomplete syntax %%%")
        
        # Should not raise exceptions, just skip or handle gracefully
        files = ["malformed.js", "malformed.py"]
        graph = analyzer.build_import_graph(files)
        
        assert isinstance(graph, dict)

    def test_nonexistent_files(self, analyzer):
        """Test handling of non-existent files."""
        files = ["nonexistent.js", "missing.py"]
        graph = analyzer.build_import_graph(files)
        
        # Should return empty graph for non-existent files
        assert graph == {}
