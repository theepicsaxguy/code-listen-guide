from typing import Any, Dict

from agent_framework import AIFunction
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from backend.tools.db_tools import save_chapter_script


def _ai_save_script(job_id: str, chapter_number: int, script: str) -> bool:
    return save_chapter_script(job_id, chapter_number, script)


async def script_agent(settings: Any, chapter_ctx: Dict[str, Any]) -> Any:
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    return client.create_agent(
        name=f"ScriptWriter_{chapter_ctx.get('number', 'x')}",
        instructions="Write a narration script for the chapter using the supplied analysis context.",
        tools=[AIFunction(_ai_save_script)],
    )
