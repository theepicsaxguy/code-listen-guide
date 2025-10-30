import asyncio
from pathlib import Path
from typing import Annotated, Any, Dict, List

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
    """Parse repository using chonkie pipeline."""
    chonkie = chonkiePipeline()
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(chonkie.process_pipeline(Path(path)))
        return result
    finally:
        loop.close()


async def create_analyzer_agent(chat_client: Any) -> ChatAgent:
    tools = [
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
        tools=tools,
    )


async def analyzer_agent(settings: Any) -> ChatAgent:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_analyzer_agent(client)
