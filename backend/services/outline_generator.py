"""Outline generation service backed by Microsoft Agent Framework agents."""

import json
import logging
from typing import Any, Dict

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from backend.agents import outline_agent
from backend.config import get_settings

logger = logging.getLogger(__name__)

_DEPTH_INSTRUCTIONS = {
    "survey": "Focus on top-level architecture and main modules. Aim for 10-15 chapters.",
    "standard": "Cover user-facing modules, critical internals, and architectural decisions. Aim for 20-30 chapters.",
    "comprehensive": "Document every subsystem and important implementation detail. Aim for 35-50 chapters.",
}


def _build_prompt(analysis_data: Dict[str, Any], depth_tier: str) -> str:
    summary = json.dumps(analysis_data, indent=2)[:4000]
    tier = depth_tier if depth_tier in _DEPTH_INSTRUCTIONS else "standard"
    guidance = _DEPTH_INSTRUCTIONS[tier]
    return (
        "You are an expert technical narrator planning an audiobook about a codebase. "
        "Use the repository analysis to design a multi-chapter outline. "
        "Respond with strict JSON containing chapters, estimated durations, learning objectives, and files covered.\n\n"
        f"Depth tier: {tier}\n"
        f"Guidance: {guidance}\n\n"
        f"Repository analysis summary:\n{summary}"
    )


async def _run_outline_agent(prompt: str) -> str:
    settings = get_settings()
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    agent = await outline_agent.create_outline_agent(client)
    response = await agent.run(prompt)
    return getattr(response, "text", None) or getattr(response, "result", "")


def _parse_outline(raw_text: str) -> Dict[str, Any]:
    try:
        payload = json.loads(raw_text)
        if isinstance(payload, dict) and "chapters" in payload:
            return payload
    except json.JSONDecodeError:
        logger.warning("Agent returned non-JSON outline payload")
    return {"chapters": [], "raw_outline": raw_text.strip()}


def _fallback_outline(analysis_data: Dict[str, Any], depth_tier: str) -> Dict[str, Any]:
    repo_name = analysis_data.get("repo_name") or "Unknown Repository"
    primary_language = next(
        iter((analysis_data.get("languages") or {}).keys()), "the project"
    )
    chapters = [
        {
            "number": 1,
            "title": f"Overview of {repo_name}",
            "description": "High-level architecture and goals",
            "estimated_duration_minutes": 12,
            "files_covered": [],
            "learning_objectives": [f"Understand the purpose of {repo_name}"],
        },
        {
            "number": 2,
            "title": f"Core {primary_language} Modules",
            "description": "Key components and how they collaborate",
            "estimated_duration_minutes": 18,
            "files_covered": [],
            "learning_objectives": [
                "Identify main modules",
                "Recognize extension points",
            ],
        },
    ]
    return {
        "chapters": chapters,
        "depth_tier": depth_tier,
        "total_estimated_duration_minutes": sum(
            chapter["estimated_duration_minutes"] for chapter in chapters
        ),
    }


async def generate_outline(
    analysis_data: Dict[str, Any], depth_tier: str, job_id: str
) -> Dict[str, Any]:
    prompt = _build_prompt(analysis_data, depth_tier)
    try:
        raw_text = await _run_outline_agent(prompt)
        parsed = _parse_outline(raw_text)
        if parsed.get("chapters"):
            return parsed
        logger.info(
            "Outline agent returned empty result, falling back to template",
            extra={"job_id": job_id},
        )
    except Exception as exc:
        logger.warning(
            "Outline agent failed; returning fallback outline",
            extra={"job_id": job_id, "error": str(exc)},
        )
    return _fallback_outline(analysis_data, depth_tier)
