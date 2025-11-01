from __future__ import annotations

from typing import Any, Callable, Optional, Sequence

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from . import build_responses_client_options
from .schemas import OutlineAgentResponse


async def create_outline_agent(
    chat_client: Any,
    *,
    tools: Optional[Sequence[Callable[..., Any]]] = None,
) -> ChatAgent:
    resolved_tools = list(tools) if tools is not None else None
    return chat_client.create_agent(
        name="OutlineGenerator",
        instructions=(
            "Generate a structured audiobook outline as JSON including chapter numbers, titles, "
            "goals, and estimated durations."
        ),
        tools=resolved_tools,
        response_format=OutlineAgentResponse,
    )


async def outline_agent(
    settings: Any,
    *,
    tools: Optional[Sequence[Callable[..., Any]]] = None,
) -> ChatAgent:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_outline_agent(client, tools=tools)
