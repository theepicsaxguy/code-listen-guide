from typing import Any, Callable, List, Optional, Sequence

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from typing import Any, Callable, Optional, Sequence

from backend.tools.audio_tools import _ai_concat, _ai_upload
from . import build_responses_client_options


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
