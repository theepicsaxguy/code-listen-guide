from typing import Any

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential


async def create_outline_agent(chat_client: Any) -> ChatAgent:
    return chat_client.create_agent(
        name="OutlineGenerator",
        instructions=(
            "Generate a structured audiobook outline as JSON including chapter numbers, titles, "
            "goals, and estimated durations."
        ),
    )


async def outline_agent(settings: Any) -> Any:
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    return await create_outline_agent(client)
