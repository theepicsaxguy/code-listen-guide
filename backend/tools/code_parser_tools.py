from pathlib import Path
from typing import Dict, List


def build_code_map(path: str) -> Dict[str, List[str]]:
    root = Path(path)
    modules: Dict[str, List[str]] = {}
    for file_path in root.rglob("*.py"):
        modules[str(file_path.relative_to(root))] = []
    return {"modules": modules}
