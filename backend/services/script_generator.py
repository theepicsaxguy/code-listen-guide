"""Script generation service using Agent Framework agents."""

import json
import logging
from typing import Any, Dict

from agent_framework.openai import OpenAIResponsesClient

from backend.agents import build_responses_client_options
from backend.agents import script_agent as script_agents
from backend.agents.schemas import ScriptAgentResponse
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


async def _run_script_agent(
    prompt: str, chapter_data: Dict[str, Any]
) -> ScriptAgentResponse | None:
    settings = get_settings()
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    agent = await script_agents.create_script_agent(client, chapter_data=chapter_data)
    thread = agent.get_new_thread()
    response = await agent.run(prompt, thread=thread)
    if isinstance(response, ScriptAgentResponse):
        return response
    candidate = getattr(response, "result", None)
    if isinstance(candidate, ScriptAgentResponse):
        return candidate
    if isinstance(candidate, dict):
        return ScriptAgentResponse.model_validate(candidate)
    text_candidate = getattr(response, "text", None)
    if isinstance(text_candidate, str):
        return ScriptAgentResponse(
            chapter_number=chapter_data.get("number"),
            chapter_title=chapter_data.get("title"),
            script=text_candidate,
        )
    if isinstance(candidate, str):
        return ScriptAgentResponse(
            chapter_number=chapter_data.get("number"),
            chapter_title=chapter_data.get("title"),
            script=candidate,
        )
    return None


async def generate_script(
    chapter_data: Dict[str, Any], code_context: Dict[str, Any], job_id: str
) -> ScriptAgentResponse:
    prompt = _build_prompt(chapter_data, code_context)
    try:
        script_response = await _run_script_agent(prompt, chapter_data)
        if script_response and script_response.script:
            return script_response
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
    fallback_script = (
        f"Welcome to {title}. In this chapter we explore the key concepts behind the project and how the code fits together. "
        "Review the repository while listening so you can pause and dive into the details that interest you most."
    )
    return ScriptAgentResponse(
        chapter_number=chapter_data.get("number"),
        chapter_title=title,
        script=fallback_script,
    )
