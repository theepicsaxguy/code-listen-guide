"""Dual voice synthesis for Marcus & Sara podcast dialogues.

Generates per‑turn audio using two distinct TTS voices and merges them
into a single MP3 with natural pacing.

Note: Integration with storage/upload handled by audio agent tools; this
service focuses on local synthesis & merging.
"""

from __future__ import annotations

from typing import List, Tuple
import tempfile
import os
from pydub import AudioSegment

try:  # Optional import; actual OpenAI client may be injected differently
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore

from backend.services.dialogue_parser import DialogueParser, DialogueTurn


VOICE_MAP = {
    "Marcus": "onyx",  # deeper authoritative
    "Sara": "nova",    # brighter curious
}


class DualVoiceSynthesizer:
    def __init__(self, api_key: str | None = None, model: str = "tts-1-hd") -> None:
        self.model = model
        self.parser = DialogueParser()
        self._client = AsyncOpenAI(api_key=api_key) if (AsyncOpenAI and api_key) else None

    async def synthesize_dialogue(self, script: str) -> Tuple[str, List[DialogueTurn]]:
        """Full pipeline: parse, validate, synthesize turns, merge.

        Returns tuple (final_audio_path, turns)
        """
        turns = self.parser.parse(script)
        if not self.parser.validate(turns):
            raise ValueError("Dialogue validation failed (insufficient balance or length)")
        segment_paths: List[str] = []
        for turn in turns:
            path = await self._synthesize_turn(turn)
            segment_paths.append(path)
        merged = self._merge_segments(segment_paths, turns)
        for p in segment_paths:
            try:
                os.remove(p)
            except OSError:
                pass
        return merged, turns

    async def _synthesize_turn(self, turn: DialogueTurn) -> str:
        voice = VOICE_MAP.get(turn.speaker, "alloy")
        if not self._client:
            # For environments without API key, create silent placeholder segment proportional to word count
            duration_ms = max(800, turn.word_count * 60)  # ~60ms per word heuristic
            seg = AudioSegment.silent(duration=duration_ms)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            seg.export(tmp.name, format="mp3")
            return tmp.name

        response = await self._client.audio.speech.create(
            model=self.model,
            voice=voice,
            input=turn.text,
            speed=1.0,
        )
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.write(response.content)  # type: ignore[attr-defined]
        tmp.close()
        return tmp.name

    def _merge_segments(self, paths: List[str], turns: List[DialogueTurn]) -> str:
        combined = AudioSegment.silent(duration=400)  # intro silence
        for i, (path, turn) in enumerate(zip(paths, turns)):
            seg = AudioSegment.from_mp3(path)
            combined += seg
            if i < len(paths) - 1:
                pause = 600 if "?" in turn.text else 350
                combined += AudioSegment.silent(duration=pause)
        combined += AudioSegment.silent(duration=800)  # outro
        out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        combined.export(out.name, format="mp3", bitrate="128k")
        return out.name


__all__ = ["DualVoiceSynthesizer", "VOICE_MAP"]
