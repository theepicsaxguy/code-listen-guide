from typing import Annotated, Any, Dict, List

from agent_framework import AIFunction, ChatAgent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential
from pydantic import Field

from backend.tools.code_parser_tools import build_code_map
from backend.tools.git_tools import clone_repository, list_repository_files


def _ai_clone_repo(url: Annotated[str, Field(description="Git repository URL")]) -> str:
    return clone_repository(url)


def _ai_list_files(path: Annotated[str, Field(description="Path to cloned repository")]) -> List[str]:
    return list_repository_files(path)


def _ai_build_code_map(path: Annotated[str, Field(description="Path to cloned repository")]) -> Dict[str, Any]:
    return build_code_map(path)


async def create_analyzer_agent(chat_client: Any) -> ChatAgent:
    tools = [
        AIFunction(_ai_clone_repo),
        AIFunction(_ai_list_files),
        AIFunction(_ai_build_code_map),
    ]
    return chat_client.create_agent(
        name="RepositoryAnalyzer",
        instructions=(
            "Clone the supplied repository, build a structural summary, and respond with JSON. "
            "Use the available tools for git operations and code parsing."
        ),
        tools=tools,
    )


async def analyzer_agent(settings: Any) -> Any:
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    return await create_analyzer_agent(client)
