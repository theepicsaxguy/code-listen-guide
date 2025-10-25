"""
Script generation service using Claude API.

DEPRECATED: This service is deprecated in favor of the Microsoft Agent Framework.
Use backend/agents/script_agent.py instead.

This file is kept for reference but should not be used in new code.
"""

from anthropic import Anthropic
from typing import Dict, Optional


class ScriptGenerator:
    """
    Generates narration scripts for audiobook chapters using Claude.

    DEPRECATED: Use backend/agents/script_agent.py instead.
    """

    def __init__(self, anthropic_api_key: str):
        """Initialize script generator (deprecated)."""
        self.client = Anthropic(api_key=anthropic_api_key)

    async def generate_chapter_script(
        self,
        chapter: Dict,
        codebase_context: Dict,
        previous_chapters_summary: str = ""
    ) -> str:
        """Generate narration script (deprecated). Use backend/agents/script_agent.py instead."""
        raise NotImplementedError("Use backend/agents/script_agent.py instead")

    def _get_relevant_code_context(self, chapter: Dict, codebase_context: Dict) -> str:
        """Extract code context (deprecated)."""
        raise NotImplementedError("Use backend/agents/script_agent.py instead")

    def _post_process_script(self, script: str) -> str:
        """Clean up script (deprecated)."""
        raise NotImplementedError("Use backend/agents/script_agent.py instead")
