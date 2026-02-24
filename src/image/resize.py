# from PIL import Image
# from pathlib import Path

# # Target dimensions per platform
# PLATFORMS = {
#     "pinterest": (1000, 1500),   # 2:3
#     "fbins":     (1080, 1350),   # 4:5
#     # "facebook":  (1200, 630),  # landscape
#     "X":         (1200, 1200),   # 1:1
# }

# TOLERANCE = 0.05  # Aspect ratio tolerance: 5%


# def _ratio_match(iw: int, ih: int, tw: int, th: int) -> bool:
#     """Check if the source image aspect ratio is close enough to the target."""
#     actual = iw / ih
#     target = tw / th
#     return abs(actual - target) / target <= TOLERANCE


# def _crop_region(img: Image.Image, tw: int, th: int, offset_x: int = 0) -> Image.Image:
#     """
#     Crop a tw×th region from the image.
#     offset_x: horizontal start position (0 = left, positive = shift right)
#     Vertical position is always centered.
#     """
#     iw, ih = img.size

#     # Scale up so both dimensions are at least as large as the target
#     scale = max(tw / iw, th / ih)
#     new_w = int(iw * scale)
#     new_h = int(ih * scale)
#     img = img.resize((new_w, new_h), Image.LANCZOS)

#     # Center vertically
#     top = (new_h - th) // 2
#     left = offset_x
#     return img.crop((left, top, left + tw, top + th))


# def smart_crop(img: Image.Image, tw: int, th: int, base: str, out_dir: Path) -> list[Path]:
#     """
#     Smart crop logic:
#     - Aspect ratio already matches → resize and save directly
#     - Scaled width fits 2 crops    → save left-center and right-center crops
#     - Otherwise                    → center crop and save one image
#     Returns a list of output file paths.
#     """
#     iw, ih = img.size
#     results = []

#     if _ratio_match(iw, ih, tw, th):
#         # Aspect ratio matches — resize only
#         out = out_dir / f"{base}.jpg"
#         img.resize((tw, th), Image.LANCZOS).save(out, "JPEG", quality=85)
#         results.append(out)
#         print(f"   [{out_dir.name}] Ratio matches → resized directly")

#     else:
#         # Scale height to th and check resulting width
#         scale = th / ih
#         scaled_w = int(iw * scale)

#         if scaled_w >= tw * 2:
#             # Wide enough to produce 2 crops.
#             # Both crops start from the center outward:
#             #   left crop:  center - tw     to center
#             #   right crop: center          to center + tw
#             center = scaled_w // 2
#             left_offset  = center - tw   # left crop starts here
#             right_offset = center        # right crop starts here

#             # Clamp to valid bounds
#             left_offset  = max(0, left_offset)
#             right_offset = min(scaled_w - tw, right_offset)

#             for i, offset in enumerate([left_offset, right_offset], start=1):
#                 out = out_dir / f"{base}_{i}.jpg"
#                 _crop_region(img, tw, th, offset_x=offset).save(out, "JPEG", quality=85)
#                 results.append(out)
#             print(f"   [{out_dir.name}] Wide enough → saved 2 crops (center-outward)")

#         else:
#             # Center crop — single output
#             out = out_dir / f"{base}.jpg"
#             _crop_region(img, tw, th, offset_x=0).save(out, "JPEG", quality=85)
#             results.append(out)
#             print(f"   [{out_dir.name}] Center crop → saved 1 image")

#     return results


# def process_image(input_path: Path, output_root: Path) -> None:
#     """Process a single image and export to all platform folders."""
#     img = Image.open(input_path).convert("RGB")
#     base = input_path.stem
#     print(f"\n🖼️  Processing: {input_path.name}  ({img.width}×{img.height})")

#     for platform, (tw, th) in PLATFORMS.items():
#         out_dir = output_root / platform
#         out_dir.mkdir(parents=True, exist_ok=True)
#         smart_crop(img, tw, th, base, out_dir)


# def process_folder(input_dir: Path, output_root: Path) -> None:
#     """Batch process all images in the given folder."""
#     exts = {".jpg", ".jpeg", ".png"}
#     images = [f for f in input_dir.iterdir() if f.suffix.lower() in exts]

#     if not images:
#         print("⚠️  No image files found.")
#         return

#     for img_path in images:
#         process_image(img_path, output_root)

#     print("\n✅ All done!")

from PIL import Image
from pathlib import Path

# Target dimensions per platform
PLATFORMS = {
    "pinterest": (1000, 1500),   # 2:3
    "fbins":     (1080, 1350),   # 4:5
    # "facebook":  (1200, 630),  # landscape
    "X":         (1200, 1200),   # 1:1
}

TOLERANCE = 0.05  # Aspect ratio tolerance: 5%


def _ratio_match(iw: int, ih: int, tw: int, th: int) -> bool:
    """Check if the source image aspect ratio is close enough to the target."""
    actual = iw / ih
    target = tw / th
    return abs(actual - target) / target <= TOLERANCE


def _crop_region(img: Image.Image, tw: int, th: int, offset_x: int = 0) -> Image.Image:
    """
    Crop a tw×th region from the image.
    offset_x: horizontal start position (0 = left, positive = shift right)
    Vertical position is always centered.
    """
    iw, ih = img.size

    # Scale up so both dimensions are at least as large as the target
    scale = max(tw / iw, th / ih)
    new_w = int(iw * scale)
    new_h = int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center vertically
    top = (new_h - th) // 2
    left = offset_x
    return img.crop((left, top, left + tw, top + th))


def smart_crop(img: Image.Image, tw: int, th: int, base: str, out_dir: Path) -> list[Path]:
    """
    Smart crop logic:
    - Aspect ratio already matches → resize and save directly
    - Scaled width fits 2 crops    → save 3 crops (left, center, right)
    - Otherwise                    → center crop and save one image
    Returns a list of output file paths.
    """
    iw, ih = img.size
    results = []

    if _ratio_match(iw, ih, tw, th):
        # Aspect ratio matches — resize only
        out = out_dir / f"{base}.jpg"
        img.resize((tw, th), Image.LANCZOS).save(out, "JPEG", quality=85)
        results.append(out)
        print(f"   [{out_dir.name}] Ratio matches → resized directly")

    else:
        # Scale height to th and check resulting width
        scale = th / ih
        scaled_w = int(iw * scale)

        if scaled_w >= tw * 2:
            # Wide enough — save 3 crops: left, center, right
            center = scaled_w // 2
            left_offset   = max(0, center - tw)
            right_offset  = min(scaled_w - tw, center)
            center_offset = max(0, min(scaled_w - tw, center - tw // 2))

            crops = [
                (f"{base}_1.jpg", left_offset),    # left
                (f"{base}_c.jpg", center_offset),  # center
                (f"{base}_2.jpg", right_offset),   # right
            ]
            for name, offset in crops:
                out = out_dir / name
                _crop_region(img, tw, th, offset_x=offset).save(out, "JPEG", quality=85)
                results.append(out)
            print(f"   [{out_dir.name}] Wide enough → saved 3 crops (left + center + right)")

        else:
            # Center crop — single output
            out = out_dir / f"{base}.jpg"
            _crop_region(img, tw, th, offset_x=0).save(out, "JPEG", quality=85)
            results.append(out)
            print(f"   [{out_dir.name}] Center crop → saved 1 image")

    return results


def process_image(input_path: Path, output_root: Path) -> None:
    """Process a single image and export to all platform folders."""
    img = Image.open(input_path).convert("RGB")
    base = input_path.stem
    print(f"\n🖼️  Processing: {input_path.name}  ({img.width}×{img.height})")

    for platform, (tw, th) in PLATFORMS.items():
        out_dir = output_root / platform
        out_dir.mkdir(parents=True, exist_ok=True)
        smart_crop(img, tw, th, base, out_dir)


def process_folder(input_dir: Path, output_root: Path) -> None:
    """Batch process all images in the given folder."""
    exts = {".jpg", ".jpeg", ".png"}
    images = [f for f in input_dir.iterdir() if f.suffix.lower() in exts]

    if not images:
        print("⚠️  No image files found.")
        return

    for img_path in images:
        process_image(img_path, output_root)

    print("\n✅ All done!")