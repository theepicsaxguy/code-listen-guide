import tempfile
from pathlib import Path
from typing import List

from git import Repo


def clone_repository(url: str) -> str:
    destination = Path(tempfile.mkdtemp(prefix="cba_repo_"))
    Repo.clone_from(url, destination, depth=1)
    return str(destination)


def list_repository_files(path: str) -> List[str]:
    root = Path(path)
    results: List[str] = []
    for entry in root.rglob("*"):
        if entry.is_file() and ".git" not in entry.parts:
            results.append(str(entry.relative_to(root)))
    return results
