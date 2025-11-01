"""SQLAlchemy model for registered tools/plugins available to agents."""

import uuid
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from backend.db.base import Base


class ToolRegistry(Base):
    __tablename__ = "tools_registry"
    __table_args__ = (
        UniqueConstraint("name"),
        UniqueConstraint(
            "module_path",
            "function_name",
            name="uq_tools_registry_module_path_function_name",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    module_path = Column(String(500), nullable=False)
    function_name = Column(String(255), nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    schema_version = Column(Integer, nullable=False, default=1)
    signature_hash = Column(String(128))
    input_schema_hash = Column(String(128))
    output_schema_hash = Column(String(128))
    last_validated_at = Column(DateTime)
    last_validation_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


CORE_TOOL_REGISTRY_SEED_DATA: List[Dict[str, Any]] = [
    {
        "name": "clone_repository",
        "module_path": "backend.agents.analyzer_agent",
        "function_name": "_ai_clone_repo",
        "description": "Clone a Git repository into a temporary sandbox directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Git repository URL",
                }
            },
            "required": ["url"],
        },
        "output_schema": {
            "type": "string",
            "description": "Absolute path to the cloned repository",
        },
        "schema_version": 1,
    },
    {
        "name": "list_repository_files",
        "module_path": "backend.agents.analyzer_agent",
        "function_name": "_ai_list_files",
        "description": "Return relative file paths contained in a cloned repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to cloned repository root",
                }
            },
            "required": ["path"],
        },
        "output_schema": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Relative file paths in the repository",
        },
        "schema_version": 1,
    },
    {
        "name": "parse_repository",
        "module_path": "backend.agents.analyzer_agent",
        "function_name": "_ai_parse_repository",
        "description": "Run the chonkie pipeline to analyse repository structure",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to cloned repository root",
                }
            },
            "required": ["path"],
        },
        "output_schema": {
            "type": "object",
            "description": "Structured repository analysis payload",
        },
        "schema_version": 1,
    },
    {
        "name": "save_chapter_script",
        "module_path": "backend.agents.script_agent",
        "function_name": "_ai_save_script",
        "description": "Persist a generated narration script for a chapter",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Job identifier",
                },
                "chapter_number": {
                    "type": "integer",
                    "description": "Chapter index",
                },
                "script": {
                    "type": "string",
                    "description": "Narration script contents",
                },
            },
            "required": ["job_id", "chapter_number", "script"],
        },
        "output_schema": {
            "type": "boolean",
            "description": "True when the script is stored",
        },
        "schema_version": 1,
    },
    {
        "name": "synthesize_speech",
        "module_path": "backend.agents.audio_agent",
        "function_name": "_ai_tts",
        "description": "Generate speech audio from text using the configured TTS provider",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to render as speech",
                },
                "voice": {
                    "type": "string",
                    "description": "Optional voice selection",
                },
            },
            "required": ["text"],
        },
        "output_schema": {
            "type": "string",
            "description": "Path to the generated audio file",
        },
        "schema_version": 1,
    },
    {
        "name": "audio_upload_to_s3",
        "module_path": "backend.agents.audio_agent",
        "function_name": "_ai_upload",
        "description": "Upload synthesized chapter audio to object storage",
        "input_schema": {
            "type": "object",
            "properties": {
                "local_path": {
                    "type": "string",
                    "description": "Local file path to upload",
                },
                "s3_key": {
                    "type": "string",
                    "description": "Destination object key",
                },
            },
            "required": ["local_path", "s3_key"],
        },
        "output_schema": {
            "type": "string",
            "description": "Public URL of the uploaded object",
        },
        "schema_version": 1,
    },
    {
        "name": "concat_audio",
        "module_path": "backend.agents.postprocess_agent",
        "function_name": "_ai_concat",
        "description": "Merge chapter audio tracks into a single audiobook file",
        "input_schema": {
            "type": "object",
            "properties": {
                "chapter_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Audio file paths",
                },
                "chapter_titles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Titles aligned to chapter_paths",
                },
            },
            "required": ["chapter_paths", "chapter_titles"],
        },
        "output_schema": {
            "type": "string",
            "description": "Path to the merged audiobook",
        },
        "schema_version": 1,
    },
    {
        "name": "postprocess_upload_to_s3",
        "module_path": "backend.agents.postprocess_agent",
        "function_name": "_ai_upload",
        "description": "Publish merged deliverables to object storage",
        "input_schema": {
            "type": "object",
            "properties": {
                "local_path": {
                    "type": "string",
                    "description": "Local file path to upload",
                },
                "s3_key": {
                    "type": "string",
                    "description": "Destination object key",
                },
            },
            "required": ["local_path", "s3_key"],
        },
        "output_schema": {
            "type": "string",
            "description": "Public URL of the uploaded object",
        },
        "schema_version": 1,
    },
]
