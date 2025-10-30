from typing import Any, Dict

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from backend.tools.db_tools import save_chapter_script
from . import build_responses_client_options
from .schemas import ScriptAgentResponse


def _ai_save_script(job_id: str, chapter_number: int, script: str) -> bool:
    return save_chapter_script(job_id, chapter_number, script)


async def create_script_agent(
    chat_client: Any, chapter_data: Dict[str, Any] | None = None
) -> ChatAgent:
    chapter_number = chapter_data.get("number") if chapter_data else None
    display_number = chapter_number if chapter_number is not None else "x"
    return chat_client.create_agent(
        name=f"ScriptWriter_{display_number}",
        instructions=(
            "Write a narration script for the provided chapter context. "
            "Focus on clear teaching, code explanations, and narrative flow."
        ),
        tools=[_ai_save_script],
        response_format=ScriptAgentResponse,
    )


async def script_agent(settings: Any, chapter_ctx: Dict[str, Any]) -> Any:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_script_agent(client, chapter_ctx)
