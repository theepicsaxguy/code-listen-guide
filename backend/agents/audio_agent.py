from typing import Any

from agent_framework import AIFunction, ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from backend.tools.audio_tools import synthesize_speech
from backend.tools.storage_tools import upload_to_s3
from . import build_responses_client_options
from .schemas import AudioAgentResponse


def _ai_tts(text: str, voice: str = "alloy") -> str:
    return synthesize_speech(text, voice)


def _ai_upload(local_path: str, s3_key: str) -> str:
    return upload_to_s3(local_path, s3_key)


async def create_audio_agent(chat_client: Any) -> ChatAgent:
    return chat_client.create_agent(
        name="AudioProducer",
        instructions=(
            "Turn scripts into MP3 files, upload them to storage, and return the remote URL. "
            "Use the provided tools for text-to-speech and uploads."
        ),
        tools=[AIFunction(_ai_tts), AIFunction(_ai_upload)],
        response_format=AudioAgentResponse,
    )


async def audio_agent(settings: Any) -> Any:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_audio_agent(client)
