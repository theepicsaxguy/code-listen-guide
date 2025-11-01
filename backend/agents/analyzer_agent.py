from pathlib import Path
from typing import Annotated, Any, Callable, Dict, List, Optional, Sequence

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient
from pydantic import Field

from backend.services.chonkie_pipeline import chonkiePipeline
from backend.tools.git_tools import clone_repository, list_repository_files
from . import build_responses_client_options


def _ai_clone_repo(url: Annotated[str, Field(description="Git repository URL")]) -> str:
    return clone_repository(url)


def _ai_list_files(
    path: Annotated[str, Field(description="Path to cloned repository")],
) -> List[str]:
    return list_repository_files(path)


def _ai_parse_repository(
    path: Annotated[str, Field(description="Path to cloned repository")],
) -> Dict[str, Any]:
    """Parse repository using chonkie pipeline.
    
    Note: This is a synchronous tool function that needs to call async code.
    Uses run_async_from_sync utility to safely handle event loop conflicts.
    """
    from backend.utils.async_runner import run_async_from_sync
    
    chonkie = chonkiePipeline()
    return run_async_from_sync(chonkie.process_pipeline, Path(path))


async def create_analyzer_agent(
    chat_client: Any,
    *,
    tools: Optional[Sequence[Callable[..., Any]]] = None,
) -> ChatAgent:
    resolved_tools = list(tools) if tools is not None else [
        _ai_clone_repo,
        _ai_list_files,
        _ai_parse_repository,
    ]
    return chat_client.create_agent(
        name="RepositoryAnalyzer",
        instructions=(
            "Clone the supplied repository, build a structural summary using chonkie pipeline, and respond with JSON. "
            "Use the available tools for git operations and advanced code parsing with chonkie."
        ),
        tools=resolved_tools,
    )


async def analyzer_agent(
    settings: Any,
    *,
    tools: Optional[Sequence[Callable[..., Any]]] = None,
) -> ChatAgent:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_analyzer_agent(client, tools=tools)
