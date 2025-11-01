from typing import Any, Callable, List, Optional, Sequence

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from backend.tools.audio_tools import concat_audio_with_chapters
from backend.tools.storage_tools import upload_to_s3
from . import build_responses_client_options


def _ai_concat(chapter_paths: List[str], chapter_titles: List[str]) -> str:
    return concat_audio_with_chapters(chapter_paths, chapter_titles)


def _ai_upload(local_path: str, s3_key: str) -> str:
    return upload_to_s3(local_path, s3_key)


async def create_postprocess_agent(
    chat_client: Any,
    *,
    tools: Optional[Sequence[Callable[..., Any]]] = None,
) -> ChatAgent:
    resolved_tools = list(tools) if tools is not None else [_ai_concat, _ai_upload]
    return chat_client.create_agent(
        name="PostProcessor",
        instructions=(
            "Merge chapter audio, publish the final files, and return JSON describing deliverables."
        ),
        tools=resolved_tools,
    )


async def postprocess_agent(
    settings: Any,
    *,
    tools: Optional[Sequence[Callable[..., Any]]] = None,
) -> ChatAgent:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_postprocess_agent(client, tools=tools)
