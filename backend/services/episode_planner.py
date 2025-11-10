"""LLM-based episode planning service.

Generates semantic episode metadata (titles, themes, hooks, objectives) from
dependency clusters using Microsoft Agent Framework.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from backend.agents.episode_agent import create_episode_agent
from backend.agents import build_responses_client_options
from backend.config import get_settings
from backend.services.dependency_analyzer import ClusterPlan
from agent_framework.openai import OpenAIResponsesClient

logger = logging.getLogger(__name__)


EPISODE_PLANNING_PROMPT = """You are a technical podcast episode planner. Given a code repository dependency cluster, generate a compelling episode plan.

A cluster is a group of related files that work together. Your job is to:
1. Create an engaging episode title (5-10 words)
2. Define a narrative theme (1-2 sentences explaining the episode's focus)
3. Generate 3-5 conversation hooks (questions or topics that drive dialogue)
4. List 3-5 learning objectives (what listeners will understand)

INPUT:
- Cluster files: {file_list}
- Architectural layer: {architectural_layer}
- Dependency relationships: {dependency_info}
- Repository context: {repo_context}

OUTPUT JSON format:
{{
  "title": "Engaging Episode Title Here",
  "narrative_theme": "This episode explores how [concept] works in the codebase, focusing on [specifics]",
  "conversation_hooks": [
    "Why did the team choose [approach]?",
    "What are the trade-offs between [options]?",
    "How does [component] handle edge cases?"
  ],
  "learning_objectives": [
    "Understand [concept]",
    "Learn [pattern]",
    "Grasp [design decision]"
  ]
}}

Guidelines:
- Titles should be specific and intriguing (not generic like "Episode 1")
- Themes should explain the architectural or design story
- Hooks should prompt natural two-host conversations
- Objectives should be concrete and achievable
- Reference actual file names and concepts when relevant
"""


class EpisodePlanner:
    """Generates semantic episode metadata using Microsoft Agent Framework."""

    def __init__(self) -> None:
        """Initialize planner with agent framework."""
        self.client = None

    async def _get_agent(self):
        """Get or create the episode planning agent."""
        if self.client is None:
            settings = get_settings()
            client = OpenAIResponsesClient(**build_responses_client_options(settings))
            self.client = await create_episode_agent(client)
        return self.client

    async def plan_episode(
        self,
        cluster: ClusterPlan,
        dependency_graph: Dict[str, List[str]],
        architectural_layer: Optional[str],
        repo_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate episode plan from a dependency cluster.

        Args:
            cluster: Dependency cluster with grouped files
            dependency_graph: Full dependency graph for context
            architectural_layer: Detected architectural layer name
            repo_context: Optional repository metadata (name, description, etc.)

        Returns:
            Dictionary with title, narrative_theme, conversation_hooks, learning_objectives
        """
        try:
            agent = await self._get_agent()
            
            # Build input context
            file_list = sorted(cluster.files)
            cluster_deps = self._extract_cluster_dependencies(cluster.files, dependency_graph)
            repo_info = repo_context or {}

            prompt = EPISODE_PLANNING_PROMPT.format(
                file_list=", ".join(file_list[:20]),  # Limit to avoid token bloat
                architectural_layer=architectural_layer or "Uncategorized",
                dependency_info=json.dumps(cluster_deps, indent=2)[:500],
                repo_context=json.dumps(repo_info, indent=2)[:300],
            )

            result = await agent.run(prompt)
            
            # The agent framework should return structured data
            if hasattr(result, 'result') and result.result:
                response_data = result.result
                return {
                    "title": response_data.get("title", self._default_title(cluster)),
                    "narrative_theme": response_data.get("narrative_theme", "Technical deep dive"),
                    "conversation_hooks": response_data.get("conversation_hooks", ["Explore key concepts"]),
                    "learning_objectives": response_data.get("learning_objectives", ["Understand system design"]),
                }
            else:
                logger.warning("Agent returned no result, using placeholder")
                return self._generate_placeholder(cluster, architectural_layer)

        except Exception as e:
            logger.error("Episode planning failed", exc_info=e, extra={"cluster_size": len(cluster.files)})
            return self._generate_placeholder(cluster, architectural_layer)

    def _extract_cluster_dependencies(
        self, cluster_files: set[str], full_graph: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Extract dependency relationships within and entering the cluster."""
        cluster_set = set(cluster_files)
        internal = {}
        external = {}

        for file in cluster_files:
            deps = full_graph.get(file, [])
            internal_deps = [d for d in deps if d in cluster_set]
            external_deps = [d for d in deps if d not in cluster_set]
            if internal_deps:
                internal[file] = internal_deps
            if external_deps:
                external[file] = external_deps

        return {"internal": internal, "external": external}

    def _generate_placeholder(
        self, cluster: ClusterPlan, architectural_layer: Optional[str]
    ) -> Dict[str, Any]:
        """Generate placeholder metadata when LLM is unavailable."""
        layer_name = architectural_layer or "Components"
        file_count = len(cluster.files)
        return {
            "title": f"{layer_name}: {file_count} Related Files",
            "narrative_theme": f"Exploration of {layer_name.lower()} components and their interactions",
            "conversation_hooks": [
                "What is the purpose of this module?",
                "How do these files work together?",
                "What design patterns are used?",
            ],
            "learning_objectives": [
                "Understand the module structure",
                "Learn component relationships",
                "Grasp design decisions",
            ],
        }

    def _default_title(self, cluster: ClusterPlan) -> str:
        """Generate default title from cluster."""
        file_count = len(cluster.files)
        return f"Episode: {file_count} Related Files"


async def plan_episodes_from_clusters(
    clusters: List[ClusterPlan],
    dependency_graph: Dict[str, List[str]],
    architectural_layers: Dict[str, ClusterPlan],
    repo_context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Plan multiple episodes from clusters using LLM.

    Args:
        clusters: Dependency clusters to plan episodes for
        dependency_graph: Full dependency graph
        architectural_layers: Mapping of layer name to cluster
        repo_context: Optional repository metadata

    Returns:
        List of episode plan dictionaries
    """
    planner = EpisodePlanner()

    plans = []
    for cluster in clusters:
        # Find architectural layer for this cluster
        layer = None
        for layer_name, layer_cluster in architectural_layers.items():
            if cluster.files.intersection(layer_cluster.files):
                layer = layer_name
                break

        plan = await planner.plan_episode(cluster, dependency_graph, layer, repo_context)
        plans.append(plan)

    return plans


__all__ = ["EpisodePlanner", "plan_episodes_from_clusters"]
