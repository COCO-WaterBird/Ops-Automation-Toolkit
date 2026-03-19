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


def _resize_crop_center(img: Image.Image, tw: int, th: int) -> Image.Image:
    """
    Keep aspect ratio: scale-to-cover then center-crop to exact (tw, th).
    This avoids stretching/distortion.
    """
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - tw) // 2
    top = (new_h - th) // 2
    return img.crop((left, top, left + tw, top + th))


def convert_to_webp_276x143(
    input_path: Path,
    output_dir: Path,
    quality: int = 85,
) -> Path:
    """
    Convert a single image to WebP with exact dimensions 276x143.

    - Supported input formats: png, jpg/jpeg, webp, bmp, tiff, svg
    - For svg, uses cairosvg if available (renders to a raster first).
    - Output: <stem>.webp
    """
    return convert_to_webp_fixed(
        input_path=input_path,
        output_dir=output_dir,
        width=276,
        height=143,
        quality=quality,
    )


def convert_to_webp_fixed(
    input_path: Path,
    output_dir: Path,
    width: int,
    height: int,
    quality: int = 85,
) -> Path:
    """
    Convert a single image to WebP with exact dimensions (width, height).

    - Supported input formats: png, jpg/jpeg, webp, bmp, tiff, svg
    - SVG: uses cairosvg (requires system-level libcairo).
    - Output: <stem>.webp
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{input_path.stem}.webp"

    ext = input_path.suffix.lower()
    if ext == ".svg":
        try:
            import cairosvg  # type: ignore
        except (ImportError, OSError) as e:
            raise RuntimeError(
                "SVG 转换需要安装 `cairosvg`。请先执行：pip install cairosvg"
            ) from e

        from io import BytesIO

        try:
            # Render at a higher width so we can still crop center without distortion.
            raster_width = max(1, width * 2)
            png_bytes = cairosvg.svg2png(url=str(input_path), output_width=raster_width)
        except OSError as e:
            # cairosvg/cairocffi 需要系统级的 libcairo 动态库（libcairo.so.2 / dylib）
            raise RuntimeError(
                "SVG 转换所需的系统库 `cairo/libcairo` 未安装。"
                "macOS 下通常可通过 Homebrew 安装：\n"
                "  brew install cairo\n"
                "然后重试该命令。"
            ) from e

        img = Image.open(BytesIO(png_bytes))
    else:
        img = Image.open(input_path)

    # Keep alpha if present; PIL will drop it for JPEG inputs anyway.
    if img.mode in {"RGBA", "LA"}:
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    img = _resize_crop_center(img, width, height)
    img.save(out_path, "WEBP", quality=quality)
    print(f"   Converted: {input_path.name} → {out_path.name}")
    return out_path


def convert_folder_to_webp_276x143(
    input_dir: Path,
    output_dir: Path,
    quality: int = 85,
    skip_svg: bool = False,
) -> list[Path]:
    """
    Batch convert images in a folder to WebP(276x143).
    """
    return convert_folder_to_webp_fixed(
        input_dir=input_dir,
        output_dir=output_dir,
        width=276,
        height=143,
        quality=quality,
        skip_svg=skip_svg,
    )


def convert_folder_to_webp_fixed(
    input_dir: Path,
    output_dir: Path,
    width: int,
    height: int,
    quality: int = 85,
    skip_svg: bool = False,
) -> list[Path]:
    """
    Batch convert images in a folder to WebP(width, height).
    """
    supported = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".svg"}
    images = [
        f
        for f in input_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in supported
        and (not skip_svg or f.suffix.lower() != ".svg")
    ]

    if not images:
        print("⚠️  No convertible images found.")
        return []

    print(f"\n🔄 Converting {len(images)} image(s) in: {input_dir}")
    results: list[Path] = []
    for img_path in images:
        out = convert_to_webp_fixed(
            input_path=img_path,
            output_dir=output_dir,
            width=width,
            height=height,
            quality=quality,
        )
        results.append(out)

    print(f"✅ Done. {len(results)} file(s) saved to: {output_dir}")
    return results