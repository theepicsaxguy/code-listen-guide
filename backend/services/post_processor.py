"""
Post-processing service for creating final deliverables.

DEPRECATED: This service is deprecated in favor of the Microsoft Agent Framework.
Use backend/agents/postprocess_agent.py instead.

This file is kept for reference but should not be used in new code.
"""

import subprocess
from pathlib import Path
import json
from typing import List, Dict


class PostProcessor:
    """
    Post-processes generated content into final deliverables.

    DEPRECATED: Use backend/agents/postprocess_agent.py instead.
    """

    async def create_full_audiobook(
        self,
        chapter_audio_files: List[Path],
        output_path: Path
    ) -> Path:
        """Combine audio files (deprecated). Use backend/agents/postprocess_agent.py instead."""
        raise NotImplementedError("Use backend/agents/postprocess_agent.py instead")

    async def embed_chapter_markers(
        self,
        audiobook_path: Path,
        chapters: List[Dict]
    ):
        """Embed chapter markers (deprecated)."""
        raise NotImplementedError("Use backend/agents/postprocess_agent.py instead")

    async def generate_cover_image(
        self,
        repo_name: str,
        primary_language: str,
        output_path: Path
    ) -> Path:
        """Generate cover image (deprecated)."""
        raise NotImplementedError("Use backend/agents/postprocess_agent.py instead")

    async def create_metadata_json(
        self,
        job: Dict,
        chapters: List[Dict],
        output_path: Path
    ) -> Path:
        """Create metadata (deprecated)."""
        raise NotImplementedError("Use backend/agents/postprocess_agent.py instead")

    async def create_scripts_zip(
        self,
        scripts: List[Dict],
        output_path: Path
    ) -> Path:
        """Create scripts ZIP (deprecated)."""
        raise NotImplementedError("Use backend/agents/postprocess_agent.py instead")
