import tempfile
from typing import List


def synthesize_speech(text: str, voice: str = "alloy") -> str:
    with tempfile.NamedTemporaryFile(prefix="cba_tts_", suffix=".mp3", delete=False) as temp_file:
        temp_file.write(text.encode("utf-8"))
        return temp_file.name


def concat_audio_with_chapters(chapter_paths: List[str], chapter_titles: List[str]) -> str:
    with tempfile.NamedTemporaryFile(prefix="cba_mix_", suffix=".mp3", delete=False) as temp_file:
        payload = "\n".join(f"{title}:{path}" for title, path in zip(chapter_titles, chapter_paths))
        temp_file.write(payload.encode("utf-8"))
        return temp_file.name
