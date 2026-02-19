# 🎨 BrandPulse

A high-utility CLI tool to generate professional GitHub README banners with consistent branding aesthetics.

![Banner](banner.png)

## Features
- [x] **Theme Presets**: Switch between styles like `Cyberpunk`, `Matrix`, `Sunset`, `Forest`, and `Ocean`.
- [x] **Randomizer Mode**: Use `--random` to generate a surprise banner with randomized styles and effects.
- [x] **Glow Control**: Customize or remove brand glow shapes (`Center`, `Sides`, `Corners`, `None`).
- [x] **Background Gradients**: Smooth color transitions between primary and secondary colors.
- [x] **Opacity Control**: Fine-tune the alpha transparency of patterns, scanlines, and brand glows.
- [x] **Google Font Integration**: Choose from `Orbitron`, `Space Grotesk`, `Press Start 2P`, or `Inter`.
- [x] **Geometric Patterns**: Choose from `Grid`, `Dots`, `Hex`, `Rays`, `Waves`, `Circuit`, or `Stars`.
- [x] **Text Alignment**: Position your project title with `Left`, `Center`, or `Right` alignment.
- [x] **Visual Finishing**: Apply `Vignette` and `Border` effects for a cinematic feel.
- [x] **HD Rendering**: Uses 4X super-sampling and Lanczos anti-aliasing for razor-sharp output.
- [x] **Custom Backgrounds**: Support for using your own images (AI-generated or photos).

## Usage
Requires Python 3 and the `Pillow` library.

### Basic Generation
```bash
python3 brand.py "Project Name"
```

### Surprise Me (Random Mode)
```bash
python3 brand.py "Project Name" --random
```

### Full Style Control
```bash
# Sunset gradient with a vignette, 10px border, and hex pattern
python3 brand.py "My Project" --gradient --theme sunset --vignette --border 10 --pattern hex --glow sides
```

### Custom AI Background
```bash
python3 brand.py "Project Name" --bg my_ai_image.png --no-text
```

## Available Themes
- `cyberpunk`, `matrix`, `sunset`, `forest`, `ocean`, `mono`.

## Tech Stack
- **Python 3**
- **Pillow (PIL)**: For advanced image processing and procedural rendering.
