from typing import Any

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from . import build_responses_client_options
from .schemas import EpisodeAgentResponse


async def create_episode_agent(chat_client: Any) -> ChatAgent:
    return chat_client.create_agent(
        name="EpisodePlanner",
        instructions=(
            "Generate a compelling episode plan as JSON including title, narrative theme, "
            "conversation hooks, and learning objectives for a technical podcast episode "
            "based on a code repository dependency cluster."
        ),
        response_format=EpisodeAgentResponse,
    )


async def episode_agent(settings: Any) -> Any:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_episode_agent(client)