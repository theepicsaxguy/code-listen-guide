"""Post-processing utilities orchestrated through Microsoft Agent Framework agents."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from backend.agents import postprocess_agent
from backend.config import get_settings
from backend.tools.audio_tools import concat_audio_with_chapters

logger = logging.getLogger(__name__)


def _build_merge_prompt(audio_files: List[str], output_path: str) -> str:
    payload = json.dumps(
        {"audio_files": audio_files, "output_path": output_path}, indent=2
    )
    return (
        "You can merge chapter audio files by calling the available tools. "
        "Produce a single MP3 file and return its local path.\n\n"
        f"Work request:\n{payload}"
    )


def _build_deliverables_prompt(
    job_data: Dict[str, str], chapters: List[Dict[str, str]]
) -> str:
    payload = json.dumps({"job": job_data, "chapters": chapters}, indent=2)
    return (
        "Summarize the audiobook deliverables after post-processing. "
        "Return JSON with download targets, chapter metadata, and any important notes.\n\n"
        f"Context:\n{payload}"
    )


async def _run_postprocess_agent(prompt: str) -> str:
    settings = get_settings()
    credential = DefaultAzureCredential(exclude_cli_credential=True)
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        credential=credential,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
    )
    agent = await postprocess_agent.create_postprocess_agent(client)
    response = await agent.run(prompt)
    return getattr(response, "text", None) or getattr(response, "result", "")


async def merge_audio_files(
    audio_files: List[str], output_path: str, job_id: str
) -> str:
    prompt = _build_merge_prompt(audio_files, output_path)
    try:
        result_path = await _run_postprocess_agent(prompt)
        if result_path and Path(result_path).exists():
            return result_path
        logger.info(
            "Post-process agent returned non-existent path", extra={"job_id": job_id}
        )
    except Exception as exc:
        logger.warning(
            "Post-process agent failed; merging audio locally",
            extra={"job_id": job_id, "error": str(exc)},
        )
    titles = [f"Chapter {index + 1}" for index in range(len(audio_files))]
    return concat_audio_with_chapters(audio_files, titles)


async def create_deliverables(
    job_data: Dict[str, str], chapters: List[Dict[str, str]]
) -> Dict[str, Any]:
    prompt = _build_deliverables_prompt(job_data, chapters)
    try:
        raw_text = await _run_postprocess_agent(prompt)
        payload = json.loads(raw_text)
        if isinstance(payload, dict):
            return payload
        logger.info(
            "Post-process agent returned non-dict payload",
            extra={"job_id": job_data.get("id")},
        )
    except Exception as exc:
        logger.warning(
            "Deliverable summary generation failed",
            extra={"job_id": job_data.get("id"), "error": str(exc)},
        )
    return {
        "job_id": job_data.get("id"),
        "chapters": chapters,
        "notes": "Agent unavailable; provide manual QA before release.",
    }
