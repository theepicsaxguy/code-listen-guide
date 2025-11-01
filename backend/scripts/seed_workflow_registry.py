#!/usr/bin/env python3
"""
Seed script to populate agents_registry and tools_registry with existing agents and tools.

This script inspects the backend/agents and backend/tools directories and creates
registry entries for all discovered agents and tools.

Usage:
    python backend/scripts/seed_workflow_registry.py
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from backend.db.session import SessionLocal
from backend.models.agent_registry import AgentRegistry
from backend.models.tool_registry import ToolRegistry


def seed_agents(db: Session):
    """Seed agents_registry with existing agents."""
    
    agents = [
        {
            "name": "analyzer_agent",
            "module_path": "backend.agents.analyzer_agent",
            "factory_function": "analyzer_agent",
            "description": "Repository analyzer agent that clones repos and parses code structure using chonkie pipeline",
            "config_schema": {
                "type": "object",
                "properties": {
                    "settings": {"type": "object", "description": "Application settings"}
                }
            },
            "tools": ["_ai_clone_repo", "_ai_list_files", "_ai_parse_repository"]
        },
        {
            "name": "outline_agent",
            "module_path": "backend.agents.outline_agent",
            "factory_function": "outline_agent",
            "description": "Outline generator agent that creates chapter structure from repository analysis",
            "config_schema": {
                "type": "object",
                "properties": {
                    "settings": {"type": "object", "description": "Application settings"}
                }
            },
            "tools": []
        },
        {
            "name": "script_agent",
            "module_path": "backend.agents.script_agent",
            "factory_function": "script_agent",
            "description": "Script writer agent that generates narration scripts for chapters",
            "config_schema": {
                "type": "object",
                "properties": {
                    "settings": {"type": "object", "description": "Application settings"},
                    "chapter_ctx": {"type": "object", "description": "Chapter context with outline data"}
                }
            },
            "tools": ["_ai_save_script"]
        },
        {
            "name": "audio_agent",
            "module_path": "backend.agents.audio_agent",
            "factory_function": "audio_agent",
            "description": "Audio producer agent that synthesizes speech from scripts and uploads to S3",
            "config_schema": {
                "type": "object",
                "properties": {
                    "settings": {"type": "object", "description": "Application settings"}
                }
            },
            "tools": ["_ai_tts", "_ai_upload"]
        },
        {
            "name": "postprocess_agent",
            "module_path": "backend.agents.postprocess_agent",
            "factory_function": "postprocess_agent",
            "description": "Post-processing agent that concatenates audio files and uploads deliverables to S3",
            "config_schema": {
                "type": "object",
                "properties": {
                    "settings": {"type": "object", "description": "Application settings"}
                }
            },
            "tools": ["_ai_concat", "_ai_upload"]
        }
    ]
    
    for agent_data in agents:
        # Check if agent already exists
        existing = db.query(AgentRegistry).filter(AgentRegistry.name == agent_data["name"]).first()
        if existing:
            print(f"✓ Agent '{agent_data['name']}' already exists, skipping")
            continue
        
        agent = AgentRegistry(
            name=agent_data["name"],
            module_path=agent_data["module_path"],
            factory_function=agent_data["factory_function"],
            description=agent_data["description"],
            config_schema=agent_data["config_schema"],
            tools=agent_data["tools"],
            account_acl=agent_data.get("account_acl", []),
            quota_limits=agent_data.get("quota_limits", []),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(agent)
        print(f"✓ Created agent: {agent_data['name']}")
    
    db.commit()
    print(f"\n✓ Seeded {len(agents)} agents successfully")


def seed_tools(db: Session):
    """Seed tools_registry with existing tools."""
    
    tools = [
        {
            "name": "clone_repository",
            "module_path": "backend.tools.git_tools",
            "function_name": "_ai_clone_repo",
            "description": "Clone a GitHub repository to a temporary directory",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string", "description": "GitHub repository URL"},
                    "git_ref": {"type": "string", "description": "Branch, tag, or commit hash"}
                },
                "required": ["repo_url"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string"},
                    "commit_hash": {"type": "string"},
                    "files_count": {"type": "integer"}
                }
            }
        },
        {
            "name": "list_files",
            "module_path": "backend.tools.git_tools",
            "function_name": "_ai_list_files",
            "description": "List files in a cloned repository directory",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to repository"}
                },
                "required": ["repo_path"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "files": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        {
            "name": "parse_repository",
            "module_path": "backend.tools.code_parser_tools",
            "function_name": "_ai_parse_repository",
            "description": "Parse repository structure using chonkie pipeline",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"}
                },
                "required": ["repo_path"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "analysis": {"type": "object"}
                }
            }
        },
        {
            "name": "save_chapter_script",
            "module_path": "backend.tools.script_tools",
            "function_name": "_ai_save_script",
            "description": "Save generated script to database for a chapter",
            "input_schema": {
                "type": "object",
                "properties": {
                    "chapter_id": {"type": "string"},
                    "script_text": {"type": "string"}
                },
                "required": ["chapter_id", "script_text"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"}
                }
            }
        },
        {
            "name": "synthesize_speech",
            "module_path": "backend.tools.audio_tools",
            "function_name": "_ai_tts",
            "description": "Convert text to speech using OpenAI TTS API",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "voice": {"type": "string"}
                },
                "required": ["text"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "audio_file": {"type": "string"}
                }
            }
        },
        {
            "name": "upload_to_s3",
            "module_path": "backend.tools.audio_tools",
            "function_name": "_ai_upload",
            "description": "Upload audio file to AWS S3",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "s3_key": {"type": "string"}
                },
                "required": ["file_path", "s3_key"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                }
            }
        },
        {
            "name": "concatenate_audio",
            "module_path": "backend.tools.audio_tools",
            "function_name": "_ai_concat",
            "description": "Concatenate multiple audio files with chapter markers",
            "input_schema": {
                "type": "object",
                "properties": {
                    "audio_files": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["audio_files"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "output_file": {"type": "string"}
                }
            }
        }
    ]
    
    for tool_data in tools:
        # Check if tool already exists
        existing = db.query(ToolRegistry).filter(ToolRegistry.name == tool_data["name"]).first()
        if existing:
            print(f"✓ Tool '{tool_data['name']}' already exists, skipping")
            continue
        
        tool = ToolRegistry(
            name=tool_data["name"],
            module_path=tool_data["module_path"],
            function_name=tool_data["function_name"],
            description=tool_data["description"],
            input_schema=tool_data["input_schema"],
            output_schema=tool_data["output_schema"],
            created_at=datetime.utcnow()
        )
        db.add(tool)
        print(f"✓ Created tool: {tool_data['name']}")
    
    db.commit()
    print(f"\n✓ Seeded {len(tools)} tools successfully")


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Seeding Workflow Registry")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        print("\n1. Seeding agents_registry...")
        seed_agents(db)
        
        print("\n2. Seeding tools_registry...")
        seed_tools(db)
        
        print("\n" + "=" * 60)
        print("✓ Registry seeding completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
