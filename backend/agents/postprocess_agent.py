from typing import Any, List

from agent_framework import AIFunction, ChatAgent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from backend.tools.audio_tools import concat_audio_with_chapters
from backend.tools.storage_tools import upload_to_s3


def _ai_concat(chapter_paths: List[str], chapter_titles: List[str]) -> str:
    return concat_audio_with_chapters(chapter_paths, chapter_titles)


def _ai_upload(local_path: str, s3_key: str) -> str:
    return upload_to_s3(local_path, s3_key)


async def create_postprocess_agent(chat_client: Any) -> ChatAgent:
    return chat_client.create_agent(
        name="PostProcessor",
        instructions=(
            "Merge chapter audio, publish the final files, and return JSON describing deliverables."
        ),
        tools=[AIFunction(_ai_concat), AIFunction(_ai_upload)],
    )


async def postprocess_agent(settings: Any) -> Any:
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    return await create_postprocess_agent(client)
