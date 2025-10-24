"""
Outline generation service using Claude API.

TODO: Implementation steps:
1. Initialize Anthropic client
2. Implement generate_outline() with Claude prompt
3. Add depth-specific instructions
4. Parse JSON response from Claude
5. Validate outline structure
6. Calculate duration estimates
7. Add error handling and retries
8. Track API costs
"""

from anthropic import Anthropic
import json
from typing import Dict, List

# from backend.config import get_settings


class OutlineGenerator:
    """
    Generates chapter outlines using Claude AI.

    TODO:
    - Implement Claude API integration
    - Create optimal prompts for different depth tiers
    - Add response validation
    - Implement cost tracking
    """

    def __init__(self, anthropic_api_key: str):
        """
        Initialize outline generator.

        TODO:
        - Initialize Anthropic client
        - Set up prompt templates
        """
        self.client = Anthropic(api_key=anthropic_api_key)

    async def generate_outline(
        self,
        repo_analysis: Dict,
        parsed_codebase: Dict,
        depth_tier: str
    ) -> Dict:
        """
        Generate chapter outline using Claude.

        Args:
            repo_analysis: Repository metadata from RepositoryAnalyzer
            parsed_codebase: Parsed code symbols from RepositoryAnalyzer
            depth_tier: One of 'survey', 'standard', 'comprehensive'

        Returns:
            Dictionary with:
            - chapters: List of chapter objects
            - total_estimated_duration_minutes: Total duration
            - total_chapters: Chapter count

        TODO:
        1. Build prompt with repo analysis and depth instructions
        2. Call Claude API
        3. Parse JSON response
        4. Validate outline structure
        5. Calculate total duration
        6. Return outline data
        """

        depth_instructions = {
            "survey": "Focus on high-level architecture, public APIs, and key algorithms. Aim for 10-15 chapters.",
            "standard": "Cover all public interfaces, important private functions, and design patterns. Aim for 25-35 chapters.",
            "comprehensive": "Explain every class, function, and implementation detail. Aim for 40-60 chapters."
        }

        # TODO: Build comprehensive prompt
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

        # TODO: Call Claude API
        # response = self.client.messages.create(
        #     model="claude-sonnet-4-20250514",
        #     max_tokens=8000,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        #
        # outline_text = response.content[0].text
        # outline = json.loads(outline_text)
        #
        # return outline

        # TODO: Implement
        pass

    def _validate_outline(self, outline: Dict) -> bool:
        """
        Validate outline structure.

        TODO:
        - Check required fields
        - Validate chapter numbers are sequential
        - Ensure reasonable duration estimates
        """
        pass
