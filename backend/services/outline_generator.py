"""Outline generation service backed by Agent Framework agents."""

import json
import logging
from typing import Any, Dict

from agent_framework.openai import OpenAIResponsesClient

from backend.agents import build_responses_client_options, outline_agent
from backend.agents.schemas import OutlineAgentResponse
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


async def _run_outline_agent(prompt: str) -> OutlineAgentResponse | None:
    settings = get_settings()
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    agent = await outline_agent.create_outline_agent(client)
    thread = agent.get_new_thread()
    response = await agent.run(prompt, thread=thread)
    if isinstance(response, OutlineAgentResponse):
        return response
    candidate = getattr(response, "result", None)
    if isinstance(candidate, OutlineAgentResponse):
        return candidate
    if isinstance(candidate, dict):
        return OutlineAgentResponse.model_validate(candidate)
    text_candidate = getattr(response, "text", None)
    if isinstance(text_candidate, str) and text_candidate.strip():
        return OutlineAgentResponse(chapters=[], raw_outline=text_candidate.strip())
    if isinstance(candidate, str) and candidate.strip():
        return OutlineAgentResponse(chapters=[], raw_outline=candidate.strip())
    return None


def _fallback_outline(
    analysis_data: Dict[str, Any], depth_tier: str
) -> OutlineAgentResponse:
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
    total_minutes = sum(chapter["estimated_duration_minutes"] for chapter in chapters)
    return OutlineAgentResponse(
        chapters=chapters,
        depth_tier=depth_tier,
        total_estimated_duration_minutes=total_minutes,
    )


async def generate_outline(
    analysis_data: Dict[str, Any], depth_tier: str, job_id: str
) -> OutlineAgentResponse:
    prompt = _build_prompt(analysis_data, depth_tier)
    try:
        response = await _run_outline_agent(prompt)
        if response and response.chapters:
            return response
        if response and response.raw_outline:
            logger.info(
                "Outline agent returned raw outline payload", extra={"job_id": job_id}
            )
            return response
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
