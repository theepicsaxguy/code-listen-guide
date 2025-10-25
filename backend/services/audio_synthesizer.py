"""
Audio synthesis service for converting scripts to speech.

DEPRECATED: This service is deprecated in favor of the Microsoft Agent Framework.
Use backend/agents/audio_agent.py instead.

This file is kept for reference but should not be used in new code.
"""

import asyncio
from pathlib import Path
from typing import Tuple, List


class AudioSynthesizer:
    """
    Synthesizes audio from text scripts using TTS APIs.

    DEPRECATED: Use backend/agents/audio_agent.py instead.
    """

    def __init__(self, api_key: str, provider: str = "openai"):
        """Initialize audio synthesizer (deprecated)."""
        self.provider = provider

    async def synthesize_chapter(
        self,
        script: str,
        output_path: Path,
        voice_id: str = "alloy"
    ) -> Tuple[Path, int]:
        """Convert script to audio (deprecated). Use backend/agents/audio_agent.py instead."""
        raise NotImplementedError("Use backend/agents/audio_agent.py instead")

    def _split_script(self, script: str, max_chars: int = 4096) -> List[str]:
        """Split script (deprecated)."""
        raise NotImplementedError("Use backend/agents/audio_agent.py instead")

    def _combine_audio_segments(self, segments: List[Path], output: Path) -> Path:
        """Combine audio segments (deprecated)."""
        raise NotImplementedError("Use backend/agents/audio_agent.py instead")

    def _get_audio_duration(self, audio_path: Path) -> int:
        """Get audio duration (deprecated)."""
        raise NotImplementedError("Use backend/agents/audio_agent.py instead")
