# 🎨 BrandPulse

A high-utility CLI tool to generate professional GitHub README banners with consistent branding aesthetics.

![Banner](banner.png)

## Features
- [x] **Shape Mixer**: Use `--glow-shape mixed` to use a variety of different geometric shapes in the background.
- [x] **Shape Count**: Use `--shape-count [number]` to control the quantity of accent shapes.
- [x] **Scatter Mode**: Use `--glow scatter` to randomly distribute shapes across the entire banner.
- [x] **Theme Presets**: Switch between styles like `Cyberpunk`, `Matrix`, `Sunset`, `Forest`, and `Ocean`.
- [x] **Randomizer Mode**: Use `--random` to generate a surprise banner with randomized styles and effects.
- [x] **Glow Control**: Customize or remove brand glow shapes (`Center`, `Sides`, `Corners`, `Scatter`, `None`).
- [x] **Background Gradients**: Smooth color transitions between primary and secondary colors.
- [x] **Opacity Control**: Fine-tune the alpha transparency of patterns, scanlines, and brand glows.
- [x] **Google Font Integration**: Choose from `Orbitron`, `Space Grotesk`, `Press Start 2P`, or `Inter`.
- [x] **Geometric Patterns**: Choose from `Grid`, `Dots`, `Hex`, `Rays`, `Waves`, `Circuit`, or `Stars`.
- [x] **HD Rendering**: Uses 4X super-sampling and Lanczos anti-aliasing for razor-sharp output.

## Usage
Requires Python 3 and the `Pillow` library.

### Basic Generation
```bash
python3 brand.py "Project Name"
```

### Shape Mixer (Mixed Shapes & Scatter)
```bash
# Mixed shapes scattered across a Matrix background
python3 brand.py "Mixed Project" --glow scatter --glow-shape mixed --shape-count 5 --theme matrix
```

### Surprise Me (Random Mode)
```bash
python3 brand.py "Project Name" --random
```

## Tech Stack
- **Python 3**
- **Pillow (PIL)**: For advanced image processing and procedural rendering.
