from typing import Any

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential


async def outline_agent(settings: Any) -> Any:
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    return client.create_agent(
        name="OutlineGenerator",
        instructions="Generate a structured audiobook outline as JSON including titles, goals, and timing.",
    )
