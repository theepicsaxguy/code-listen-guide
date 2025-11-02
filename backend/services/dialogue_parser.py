"""Dialogue parsing & validation utilities for podcast scripts.

Responsible for:
 - Parsing Marcus/Sara speaker turns from raw agent output
 - Basic structural validation (speaker alternation ratio, minimum turns)
 - Lightweight metrics helpful for downstream synthesis (turn lengths)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Iterable
import re

SPEAKER_PATTERN = re.compile(r"^(Marcus|Sara):\s*(.+)$")


@dataclass(slots=True)
class DialogueTurn:
    speaker: str
    text: str
    word_count: int


class DialogueParser:
    """Parses and validates dialogue scripts.

    Expected format: one line per speaker turn beginning with
    'Marcus:' or 'Sara:' exactly.
    """

    def parse(self, script: str) -> List[DialogueTurn]:
        turns: List[DialogueTurn] = []
        for raw_line in script.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("[") and line.endswith("]"):
                # Section markers like [INTRO] are ignored for turn parsing
                continue
            m = SPEAKER_PATTERN.match(line)
            if not m:
                continue  # silently skip non-conforming lines (could log later)
            speaker, text = m.groups()
            words = [w for w in re.split(r"\s+", text) if w]
            turns.append(DialogueTurn(speaker=speaker, text=text, word_count=len(words)))
        return turns

    def validate(self, turns: Iterable[DialogueTurn]) -> bool:
        turns_list = list(turns)
        if len(turns_list) < 15:  # require reasonable dialogue length
            return False
        speakers = [t.speaker for t in turns_list]
        sara_count = sum(1 for s in speakers if s == "Sara")
        sara_ratio = sara_count / len(speakers)
        if sara_ratio < 0.30:  # builder voice should appear sufficiently
            return False
        # Check no extremely long monologue (> 400 words) single turn
        if any(t.word_count > 400 for t in turns_list):
            return False
        return True

    def summarize(self, turns: Iterable[DialogueTurn]) -> dict:
        turns_list = list(turns)
        if not turns_list:
            return {"total_turns": 0}
        total_words = sum(t.word_count for t in turns_list)
        avg_words = total_words / len(turns_list)
        sara_ratio = sum(1 for t in turns_list if t.speaker == "Sara") / len(turns_list)
        return {
            "total_turns": len(turns_list),
            "total_words": total_words,
            "avg_words_per_turn": round(avg_words, 2),
            "sara_turn_ratio": round(sara_ratio, 3),
        }


__all__ = ["DialogueParser", "DialogueTurn"]
