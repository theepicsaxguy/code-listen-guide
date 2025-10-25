import logging
import tempfile
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def synthesize_speech(text: str, voice: str = "alloy") -> str:
    """
    Convert text to speech using OpenAI TTS.

    Args:
        text: The text to convert to speech
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)

    Returns:
        Path to the generated MP3 file
    """
    try:
        from openai import OpenAI

        from backend.config import get_settings

        settings = get_settings()

        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            # Return a placeholder file for development
            with tempfile.NamedTemporaryFile(prefix="cba_tts_", suffix=".mp3", delete=False) as temp_file:
                temp_file.write(text.encode("utf-8"))
                return temp_file.name

        client = OpenAI(api_key=settings.openai_api_key)

        # Create temp file for audio output
        with tempfile.NamedTemporaryFile(prefix="cba_tts_", suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name

        # Call OpenAI TTS API
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text, response_format="mp3")

        # Write audio to file
        response.stream_to_file(temp_path)

        logger.info(f"Generated TTS audio: {temp_path} (voice={voice}, text_length={len(text)})")
        return temp_path

    except Exception as e:
        logger.error(f"Failed to synthesize speech: {e}")
        # Return a placeholder file on error
        with tempfile.NamedTemporaryFile(prefix="cba_tts_error_", suffix=".mp3", delete=False) as temp_file:
            temp_file.write(f"ERROR: {str(e)}".encode("utf-8"))
            return temp_file.name


def concat_audio_with_chapters(chapter_paths: List[str], chapter_titles: List[str]) -> str:
    """
    Concatenate multiple audio files into a single audiobook with chapter markers.

    Args:
        chapter_paths: List of paths to chapter audio files
        chapter_titles: List of chapter titles

    Returns:
        Path to the merged MP3 file
    """
    try:
        from pydub import AudioSegment

        if len(chapter_paths) != len(chapter_titles):
            raise ValueError("Number of paths and titles must match")

        logger.info(f"Concatenating {len(chapter_paths)} chapters")

        # Load all audio files
        combined = AudioSegment.empty()
        silence = AudioSegment.silent(duration=2000)  # 2 seconds of silence between chapters

        for idx, (path, title) in enumerate(zip(chapter_paths, chapter_titles)):
            try:
                chapter_audio = AudioSegment.from_mp3(path)
                logger.info(f"Loaded chapter {idx + 1}: {title} ({len(chapter_audio)}ms)")

                # Add silence before chapter (except first)
                if idx > 0:
                    combined += silence

                # Add chapter audio
                combined += chapter_audio

            except Exception as e:
                logger.warning(f"Failed to load chapter {idx + 1} from {path}: {e}")
                continue

        if len(combined) == 0:
            raise ValueError("No audio segments were successfully loaded")

        # Create temp file for output
        with tempfile.NamedTemporaryFile(prefix="cba_audiobook_", suffix=".mp3", delete=False) as temp_file:
            output_path = temp_file.name

        # Export combined audio
        combined.export(output_path, format="mp3", bitrate="192k")

        logger.info(f"Created audiobook: {output_path} (duration={len(combined)}ms, chapters={len(chapter_paths)})")
        return output_path

    except ImportError:
        logger.error("pydub not available - audio concatenation disabled")
        # Return placeholder
        with tempfile.NamedTemporaryFile(prefix="cba_concat_error_", suffix=".mp3", delete=False) as temp_file:
            payload = "\n".join(f"{title}:{path}" for title, path in zip(chapter_titles, chapter_paths))
            temp_file.write(payload.encode("utf-8"))
            return temp_file.name
    except Exception as e:
        logger.error(f"Failed to concatenate audio: {e}")
        # Return placeholder on error
        with tempfile.NamedTemporaryFile(prefix="cba_concat_error_", suffix=".mp3", delete=False) as temp_file:
            temp_file.write(f"ERROR: {str(e)}".encode("utf-8"))
            return temp_file.name
