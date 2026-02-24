# Architecture

## Project Structure

```
ops-automation-toolkit/
├── assets/
│   ├── icons/          # Icon source files
│   └── samples/        # Sample images for testing
├── bin/
│   └── ops             # CLI entry point
├── docs/
│   ├── architecture.md # Project structure and design
│   └── workflow.md     # How to use the toolkit
├── src/
│   ├── cli.py          # Argument parsing and command routing
│   ├── common/
│   │   ├── fs.py       # File system utilities
│   │   └── logging.py  # Logging helpers
│   ├── icon/
│   │   └── generate_svg.py  # SVG icon generation
│   └── image/
│       ├── convert.py  # Batch convert images to JPG
│       ├── resize.py   # Smart crop and resize per platform
│       └── utils.py    # Shared image utilities
└── README.md
```

## Module Responsibilities

### `bin/ops`

Executable entry point. Adds the project root to `sys.path` and delegates to `src/cli.py`.

### `src/cli.py`

Parses CLI arguments using `argparse`. Routes commands to the appropriate module functions.

### `src/image/convert.py`

Converts PNG / BMP / WebP images to JPG format. Skips files that are already JPG.

### `src/image/resize.py`

Smart crop logic for social media platforms. Determines whether to output 1 or 3 images based on the source aspect ratio:

- **Ratio matches target** → resize directly
- **Wide enough for 2 crops** → output left, center, and right crops
- **Otherwise** → center crop

### Platform Targets

| Platform  | Size      | Ratio |
| --------- | --------- | ----- |
| Pinterest | 1000×1500 | 2:3   |
| FB / Ins  | 1080×1350 | 4:5   |
| X         | 1200×1200 | 1:1   |
