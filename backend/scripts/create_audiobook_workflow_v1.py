#!/usr/bin/env python3
"""
Create the default audiobook_generation workflow definition and first revision.

This script creates:
1. A workflow_definitions record for "audiobook_generation"
2. A workflow_revisions record (version 1) with all workflow steps
3. workflow_steps records for each stage of the audiobook generation process

Usage:
    python -m backend.scripts.create_audiobook_workflow_v1
"""

import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from backend.db.session import SessionLocal
from backend.models.workflow_definition import WorkflowDefinition
from backend.models.workflow_revision import WorkflowRevision
from backend.models.workflow_step import WorkflowStep
from backend.models.agent_registry import AgentRegistry


def create_audiobook_workflow(db: Session):
    """Create the audiobook_generation workflow definition and first revision."""
    
    # Check if workflow already exists
    existing = db.query(WorkflowDefinition).filter(
        WorkflowDefinition.name == "audiobook_generation"
    ).first()
    
    if existing:
        print("✓ Workflow 'audiobook_generation' already exists")
        return existing
    
    # Get agent IDs from registry
    agents = {
        "analyzer": db.query(AgentRegistry).filter(AgentRegistry.name == "analyzer_agent").first(),
        "outline": db.query(AgentRegistry).filter(AgentRegistry.name == "outline_agent").first(),
        "script": db.query(AgentRegistry).filter(AgentRegistry.name == "script_agent").first(),
        "audio": db.query(AgentRegistry).filter(AgentRegistry.name == "audio_agent").first(),
        "postprocess": db.query(AgentRegistry).filter(AgentRegistry.name == "postprocess_agent").first(),
    }
    
    # Verify all agents exist
    for agent_name, agent in agents.items():
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in registry. Run seed_workflow_registry.py first.")
    
    print("✓ All required agents found in registry")
    
    # Create workflow definition
    workflow_def = WorkflowDefinition(
        name="audiobook_generation",
        description="Complete audiobook generation workflow: analysis → outline → approval → scripting → audio → post-processing",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(workflow_def)
    db.flush()  # Get ID without committing
    
    print(f"✓ Created workflow definition: {workflow_def.name} (ID: {workflow_def.id})")
    
    # Create first revision
    revision = WorkflowRevision(
        workflow_definition_id=workflow_def.id,
        version=1,
        is_published=True,
        revision_metadata={
            "author": "system",
            "notes": "Initial hardcoded workflow converted to DB-driven format",
            "changelog": "Created from backend/workflows/audiobook_workflow.py"
        },
        created_at=datetime.utcnow(),
        published_at=datetime.utcnow()
    )
    db.add(revision)
    db.flush()
    
    print(f"✓ Created revision v{revision.version} (ID: {revision.id})")
    
    # Define workflow steps
    steps = [
        {
            "step_order": 0,
            "step_name": "analysis",
            "agent_id": agents["analyzer"].id,
            "execution_mode": "sequential",
            "input_mapping": {
                "repo_url": "${job.repo_url}",
                "git_ref": "${job.git_ref}"
            },
            "output_mapping": {
                "analysis_result": "${step.output}"
            },
            "checkpoint_enabled": True,
            "retry_policy": {
                "max_retries": 2,
                "backoff": "exponential"
            },
            "step_config": {}
        },
        {
            "step_order": 1,
            "step_name": "outline",
            "agent_id": agents["outline"].id,
            "execution_mode": "sequential",
            "input_mapping": {
                "analysis_data": "${steps.analysis.output}",
                "depth_tier": "${job.depth_tier}"
            },
            "output_mapping": {
                "outline_data": "${step.output}"
            },
            "checkpoint_enabled": True,
            "retry_policy": {
                "max_retries": 2,
                "backoff": "exponential"
            },
            "step_config": {}
        },
        {
            "step_order": 2,
            "step_name": "approval",
            "agent_id": None,  # Human-in-the-loop step
            "execution_mode": "conditional",
            "input_mapping": {
                "outline": "${steps.outline.output}"
            },
            "output_mapping": {
                "approved_outline": "${step.output}"
            },
            "checkpoint_enabled": True,
            "retry_policy": None,
            "step_config": {
                "pause_for_user": True,
                "transition_on_approval": "scripting",
                "transition_on_rejection": "outline"
            }
        },
        {
            "step_order": 3,
            "step_name": "scripting",
            "agent_id": agents["script"].id,
            "execution_mode": "concurrent",
            "input_mapping": {
                "chapters": "${steps.approval.output.chapters}",
                "analysis": "${steps.analysis.output}"
            },
            "output_mapping": {
                "scripts": "${step.output}"
            },
            "checkpoint_enabled": True,
            "retry_policy": {
                "max_retries": 1,
                "backoff": "linear"
            },
            "step_config": {
                "concurrency_mode": "per_chapter",
                "max_concurrent": 5
            }
        },
        {
            "step_order": 4,
            "step_name": "audio",
            "agent_id": agents["audio"].id,
            "execution_mode": "concurrent",
            "input_mapping": {
                "chapters": "${steps.approval.output.chapters}",
                "scripts": "${steps.scripting.output}"
            },
            "output_mapping": {
                "audio_files": "${step.output}"
            },
            "checkpoint_enabled": True,
            "retry_policy": {
                "max_retries": 2,
                "backoff": "exponential"
            },
            "step_config": {
                "concurrency_mode": "batch",
                "batch_size": 5
            }
        },
        {
            "step_order": 5,
            "step_name": "post_processing",
            "agent_id": agents["postprocess"].id,
            "execution_mode": "sequential",
            "input_mapping": {
                "audio_files": "${steps.audio.output}",
                "metadata": {
                    "title": "${job.repo_name}",
                    "chapters": "${steps.approval.output.chapters}"
                }
            },
            "output_mapping": {
                "deliverables": "${step.output}"
            },
            "checkpoint_enabled": True,
            "retry_policy": {
                "max_retries": 2,
                "backoff": "exponential"
            },
            "step_config": {}
        }
    ]
    
    # Create workflow steps
    for step_data in steps:
        step = WorkflowStep(
            revision_id=revision.id,
            **step_data
        )
        db.add(step)
        print(f"  ✓ Created step {step_data['step_order']}: {step_data['step_name']}")
    
    # Update workflow definition to point to current revision
    workflow_def.current_revision_id = revision.id
    
    db.commit()
    
    print(f"\n✓ Workflow created and published successfully!")
    print(f"  - Workflow ID: {workflow_def.id}")
    print(f"  - Current Revision: v{revision.version}")
    print(f"  - Total Steps: {len(steps)}")
    
    return workflow_def


def main():
    """Main function."""
    print("=" * 60)
    print("Creating Audiobook Generation Workflow v1")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        workflow = create_audiobook_workflow(db)
        
        print()
        print("=" * 60)
        print("✓ Workflow setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Verify workflow in database:")
        print("   SELECT * FROM workflow_definitions;")
        print("   SELECT * FROM workflow_revisions;")
        print("   SELECT * FROM workflow_steps ORDER BY step_order;")
        print()
        print("2. Test workflow loading:")
        print("   python -m backend.workflows.dynamic_loader")
        print()
    except Exception as e:
        print(f"\n✗ Error during workflow creation: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
