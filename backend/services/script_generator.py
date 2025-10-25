"""Script generation service using Microsoft Agent Framework agents."""

import json
import logging
from typing import Any, Dict

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from backend.agents import script_agent as script_agents
from backend.config import get_settings

logger = logging.getLogger(__name__)


def _build_prompt(chapter_data: Dict[str, Any], code_context: Dict[str, Any]) -> str:
    chapter_json = json.dumps(chapter_data, indent=2)
    context_json = json.dumps(code_context, indent=2)[:4000]
    return (
        "You are writing an engaging audiobook narration script. "
        "Incorporate the provided chapter plan and code context. "
        "Write in a warm, explanatory tone with clear transitions and callouts for code listings.\n\n"
        f"Chapter details:\n{chapter_json}\n\n"
        f"Code context:\n{context_json}"
    )


async def _run_script_agent(prompt: str, chapter_data: Dict[str, Any]) -> str:
    settings = get_settings()
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    agent = await script_agents.create_script_agent(client, chapter_data=chapter_data)
    response = await agent.run(prompt)
    return getattr(response, "text", None) or getattr(response, "result", "")


async def generate_script(
    chapter_data: Dict[str, Any], code_context: Dict[str, Any], job_id: str
) -> str:
    prompt = _build_prompt(chapter_data, code_context)
    try:
        script_text = await _run_script_agent(prompt, chapter_data)
        if script_text.strip():
            return script_text
        logger.info(
            "Script agent returned empty response",
            extra={"job_id": job_id, "chapter": chapter_data.get("number")},
        )
    except Exception as exc:
        logger.warning(
            "Script agent failed; returning fallback script",
            extra={
                "job_id": job_id,
                "chapter": chapter_data.get("number"),
                "error": str(exc),
            },
        )
    title = chapter_data.get("title") or "Chapter"
    return (
        f"Welcome to {title}. In this chapter we explore the key concepts behind the project and how the code fits together. "
        "Review the repository while listening so you can pause and dive into the details that interest you most."
    )
