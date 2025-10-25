# Backend Tests

Comprehensive test suite for the Codebase Audiobook backend.

## Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures and configuration
├── test_audiobook_tasks.py  # Existing workflow task tests
├── test_docling_service.py  # Docling pipeline tests
├── test_agents.py           # Microsoft Agent Framework agent tests
├── test_services.py         # Backend service layer tests
├── test_api_routes.py       # FastAPI route tests
├── test_workflows.py        # Workflow orchestration tests
└── test_models.py           # Database model tests
```

## Running Tests

### Run All Tests

```bash
cd /home/runner/work/code-listen-guide/code-listen-guide
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Docling tests
pytest -m docling

# Agent tests
pytest -m agents

# API tests
pytest -m api

# Service tests
pytest -m services

# Workflow tests
pytest -m workflows

# Model tests
pytest -m models
```

### Run Specific Test Files

```bash
# Test Docling service
pytest backend/tests/test_docling_service.py

# Test agents
pytest backend/tests/test_agents.py

# Test API routes
pytest backend/tests/test_api_routes.py

# Test workflows
pytest backend/tests/test_workflows.py

# Test models
pytest backend/tests/test_models.py

# Test services
pytest backend/tests/test_services.py
```

### Run with Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=backend --cov-report=html

# Open coverage report
open coverage_html/index.html
```

### Run Fast Tests Only (skip slow integration tests)

```bash
pytest -m "not slow"
```

## Test Markers

Tests are organized with pytest markers:

- `unit` - Fast unit tests for individual components
- `integration` - Integration tests across multiple components
- `slow` - Tests that take longer to execute
- `docling` - Tests requiring Docling installation
- `agents` - Tests for Microsoft Agent Framework agents
- `api` - API route tests
- `services` - Service layer tests
- `models` - Database model tests
- `workflows` - Workflow orchestration tests
- `requires_env` - Tests requiring environment variables (API keys, etc.)

## Test Coverage

### Docling Pipeline Tests (`test_docling_service.py`)
- ✅ Pipeline initialization
- ✅ Content type detection (code, documentation, configuration)
- ✅ File parsing
- ✅ Content cleaning (whitespace, minification detection)
- ✅ Semantic tagging (language, framework, patterns, complexity)
- ✅ File exclusion/inclusion patterns
- ✅ Entry point identification
- 🔲 Full pipeline integration (requires Docling installation)

### Agent Tests (`test_agents.py`)
- ✅ Analyzer agent creation
- ✅ Outline agent creation
- ✅ Script agent creation
- ✅ Audio agent creation
- ✅ Post-process agent creation
- ✅ Agent configuration verification
- 🔲 Full workflow with real agents (requires agent framework setup)

### Service Tests (`test_services.py`)
- ✅ Repository analyzer initialization
- ✅ Repository cloning
- ✅ Outline generation
- ✅ Script generation
- ✅ Audio synthesis
- ✅ Post-processing
- ✅ S3 storage operations
- ✅ Stripe payment processing
- 🔲 Full integration pipeline (requires external services)

### API Tests (`test_api_routes.py`)
- ✅ Authentication endpoints (register, login, get user)
- ✅ Job CRUD operations
- ✅ Job workflow start/resume
- ✅ Outline generation and approval
- ✅ Payment intent creation
- ✅ Stripe webhook handling
- ✅ Player data retrieval
- ✅ Deliverable downloads
- 🔲 Full lifecycle integration (requires auth implementation)

### Workflow Tests (`test_workflows.py`)
- ✅ Workflow initialization
- ✅ Stage execution order
- ✅ Human approval handling
- ✅ Checkpoint saving and loading
- ✅ Workflow resumption
- ✅ Task start/resume functions
- 🔲 End-to-end workflow with real repository (requires full setup)

### Model Tests (`test_models.py`)
- ✅ User model CRUD
- ✅ Job model and status transitions
- ✅ Chapter model and ordering
- ✅ Outline model and approval
- ✅ Payment model and status tracking
- ✅ Usage log model and cost tracking
- ✅ Workflow checkpoint model
- 🔲 Model relationships (currently commented out in codebase)

## CI/CD Integration

These tests are exercised by three GitHub Actions workflows so contributors get the same signal locally and in CI.

### CI (`.github/workflows/ci.yml`)
- Frontend job builds the Vite app with Node.js 22 so regressions in the UI surface early.
- Backend job installs ffmpeg, restores Python dependencies from `backend/requirements.txt`, and runs the marker suites on Python 3.12 before generating a coverage report that uploads to Codecov when credentials exist.

### Integration Tests (`.github/workflows/integration-tests.yml`)
- Manual dispatches and the nightly schedule light up the slow `integration` + `slow` suite with the required API keys.
- Failures create a GitHub issue automatically so the team can follow up without combing through job logs.

### Code Quality (`.github/workflows/code-quality.yml`)
- Black, Flake8, and MyPy run on Python 3.12 with pip caching to keep lint feedback fast.
- MyPy is advisory via `continue-on-error` so strict typing gaps show up without blocking urgent hotfixes.

## Environment Variables for Tests

Some tests require environment variables. Create a `.env.test` file:

```bash
# Testing environment variables
DATABASE_URL=sqlite:///:memory:
ANTHROPIC_API_KEY=test-key
AZURE_OPENAI_API_KEY=test-key
STRIPE_SECRET_KEY=sk_test_...
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

## Debugging Tests

### Run with verbose output
```bash
pytest -vv
```

### Run with print statements visible
```bash
pytest -s
```

### Run specific test
```bash
pytest backend/tests/test_models.py::TestUserModel::test_create_user
```

### Run with pdb debugger on failure
```bash
pytest --pdb
```

## Adding New Tests

1. Create test file in `backend/tests/`
2. Use descriptive test names: `test_<what_is_being_tested>`
3. Add appropriate markers
4. Use fixtures from `conftest.py`
5. Mock external services
6. Test both success and failure cases

Example:

```python
import pytest
from unittest.mock import MagicMock

@pytest.mark.unit
@pytest.mark.services
def test_my_new_feature(mock_client):
    """Test description."""
    from backend.services.my_service import my_function

    result = my_function(param="test")

    assert result is not None
    assert result.status == "success"
```

## Known Limitations

1. **Docling Tests**: Some tests require Docling installation and are marked with `@pytest.mark.skip`
2. **Agent Integration**: Full agent workflow tests require Microsoft Agent Framework setup
3. **External Services**: Tests requiring real API keys are mocked by default
4. **Model Relationships**: Some relationship tests are skipped because relationships are commented out in models

## Future Improvements

- [ ] Add performance benchmarks
- [ ] Add load testing for API endpoints
- [ ] Add security testing (SQL injection, XSS, etc.)
- [ ] Add contract testing for external services
- [ ] Add mutation testing
- [ ] Add visual regression testing for documentation
- [ ] Increase coverage to 90%+
