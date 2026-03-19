# import argparse
# from src.image.convert import cmd_convert
# from src.image.resize import cmd_resize
# from src.icon.generate_svg import cmd_svg

# # crop.py 你目录里没有，先去掉
# # from src.image.crop import cmd_crop


# def build_parser() -> argparse.ArgumentParser:
#     p = argparse.ArgumentParser(prog="ops", description="Ops Automation Toolkit")
#     sub = p.add_subparsers(dest="group", required=True)

#     # ops img ...
#     img = sub.add_parser("img", help="Image batch tools")
#     img_sub = img.add_subparsers(dest="img_cmd", required=True)

#     c = img_sub.add_parser("convert", help="Convert images (png->jpg etc)")
#     cmd_convert(c)

#     r = img_sub.add_parser("resize", help="Resize images in batch")
#     cmd_resize(r)

#     # crop 暂时注释掉，等你创建 crop.py 后再打开
#     # cr = img_sub.add_parser("crop", help="Crop images in batch")
#     # cmd_crop(cr)

#     # ops icon ...
#     icon = sub.add_parser("icon", help="Icon tools")
#     icon_sub = icon.add_subparsers(dest="icon_cmd", required=True)

#     s = icon_sub.add_parser("svg", help="Generate/normalize SVG icons")
#     cmd_svg(s)

#     return p


# def main():
#     parser = build_parser()
#     args = parser.parse_args()
#     args.handler(args)


# if __name__ == "__main__":
#     main()



import argparse
from pathlib import Path

from src.image.convert import (
    convert_folder,
    convert_folder_to_webp_276x143,
    convert_folder_to_webp_fixed,
)
from src.image.resize import process_folder


def cmd_convert(args):
    convert_folder(
        input_dir=Path(args.input),
        output_dir=Path(args.output),
        quality=args.quality,
    )


def cmd_resize(args):
    process_folder(
        input_dir=Path(args.input),
        output_root=Path(args.output),
    )


def cmd_process(args):
    """Convert then resize in one step."""
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    tmp_dir = output_dir / "_converted"

    print("=== Step 1: Convert to JPG ===")
    converted = convert_folder(input_dir, tmp_dir, quality=args.quality)

    print("\n=== Step 2: Resize for all platforms ===")
    process_folder(tmp_dir, output_dir)

    # Clean up temp folder
    for f in converted:
        f.unlink(missing_ok=True)
    if tmp_dir.exists():
        tmp_dir.rmdir()

def cmd_webp_276x143(args):
    convert_folder_to_webp_276x143(
        input_dir=Path(args.input),
        output_dir=Path(args.output),
        quality=args.quality,
        skip_svg=args.skip_svg,
    )

def cmd_webp_fixed(args):
    convert_folder_to_webp_fixed(
        input_dir=Path(args.input),
        output_dir=Path(args.output),
        width=args.width,
        height=args.height,
        quality=args.quality,
        skip_svg=args.skip_svg,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ops",
        description="ops-automation-toolkit CLI",
    )
    sub = parser.add_subparsers(dest="group", required=True)

    # ── ops image ──────────────────────────────────────
    image_parser = sub.add_parser("image", help="Image processing commands")
    image_sub = image_parser.add_subparsers(dest="command", required=True)

    # shared arguments
    def add_io_args(p, default_output: str):
        p.add_argument("--input",   required=True,        help="Input folder path")
        p.add_argument("--output",  default=default_output, help="Output folder path")
        p.add_argument("--quality", type=int, default=85, help="Quality (1-95, default: 85)")

    # ops image convert
    p_convert = image_sub.add_parser("convert", help="Batch convert images to JPG")
    add_io_args(p_convert, "output/converted")
    p_convert.set_defaults(func=cmd_convert)

    # ops image resize
    p_resize = image_sub.add_parser("resize", help="Resize images for each platform")
    add_io_args(p_resize, "output")
    p_resize.set_defaults(func=cmd_resize)

    # ops image process
    p_process = image_sub.add_parser("process", help="Convert + resize in one step")
    add_io_args(p_process, "output")
    p_process.set_defaults(func=cmd_process)

    # ops image webp-276x143
    p_webp = image_sub.add_parser("webp-276x143", help="Convert images to WebP(276x143)")
    add_io_args(p_webp, "output/webp-276x143")
    p_webp.add_argument(
        "--skip-svg",
        action="store_true",
        help="Skip .svg files (useful if system cairo libs are not installed).",
    )
    p_webp.set_defaults(func=cmd_webp_276x143)

    # ops image webp-fixed
    p_webp_fixed = image_sub.add_parser(
        "webp-fixed",
        help="Convert images to WebP with fixed size (--width/--height)",
    )
    p_webp_fixed.add_argument("--input", required=True, help="Input folder path")
    p_webp_fixed.add_argument("--output", default="output/webp-fixed", help="Output folder path")
    p_webp_fixed.add_argument("--width", type=int, required=True, help="Output width (px)")
    p_webp_fixed.add_argument("--height", type=int, required=True, help="Output height (px)")
    p_webp_fixed.add_argument("--quality", type=int, default=85, help="WebP quality (1-95, default: 85)")
    p_webp_fixed.add_argument(
        "--skip-svg",
        action="store_true",
        help="Skip .svg files (useful if system cairo libs are not installed).",
    )
    p_webp_fixed.set_defaults(func=cmd_webp_fixed)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()