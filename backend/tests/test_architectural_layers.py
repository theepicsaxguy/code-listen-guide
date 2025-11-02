"""Tests for architectural layer detection in DependencyAnalyzer."""

import pytest
from backend.services.dependency_analyzer import DependencyAnalyzer, ClusterPlan


def test_identify_architectural_layers_api():
    """Test API layer detection."""
    clusters = [
        ClusterPlan(files={"api/routes.py", "api/controllers.py"}, index=1),
        ClusterPlan(files={"views/user.py", "handlers/auth.py"}, index=2),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["API"]) == 2
    assert layers["API"][0].architectural_layer == "API"
    assert layers["API"][1].architectural_layer == "API"


def test_identify_architectural_layers_business():
    """Test Business Logic layer detection."""
    clusters = [
        ClusterPlan(files={"services/user_service.py", "services/auth_service.py"}, index=1),
        ClusterPlan(files={"domain/models.py", "core/business.py"}, index=2),
        ClusterPlan(files={"use_cases/create_user.py", "usecases/login.py"}, index=3),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["Business Logic"]) == 3
    for cluster in layers["Business Logic"]:
        assert cluster.architectural_layer == "Business Logic"


def test_identify_architectural_layers_data():
    """Test Data Access layer detection."""
    clusters = [
        ClusterPlan(files={"models/user.py", "models/auth.py"}, index=1),
        ClusterPlan(files={"db/connection.py", "database/migrations.py"}, index=2),
        ClusterPlan(files={"repositories/user_repo.py", "dao/auth_dao.py"}, index=3),
        ClusterPlan(files={"entities/user.py", "schemas/user.py"}, index=4),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["Data Access"]) == 4
    for cluster in layers["Data Access"]:
        assert cluster.architectural_layer == "Data Access"


def test_identify_architectural_layers_infrastructure():
    """Test Infrastructure layer detection."""
    clusters = [
        ClusterPlan(files={"utils/helpers.py", "utils/validators.py"}, index=1),
        ClusterPlan(files={"common/constants.py", "shared/types.py"}, index=2),
        ClusterPlan(files={"lib/logger.py", "infrastructure/cache.py"}, index=3),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["Infrastructure"]) == 3
    for cluster in layers["Infrastructure"]:
        assert cluster.architectural_layer == "Infrastructure"


def test_identify_architectural_layers_configuration():
    """Test Configuration layer detection."""
    clusters = [
        ClusterPlan(files={"config/settings.py", "config/database.py"}, index=1),
        ClusterPlan(files={"settings/prod.py", "env/local.py"}, index=2),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["Configuration"]) == 2
    for cluster in layers["Configuration"]:
        assert cluster.architectural_layer == "Configuration"


def test_identify_architectural_layers_testing():
    """Test Testing layer detection."""
    clusters = [
        ClusterPlan(files={"tests/test_user.py", "tests/test_auth.py"}, index=1),
        ClusterPlan(files={"test/integration.py", "__tests__/unit.py"}, index=2),
        ClusterPlan(files={"spec/user.spec.py", "services/auth.test.py"}, index=3),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["Testing"]) == 3
    for cluster in layers["Testing"]:
        assert cluster.architectural_layer == "Testing"


def test_identify_architectural_layers_uncategorized():
    """Test Uncategorized layer for unmatched files."""
    clusters = [
        ClusterPlan(files={"random/file.py", "other/module.py"}, index=1),
        ClusterPlan(files={"src/main.py", "app.py"}, index=2),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["Uncategorized"]) == 2
    for cluster in layers["Uncategorized"]:
        assert cluster.architectural_layer == "Uncategorized"


def test_identify_architectural_layers_priority():
    """Test that higher priority layers win when files match multiple patterns."""
    # Cluster with files from multiple layers - API should win (highest priority)
    clusters = [
        ClusterPlan(
            files={
                "api/routes.py",       # API (priority 5)
                "services/user.py",    # Business Logic (priority 4)
                "utils/helpers.py"     # Infrastructure (priority 0)
            },
            index=1
        ),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    # API has highest priority, so cluster should be categorized as API
    assert len(layers["API"]) == 1
    assert layers["API"][0].architectural_layer == "API"
    assert len(layers["Business Logic"]) == 0
    assert len(layers["Infrastructure"]) == 0


def test_identify_architectural_layers_windows_paths():
    """Test that Windows-style paths are handled correctly."""
    clusters = [
        ClusterPlan(files={"api\\routes.py", "services\\user_service.py"}, index=1),
        ClusterPlan(files={"models\\user.py", "db\\connection.py"}, index=2),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    # First cluster: services wins over api due to priority
    # Actually, API should win (priority 5 > 4)
    assert len(layers["API"]) == 1
    assert len(layers["Data Access"]) == 1


def test_identify_architectural_layers_all_layers():
    """Test that all layer types are represented in the result dict."""
    clusters = []
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    # Even with no clusters, all layer keys should exist
    assert "API" in layers
    assert "Business Logic" in layers
    assert "Data Access" in layers
    assert "Infrastructure" in layers
    assert "Configuration" in layers
    assert "Testing" in layers
    assert "Uncategorized" in layers
    
    # All should be empty lists
    for layer_name, cluster_list in layers.items():
        assert cluster_list == []


def test_identify_architectural_layers_test_file_extensions():
    """Test detection of .test. and .spec. file extensions."""
    clusters = [
        ClusterPlan(files={"user.test.js", "auth.spec.ts", "module.test.py"}, index=1),
    ]
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert len(layers["Testing"]) == 1
    assert layers["Testing"][0].architectural_layer == "Testing"


def test_identify_architectural_layers_empty_input():
    """Test with empty cluster list."""
    clusters = []
    
    analyzer = DependencyAnalyzer("/tmp/test_repo")
    layers = analyzer.identify_architectural_layers(clusters)
    
    assert isinstance(layers, dict)
    assert all(len(v) == 0 for v in layers.values())
