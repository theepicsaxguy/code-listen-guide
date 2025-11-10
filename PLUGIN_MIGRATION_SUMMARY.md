# Plugin Migration Summary

This document summarizes the service-to-plugin conversion completed on 2025-11-10.

## Overview

Converted pure utility services into reusable plugins registered in the `tools_registry` database table. This allows these functions to be used by both workflow steps and agents.

## Completed Conversions

### 1. Repository Parsing Plugin

**Location:** `backend/plugins/repository_parser.py`

**Functions:**
- `parse_repository(path)` - Parse repository using chonkie pipeline
- `parse_repository_with_filters(path, include_patterns, exclude_patterns)` - Parse with custom filters

**Database Registration:**
- Updated existing `parse_repository` tool to point to new plugin location
- Migration: `036662099090_update_parse_repository_tool_to_plugin.py`

### 2. Code Structure Analysis Plugin

**Location:** `backend/plugins/code_structure.py`

**Functions:**
- `analyze_code_structure(file_path, content)` - Analyze code using tree-sitter for metadata extraction
- `analyze_code_file_by_language(file_path, language, content)` - Analyze with explicit language
- `detect_file_language(file_path)` - Detect programming language from file

**Database Registration:**
- Added `analyze_code_structure` tool
- Added `detect_file_language` tool
- Migration: `03e771c8c198_add_code_structure_analysis_tools.py`

### 3. Dependency Analysis Plugin

**Location:** `backend/plugins/dependency_graph.py`

**Functions:**
- `analyze_dependencies(repo_root, files, primary_language)` - Build import/dependency graph
- `cluster_dependencies(repo_root, files, primary_language)` - Cluster files by dependencies
- `identify_architectural_layers(repo_root, files, primary_language)` - Identify architectural layers
- `build_python_import_graph(repo_root, files)` - Python-specific import graph

**Database Registration:**
- Added `analyze_dependencies` tool
- Added `cluster_dependencies` tool
- Added `identify_architectural_layers` tool
- Migration: `5af54534a844_add_dependency_analysis_tools.py`

## Deleted Services

- `backend/services/audio_synthesizer.py` - Deprecated service with NotImplementedError methods

## Services Remaining as Services

The following services were correctly kept as services (not converted to plugins):

### Agent Wrappers (LLM-based orchestration)
- `outline_generator.py` - Agent for generating episode outlines
- `script_generator.py` - Agent for generating scripts
- `post_processor.py` - Agent for post-processing
- `episode_planner.py` - Agent for planning episodes

### Infrastructure Services
- `repository_analyzer.py` - High-level repository analysis orchestrator
- `github_service.py` - GitHub API integration
- `storage.py` - S3/object storage service
- `payment.py` - Payment processing
- `webauthn_service.py` - WebAuthn authentication
- `code_context_retriever.py` - Context retrieval service

## Plugin Architecture Benefits

1. **Reusability:** Plugins can be used by any workflow step or agent
2. **Database-driven:** Plugins are registered in `tools_registry` with metadata
3. **Versioning:** Semantic versioning support for plugin evolution
4. **Discovery:** Agents can dynamically discover available plugins
5. **Type Safety:** Input/output schemas defined in database
6. **Cost Tracking:** Cost profiles for each plugin call

## Usage Examples

### In Workflow Steps

Workflow steps can now reference plugins directly:

```python
# In workflow_steps table
step = WorkflowStep(
    plugin_id=<parse_repository_plugin_id>,
    config={
        "path": "/path/to/repo"
    }
)
```

### In Agent Tools

Agents can load plugins dynamically:

```python
# Load plugin from registry
plugin_record = db.query(ToolRegistry).filter(
    ToolRegistry.name == "analyze_code_structure"
).first()

# Import and execute
module = importlib.import_module(plugin_record.module_path)
plugin_fn = getattr(module, plugin_record.function_name)
result = plugin_fn(file_path="/path/to/file.py")
```

## Testing

All plugins can be tested through:
1. **Agent Test UI:** `src/pages/admin/AgentTest.tsx` - Test agents that use these plugins
2. **Workflow Test UI:** Same page - Test workflows with plugin steps
3. **Direct API calls:** Call plugin endpoints directly via `/api/v1/parse/repository` etc.

## Database Migrations Applied

1. `036662099090_update_parse_repository_tool_to_plugin.py`
2. `03e771c8c198_add_code_structure_analysis_tools.py`
3. `5af54534a844_add_dependency_analysis_tools.py`

All migrations have been applied to the development database.

## Next Steps (Future Work)

The following services were identified as candidates for plugin conversion but not completed in this phase:

### Medium Priority
- `dual_voice_synthesizer.py` - TTS synthesis (pure function, stateless)
- `token_estimator.py` - Token counting utility
- `dialogue_parser.py` - Dialogue format parsing

These can be converted using the same pattern:
1. Create plugin wrapper in `backend/plugins/`
2. Create migration to register in `tools_registry`
3. Apply migration
4. Update any workflow steps to use plugin

## Files Modified

### Created
- `backend/plugins/__init__.py`
- `backend/plugins/repository_parser.py`
- `backend/plugins/code_structure.py`
- `backend/plugins/dependency_graph.py`
- `backend/db/migrations/versions/036662099090_update_parse_repository_tool_to_plugin.py`
- `backend/db/migrations/versions/03e771c8c198_add_code_structure_analysis_tools.py`
- `backend/db/migrations/versions/5af54534a844_add_dependency_analysis_tools.py`

### Deleted
- `backend/services/audio_synthesizer.py`

### Database Changes
- Updated 1 existing tool in `tools_registry` (parse_repository)
- Added 5 new tools in `tools_registry`:
  - analyze_code_structure
  - detect_file_language
  - analyze_dependencies
  - cluster_dependencies
  - identify_architectural_layers

## Conclusion

Successfully converted 3 utility services into 8 reusable plugins. These plugins are now available for use in workflows and by agents, providing a more flexible and maintainable architecture.
