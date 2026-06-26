# Ops Automation Toolkit

批量图像处理 + 图标生成工具集。

## 功能

- **格式转换**：PNG / BMP / WebP → JPG
- **智能裁剪**：按平台规则自动裁剪（Pinterest / FB Ins / X）
- **WebP 输出**：支持固定尺寸批量转 WebP
- **图标生成**：SVG 图标规范化生成

## 环境要求

- Python 3.10+
- Pillow
- （可选）cairosvg + libcairo：用于 SVG 转 raster
- （可选）ImageMagick：部分历史流程依赖

## 安装

```bash
pip install Pillow
```

## 快速开始

```bash
chmod +x bin/ops
```

## CLI 命令

### 1. 格式转换（PNG → JPG）

```bash
./bin/ops image convert --input ./assets/samples --output ./output/converted
```

### 2. 智能裁剪（按平台输出）

```bash
./bin/ops image resize --input ./assets/samples --output ./output
```

输出目录：
- `output/pinterest/`（1000×1500）
- `output/fbins/`（1080×1350）
- `output/X/`（1200×1200）

裁剪逻辑：
- 原图比例与目标接近 → 直接缩放，输出 1 张
- 宽度足够容纳 2 个裁剪框 → 输出左、中、右 3 张
- 其他情况 → 中心裁剪，输出 1 张

### 3. 一步完成：转换 + 裁剪

```bash
./bin/ops image process --input ./assets/samples --output ./output
```

### 4. 固定尺寸转 WebP（276×143）

```bash
./bin/ops image webp-276x143 --input ./assets/samples --output ./output/webp-276x143 --skip-svg
```

### 5. 自定义尺寸转 WebP

```bash
./bin/ops image webp-fixed --input ./assets/samples --output ./output/webp-1104x572 --width 1104 --height 572 --skip-svg
```

- `--skip-svg`：跳过 `.svg` 文件（避免 cairo 依赖报错）

### 6. 图标生成

```bash
./bin/ops icon svg --help
```

## 项目结构

```
ops-automation-toolkit/
├── bin/
│   └── ops                # CLI 入口
├── src/
│   ├── cli.py             # 命令路由
│   ├── image/
│   │   ├── convert.py     # 格式转换
│   │   └── resize.py      # 智能裁剪
│   └── icon/
│       └── generate_svg.py # SVG 生成
├── assets/
│   └── samples/           # 示例图片
├── output/                # 输出目录
└── docs/
    ├── workflow.md        # 工作流说明
    └── architecture.md    # 架构说明
```

## 常见问题

**Q: 执行 `./bin/ops` 报 `from: command not found`？**

A: 确保文件有执行权限且 shebang 在第一行：
```bash
chmod +x bin/ops
```

**Q: SVG 转换失败？**

A: 安装 cairo：
```bash
brew install cairo
pip install cairosvg
```

或使用 `--skip-svg` 跳过。

---

更多细节请参考 `docs/workflow.md` 和 `docs/architecture.md`。
