from pathlib import Path
from src.common.fs import ensure_dir


def out_path(in_path: Path, out_dir: str, new_ext: str | None = None) -> Path:
    ensure_dir(out_dir)
    ext = ("." + new_ext.lstrip(".")) if new_ext else in_path.suffix
    return Path(out_dir) / (in_path.stem + ext)