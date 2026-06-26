# Workflow

## Requirements

```bash
pip install Pillow
```

## Commands

### One-step: convert + resize

```bash
./bin/ops image process --input ./assets/samples --output ./output
```

### Convert only (PNG → JPG)

```bash
./bin/ops image convert --input ./assets/samples --output ./output/converted
```

### Resize only

```bash
./bin/ops image resize --input ./assets/samples --output ./output
```

### Help

```bash
./bin/ops image --help
```

## Output Structure

After running `process`, the output folder will look like:

```
output/
├── pinterest/
│   ├── photo_1.jpg   # left crop
│   ├── photo_c.jpg   # center crop
│   └── photo_2.jpg   # right crop
├── fbins/
│   └── photo.jpg
└── X/
    └── photo.jpg
```

## Crop Logic

| Source image          | Result                         |
| --------------------- | ------------------------------ |
| Already correct ratio | Resized directly, 1 file       |
| Wide (fits 2 crops)   | Left + center + right, 3 files |
| Other                 | Center crop, 1 file            |
