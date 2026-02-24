from pathlib import Path
from typing import Iterable


def iter_files(root: str, exts: Iterable[str]):
    rootp = Path(root)
    exts = {e.lower().lstrip(".") for e in exts}
    for p in rootp.rglob("*"):
        if p.is_file() and p.suffix.lower().lstrip(".") in exts:
            yield p


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)