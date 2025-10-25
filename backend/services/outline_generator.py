"""
Outline generation service using Claude API.

DEPRECATED: This service is deprecated in favor of the Microsoft Agent Framework.
Use backend/agents/outline_agent.py instead.

This file is kept for reference but should not be used in new code.
"""

from anthropic import Anthropic
import json
from typing import Dict, List

# from backend.config import get_settings


class OutlineGenerator:
    """
    Generates chapter outlines using Claude AI.

    DEPRECATED: Use backend/agents/outline_agent.py instead.
    """

    def __init__(self, anthropic_api_key: str):
        """Initialize outline generator (deprecated)."""
        self.client = Anthropic(api_key=anthropic_api_key)

    async def generate_outline(
        self,
        repo_analysis: Dict,
        parsed_codebase: Dict,
        depth_tier: str
    ) -> Dict:
        """
        Generate chapter outline using Claude (deprecated).

        Use backend/agents/outline_agent.py instead.
        """

        depth_instructions = {
            "survey": "Focus on high-level architecture, public APIs, and key algorithms. Aim for 10-15 chapters.",
            "standard": "Cover all public interfaces, important private functions, and design patterns. Aim for 25-35 chapters.",
            "comprehensive": "Explain every class, function, and implementation detail. Aim for 40-60 chapters."
        }

        prompt = f"""
You are an expert technical writer creating an audiobook outline for a codebase.

Repository: {repo_analysis.get('repo_name', 'Unknown')}
Languages: {', '.join(repo_analysis.get('languages', {}).keys())}
File count: {repo_analysis.get('file_count', 0)}
Depth: {depth_tier}

{depth_instructions[depth_tier]}

Based on this codebase analysis:
{json.dumps(repo_analysis, indent=2)[:2000]}

Create a chapter outline where each chapter:
1. Has a clear title and scope
2. Groups related functionality logically
3. Follows a narrative arc (high-level → detailed)
4. Has estimated duration of 10-25 minutes
5. Lists specific files/classes/functions covered
6. Includes learning objectives

Return ONLY valid JSON in this format:
{{
  "chapters": [
    {{
      "number": 1,
      "title": "Introduction and Architecture Overview",
      "description": "High-level system architecture and core concepts",
      "estimated_duration_minutes": 12,
      "files_covered": ["src/index.ts", "src/app.ts"],
      "topics": ["Project structure", "Entry points", "Core patterns"],
      "learning_objectives": ["Understand overall architecture", "Identify main components"]
    }}
  ],
  "total_estimated_duration_minutes": 480,
  "total_chapters": 35
}}
"""
        # Deprecated: Use backend/agents/outline_agent.py instead
        raise NotImplementedError("Use backend/agents/outline_agent.py instead")

    def _validate_outline(self, outline: Dict) -> bool:
        """Validate outline structure (deprecated)."""
        raise NotImplementedError("Use backend/agents/outline_agent.py instead")
