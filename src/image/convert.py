from PIL import Image
from pathlib import Path


def convert_to_jpg(input_path: Path, output_dir: Path, quality: int = 85) -> Path:
    """
    Convert a single image to JPG format.
    Skips the file if it is already a JPG.
    Returns the output file path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{input_path.stem}.jpg"

    if input_path.suffix.lower() in {".jpg", ".jpeg"}:
        print(f"   Skipped (already JPG): {input_path.name}")
        return input_path

    img = Image.open(input_path).convert("RGB")
    img.save(out_path, "JPEG", quality=quality)
    print(f"   Converted: {input_path.name} → {out_path.name}")
    return out_path


def convert_folder(input_dir: Path, output_dir: Path, quality: int = 85) -> list[Path]:
    """
    Batch convert all PNG images in a folder to JPG.
    Returns a list of output file paths.
    """
    supported = {".png", ".bmp", ".webp", ".tiff"}
    images = [f for f in input_dir.iterdir() if f.suffix.lower() in supported]

    if not images:
        print("⚠️  No convertible images found.")
        return []

    print(f"\n🔄 Converting {len(images)} image(s) in: {input_dir}")
    results = []
    for img_path in images:
        out = convert_to_jpg(img_path, output_dir, quality=quality)
        results.append(out)

    print(f"✅ Done. {len(results)} file(s) saved to: {output_dir}")
    return results