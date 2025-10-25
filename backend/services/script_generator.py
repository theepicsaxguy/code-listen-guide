"""Script generation service using Agent Framework agents."""

import json
import logging
from typing import Any, Dict

from agent_framework.openai import OpenAIResponsesClient

from backend.agents import build_responses_client_options
from backend.agents import script_agent as script_agents
from backend.config import get_settings
from backend.models.agent_responses import ScriptAgentResponse

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


async def _run_script_agent(
    prompt: str, chapter_data: Dict[str, Any]
) -> ScriptAgentResponse:
    settings = get_settings()
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    agent = await script_agents.create_script_agent(client, chapter_data=chapter_data)
    response = await agent.run(prompt)
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, ScriptAgentResponse):
        return parsed
    if isinstance(parsed, dict):
        return ScriptAgentResponse.model_validate(parsed)
    result = getattr(response, "result", None) or getattr(response, "text", None)
    if isinstance(result, ScriptAgentResponse):
        return result
    if isinstance(result, dict):
        return ScriptAgentResponse.model_validate(result)
    if isinstance(result, str):
        return ScriptAgentResponse.model_validate_json(result)
    if isinstance(response, ScriptAgentResponse):
        return response
    if isinstance(response, dict):
        return ScriptAgentResponse.model_validate(response)
    return ScriptAgentResponse(script=str(response))


async def generate_script(
    chapter_data: Dict[str, Any], code_context: Dict[str, Any], job_id: str
) -> ScriptAgentResponse:
    prompt = _build_prompt(chapter_data, code_context)
    try:
        script_payload = await _run_script_agent(prompt, chapter_data)
        if script_payload.script.strip():
            return script_payload
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
    return ScriptAgentResponse(
        chapter_number=chapter_data.get("number"),
        title=title,
        script=(
            "Welcome to {title}. In this chapter we explore the key concepts behind the project "
            "and how the code fits together. Review the repository while listening so you can "
            "pause and dive into the details that interest you most."
        ).format(title=title),
    )
