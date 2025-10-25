from typing import Any

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from . import build_responses_client_options
from .schemas import OutlineAgentResponse


async def create_outline_agent(chat_client: Any) -> ChatAgent:
    return chat_client.create_agent(
        name="OutlineGenerator",
        instructions=(
            "Generate a structured audiobook outline as JSON including chapter numbers, titles, "
            "goals, and estimated durations."
        ),
        response_format=OutlineAgentResponse,
    )


async def outline_agent(settings: Any) -> Any:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_outline_agent(client)
