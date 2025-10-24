from typing import Any

from agent_framework import AIFunction
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from backend.tools.audio_tools import synthesize_speech
from backend.tools.storage_tools import upload_to_s3


def _ai_tts(text: str, voice: str = "alloy") -> str:
    return synthesize_speech(text, voice)


def _ai_upload(local_path: str, s3_key: str) -> str:
    return upload_to_s3(local_path, s3_key)


async def audio_agent(settings: Any) -> Any:
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    return client.create_agent(
        name="AudioProducer",
        instructions="Turn scripts into MP3 files and upload them to storage, returning the file URLs.",
        tools=[AIFunction(_ai_tts), AIFunction(_ai_upload)],
    )
