from pathlib import Path
from src.common.fs import ensure_dir
from src.common.logging import get_logger


log = get_logger("ops.icon.svg")


def cmd_svg(p):
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--name", required=True, help="Icon name (without .svg)")
    p.set_defaults(handler=run)


def run(args):
    ensure_dir(args.out)
    out = Path(args.out) / f"{args.name}.svg"

    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">
  <rect x="16" y="16" width="96" height="96" rx="16" />
</svg>
"""
    out.write_text(svg, encoding="utf-8")
    log.info(f"generated: {out}")