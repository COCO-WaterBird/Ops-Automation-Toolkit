"""
Merge photos from multiple sources into one flat folder.

Sources:
  - *tree*: walk a directory recursively and collect image files (e.g. Ever Oak).
  - *zips* (mixed): under each root, collect (1) images in normal subfolders and
    (2) images inside every ``.zip`` found anywhere under that root (nested zips
    included). Archives are extracted to a temp work dir, not next to your files.
"""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path
from typing import BinaryIO, Iterable

from src.common.fs import ensure_dir

# Common raster formats; extend if you use TIFF/HEIC etc.
DEFAULT_IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {"jpg", "jpeg", "png", "gif", "webp", "bmp", "heic", "tif", "tiff"}
)


def _norm_exts(exts: Iterable[str]) -> set[str]:
    return {e.lower().lstrip(".") for e in exts}


_CHUNK = 1024 * 1024


def sha256_file(path: Path) -> bytes:
    """SHA-256 digest of file contents (streaming, constant memory)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            h.update(chunk)
    return h.digest()


def sha256_stream(fp: BinaryIO) -> bytes:
    """SHA-256 digest of an open binary stream."""
    h = hashlib.sha256()
    for chunk in iter(lambda: fp.read(_CHUNK), b""):
        h.update(chunk)
    return h.digest()


def count_unique_images_in_zip_by_content(
    zip_path: Path,
    extensions: frozenset[str],
    seen: set[bytes],
) -> int:
    """
    For each image member inside ``zip_path``, hash content; count how many are new vs ``seen``.
    Updates ``seen`` in place. Does not extract to disk.
    """
    exts = extensions
    added = 0
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            suf = Path(name).suffix.lower().lstrip(".")
            if suf not in exts:
                continue
            with zf.open(name, "r") as fp:
                digest = sha256_stream(fp)
            if digest in seen:
                continue
            seen.add(digest)
            added += 1
    return added


def iter_images_in_tree(root: Path, extensions: frozenset[str] | None = None) -> list[Path]:
    """Return all image files under ``root`` (recursive)."""
    exts = extensions or DEFAULT_IMAGE_EXTENSIONS
    root = root.resolve()
    out: list[Path] = []
    if not root.is_dir():
        return out
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower().lstrip(".") in exts:
            out.append(p)
    return sorted(out)


def _unique_dest_file(dest_dir: Path, filename: str) -> Path:
    """If ``filename`` exists in ``dest_dir``, append _1, _2, ... before suffix."""
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    n = 1
    while True:
        cand = dest_dir / f"{stem}_{n}{suffix}"
        if not cand.exists():
            return cand
        n += 1


def _safe_extract_zip(zip_path: Path, dest_dir: Path) -> None:
    """Extract zip to ``dest_dir``, guarding against zip-slip."""
    dest_dir = dest_dir.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            if member.is_dir():
                continue
            name = member.filename
            if name.startswith("/") or ".." in Path(name).parts:
                continue
            target = (dest_dir / name).resolve()
            if not str(target).startswith(str(dest_dir) + "/") and target != dest_dir:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member, "r") as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)


def count_images_in_zip(zip_path: Path, extensions: frozenset[str] | None = None) -> int:
    """Count file entries in a zip whose suffix looks like an image (no extract)."""
    exts = extensions or DEFAULT_IMAGE_EXTENSIONS
    n = 0
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            suf = Path(name).suffix.lower().lstrip(".")
            if suf in exts:
                n += 1
    return n


def _zip_rel_key(zip_path: Path, root: Path) -> str:
    """Stable label from ``zip_path`` relative to ``root`` (no ``.zip`` suffix)."""
    try:
        rel = zip_path.relative_to(root)
    except ValueError:
        rel = Path(zip_path.name)
    parts = rel.with_suffix("").parts
    return "__".join(parts) if parts else zip_path.stem


def _extract_dir_for_zip(zip_path: Path, root: Path, work_dir: Path) -> Path:
    """Unique folder under ``work_dir`` for this archive (avoids stem collisions)."""
    key = _zip_rel_key(zip_path, root)
    safe = key.replace("..", "_")
    return work_dir / safe


def collect_images_from_mixed_zip_root(
    zip_dir: Path,
    work_dir: Path,
    source_label: str,
    extensions: frozenset[str] | None = None,
) -> list[tuple[Path, str]]:
    """
    For every ``*.zip`` under ``zip_dir`` (recursive, any subfolder), extract and collect images.

    Loose folders on disk are handled by :func:`collect_loose_images_under_root`.

    Returns ``(path, suggested_flat_name)`` for each image from archives.
    """
    exts = extensions or DEFAULT_IMAGE_EXTENSIONS
    zip_dir = zip_dir.resolve()
    work_dir = work_dir.resolve()
    pairs: list[tuple[Path, str]] = []
    if not zip_dir.is_dir():
        return pairs

    for zp in sorted(zip_dir.rglob("*.zip")):
        extract_root = _extract_dir_for_zip(zp, zip_dir, work_dir)
        extract_root.mkdir(parents=True, exist_ok=True)
        _safe_extract_zip(zp, extract_root)
        rel_key = _zip_rel_key(zp, zip_dir)
        for img in iter_images_in_tree(extract_root, exts):
            flat_name = f"{source_label}__{rel_key}__{img.name}"
            pairs.append((img, flat_name))

    return pairs


def collect_loose_images_under_root(
    root: Path,
    source_label: str,
    extensions: frozenset[str] | None = None,
) -> list[tuple[Path, str]]:
    """Images on disk under ``root``; names include relative path to avoid collisions."""
    exts = extensions or DEFAULT_IMAGE_EXTENSIONS
    root = root.resolve()
    pairs: list[tuple[Path, str]] = []
    if not root.is_dir():
        return pairs
    for img in iter_images_in_tree(root, exts):
        rel = img.relative_to(root)
        flat_name = f"{source_label}__{rel.as_posix().replace('/', '__')}"
        pairs.append((img, flat_name))
    return pairs


def merge_photo_sources(
    *,
    tree_dirs: list[Path],
    zip_dirs: list[Path],
    output_parent: Path,
    folder_name: str,
    extensions: frozenset[str] | None = None,
    dry_run: bool = False,
    dedupe_content: bool = False,
) -> tuple[Path, int]:
    """
    Create ``output_parent / folder_name`` and copy all images into it.

    - ``tree_dirs``: each directory is scanned recursively for images.
    - ``zip_dirs``: each root is processed as a *mixed* source: (1) all image files
      in normal folders under that root, and (2) all ``*.zip`` files anywhere under
      that root (extracted to a temp folder, then images collected).
    - ``dedupe_content``: if True, skip files whose bytes match an earlier file
      (SHA-256). First occurrence wins; later duplicates are omitted.

    Returns ``(destination_dir, file_count)`` — count is unique files written (or
    would be written), after deduplication when enabled.
    """
    exts = extensions or DEFAULT_IMAGE_EXTENSIONS
    output_parent = output_parent.resolve()
    dest = output_parent / folder_name
    if not dry_run:
        ensure_dir(str(dest))

    seen_hashes: set[bytes] | None = set() if dedupe_content else None
    count = 0
    work_root = output_parent / f".{folder_name}_merge_work"

    try:
        # 1) Trees: copy with basename; collisions resolved by _unique_dest_file
        for td in tree_dirs:
            td = td.resolve()
            for img in iter_images_in_tree(td, exts):
                name = img.name
                if len(tree_dirs) > 1 or zip_dirs:
                    name = f"{td.name}__{img.name}"
                if dedupe_content and seen_hashes is not None:
                    digest = sha256_file(img)
                    if digest in seen_hashes:
                        continue
                    seen_hashes.add(digest)
                elif dry_run:
                    count += 1
                    continue
                if dry_run:
                    count += 1
                    continue
                target = _unique_dest_file(dest, name)
                shutil.copy2(img, target)
                count += 1

        # 2) Mixed zip roots: loose images in folders + every nested .zip extracted
        for zd in zip_dirs:
            zd = zd.resolve()
            label = zd.name
            if dry_run:
                if zd.is_dir():
                    if dedupe_content and seen_hashes is not None:
                        for img in iter_images_in_tree(zd, exts):
                            digest = sha256_file(img)
                            if digest in seen_hashes:
                                continue
                            seen_hashes.add(digest)
                            count += 1
                        for zp in sorted(zd.rglob("*.zip")):
                            count += count_unique_images_in_zip_by_content(
                                zp, exts, seen_hashes
                            )
                    else:
                        for _img in iter_images_in_tree(zd, exts):
                            count += 1
                        for zp in zd.rglob("*.zip"):
                            count += count_images_in_zip(zp, exts)
                continue
            ensure_dir(str(work_root))
            z_work = work_root / zd.name.replace(" ", "_")
            for img, flat_name in collect_loose_images_under_root(zd, label, exts):
                if dedupe_content and seen_hashes is not None:
                    digest = sha256_file(img)
                    if digest in seen_hashes:
                        continue
                    seen_hashes.add(digest)
                target = _unique_dest_file(dest, flat_name)
                shutil.copy2(img, target)
                count += 1
            for img, flat_name in collect_images_from_mixed_zip_root(
                zd, z_work, label, exts
            ):
                if dedupe_content and seen_hashes is not None:
                    digest = sha256_file(img)
                    if digest in seen_hashes:
                        continue
                    seen_hashes.add(digest)
                target = _unique_dest_file(dest, flat_name)
                shutil.copy2(img, target)
                count += 1
    finally:
        if work_root.exists() and not dry_run:
            shutil.rmtree(work_root, ignore_errors=True)

    return dest, count


def cmd_merge(args) -> None:
    """argparse handler: ``args`` has tree, zips, output_parent, name, dry_run, extensions."""
    exts: frozenset[str] | None = None
    if getattr(args, "extensions", None):
        exts = frozenset(_norm_exts(s.strip() for s in args.extensions.split(",") if s.strip()))

    tree_dirs = [Path(p) for p in (args.tree or [])]
    zip_dirs = [Path(p) for p in (args.zips or [])]

    if not tree_dirs and not zip_dirs:
        raise SystemExit("Provide at least one --tree or --zips directory.")

    dedupe = getattr(args, "dedupe_content", False)
    dest, n = merge_photo_sources(
        tree_dirs=tree_dirs,
        zip_dirs=zip_dirs,
        output_parent=Path(args.output_parent),
        folder_name=args.name,
        extensions=exts,
        dry_run=args.dry_run,
        dedupe_content=dedupe,
    )

    if args.dry_run:
        label = "unique " if dedupe else ""
        print(f"[dry-run] Would create {dest} and copy {n} {label}image(s).")
    else:
        label = "unique " if dedupe else ""
        print(f"Done. Wrote {n} {label}file(s) to {dest}")
