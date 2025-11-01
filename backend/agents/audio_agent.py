from typing import Any, Optional, Sequence

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from backend.tools.audio_tools import _ai_tts, _ai_upload
from . import build_responses_client_options
from .schemas import AudioAgentResponse


async def create_audio_agent(
    chat_client: Any,
    *,
    tools: Optional[Sequence[Any]] = None,
) -> ChatAgent:
    resolved_tools = list(tools) if tools is not None else [_ai_tts, _ai_upload]
    return chat_client.create_agent(
        name="AudioProducer",
        instructions=(
            "Turn scripts into MP3 files, upload them to storage, and return the remote URL. "
            "Use the provided tools for text-to-speech and uploads."
        ),
        tools=resolved_tools,
        response_format=AudioAgentResponse,
    )


async def audio_agent(
    settings: Any,
    *,
    tools: Optional[Sequence[Any]] = None,
) -> ChatAgent:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_audio_agent(client, tools=tools)
