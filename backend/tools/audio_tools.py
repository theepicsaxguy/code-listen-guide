"""Audio processing utilities and tool wrappers."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


logger = logging.getLogger(__name__)


TTS_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "voice": {"type": "string"},
    },
    "required": ["text"],
}

TTS_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "audio_file": {"type": "string"},
    },
    "required": ["audio_file"],
}

UPLOAD_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "file_path": {"type": "string"},
        "s3_key": {"type": "string"},
    },
    "required": ["file_path", "s3_key"],
}

UPLOAD_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "url": {"type": "string"},
    },
    "required": ["url"],
}

CONCAT_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "audio_files": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "titles": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["audio_files"],
}

CONCAT_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "output_file": {"type": "string"},
    },
    "required": ["output_file"],
}


def _allocate_temp_path(prefix: str) -> Path:
    with tempfile.NamedTemporaryFile(prefix=prefix, suffix=".mp3", delete=False) as temp_file:
        return Path(temp_file.name)


def _tts_cache_path(text: str, voice: str) -> Path:
    digest = hashlib.sha256(f"{voice}:{text}".encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / f"cba_tts_{digest}.mp3"


def _concat_cache_path(audio_files: Iterable[str]) -> Path:
    digest = hashlib.sha256("|".join(sorted(audio_files)).encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / f"cba_concat_{digest}.mp3"


def synthesize_speech(text: str, voice: str = "alloy", *, destination: Optional[Path] = None) -> Path:
    """Convert text to speech using the configured OpenAI client."""

    target = destination or _allocate_temp_path("cba_tts_")
    if target.exists():
        return target
    try:
        from openai import OpenAI
        from backend.config import get_settings

        settings = get_settings()
        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            target.write_text(text, encoding="utf-8")
            return target
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.audio.speech.create(
            model="tts-1", voice=voice, input=text, response_format="mp3"
        )
        response.stream_to_file(str(target))
        logger.info("Generated TTS audio at %s", target)
        return target
    except Exception as exc:
        logger.error("Failed to synthesize speech: %s", exc)
        target.write_text(f"ERROR: {exc}", encoding="utf-8")
        return target


def concat_audio_with_chapters(
    chapter_paths: List[str],
    chapter_titles: Optional[List[str]] = None,
    *,
    destination: Optional[Path] = None,
) -> Path:
    """Concatenate audio chapters using pydub when available."""

    if chapter_titles and len(chapter_titles) != len(chapter_paths):
        raise ValueError("Chapter titles must align with provided paths")
    output_path = destination or _allocate_temp_path("cba_concat_")
    if output_path.exists():
        return output_path
    try:
        from pydub import AudioSegment

        combined = AudioSegment.empty()
        silence = AudioSegment.silent(duration=2000)
        for index, chapter_path in enumerate(chapter_paths):
            chapter_audio = AudioSegment.from_file(chapter_path)
            if index > 0:
                combined += silence
            combined += chapter_audio
        combined.export(output_path, format="mp3", bitrate="192k")
        logger.info("Created merged audio at %s", output_path)
        return output_path
    except ImportError as exc:
        logger.error("pydub not available: %s", exc)
    except Exception as exc:
        logger.error("Failed to concatenate audio: %s", exc)
    output_path.write_text("Concatenation failed", encoding="utf-8")
    return output_path


def _ai_tts(text: str, voice: str = "alloy") -> Dict[str, Any]:
    """Generate or reuse cached speech audio for the supplied text."""

    validated_input = validate_tool_inputs(
        {"text": text, "voice": voice}, TTS_INPUT_SCHEMA
    )
    cache_path = _tts_cache_path(validated_input["text"], validated_input.get("voice", "alloy"))
    audio_path = synthesize_speech(
        validated_input["text"],
        validated_input.get("voice", "alloy"),
        destination=cache_path,
    )
    result = {"audio_file": str(audio_path)}
    validate_tool_outputs(result, TTS_OUTPUT_SCHEMA)
    return result


async def _ai_tts_async(text: str, voice: str = "alloy") -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_tts`."""

    return await asyncio.to_thread(_ai_tts, text=text, voice=voice)


def _ai_concat(audio_files: Iterable[str], titles: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Merge multiple audio tracks into a single file."""

    title_list = list(titles or [])
    validated_input = validate_tool_inputs(
        {"audio_files": list(audio_files), "titles": title_list}, CONCAT_INPUT_SCHEMA
    )
    cache_path = _concat_cache_path(validated_input["audio_files"])
    merged_path = concat_audio_with_chapters(
        validated_input["audio_files"],
        title_list if title_list else None,
        destination=cache_path,
    )
    result = {"output_file": str(merged_path)}
    validate_tool_outputs(result, CONCAT_OUTPUT_SCHEMA)
    return result


async def _ai_concat_async(
    audio_files: Iterable[str], titles: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_concat`."""

    return await asyncio.to_thread(_ai_concat, audio_files=list(audio_files), titles=list(titles or []))


def _ai_upload(file_path: str, s3_key: str) -> Dict[str, Any]:
    """Upload a file to remote storage via the storage tool helper."""

    validated_input = validate_tool_inputs(
        {"file_path": file_path, "s3_key": s3_key}, UPLOAD_INPUT_SCHEMA
    )
    from backend.tools.storage_tools import upload_to_s3

    url = upload_to_s3(validated_input["file_path"], validated_input["s3_key"])
    result = {"url": url}
    validate_tool_outputs(result, UPLOAD_OUTPUT_SCHEMA)
    return result


async def _ai_upload_async(file_path: str, s3_key: str) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_upload`."""

    return await asyncio.to_thread(_ai_upload, file_path=file_path, s3_key=s3_key)
