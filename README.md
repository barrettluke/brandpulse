# 🎨 BrandPulse

A high-utility CLI tool to generate professional GitHub README banners with consistent branding aesthetics.

![Banner](banner.png)

## Features
- [x] **Theme Presets**: Switch between styles like `Cyberpunk`, `Matrix`, `Sunset`, `Forest`, and `Ocean`.
- [x] **Background Gradients**: Smooth color transitions between primary and secondary colors.
- [x] **Opacity Control**: Fine-tune the alpha transparency of patterns, scanlines, and brand glows.
- [x] **Google Font Integration**: Choose from `Orbitron`, `Space Grotesk`, `Press Start 2P`, or `Inter`.
- [x] **Geometric Patterns**: Choose from `Grid`, `Dots`, `Hex`, or `Rays` to add texture to your background.
- [x] **Text Alignment**: Position your project title with `Left`, `Center`, or `Right` alignment.
- [x] **Glitch Aesthetic**: Automated chromatic aberration (Primary/Secondary offsets).
- [x] **Custom Backgrounds**: Support for using your own images (AI-generated or photos) as the banner backdrop.
- [x] **Stealth Text Mode**: Skip drawing text if your AI background already includes the project name.
- [x] **Local Branding**: Always adds a clean metadata footer to unify your repos.

## Usage
Requires Python 3 and the `Pillow` library.

### Basic Generation
```bash
python3 brand.py "Project Name"
```

### Gradients & Opacity
```bash
# Gradient background with heavy scanlines
python3 brand.py "Vivid Project" --gradient --alpha-scanlines 50

# Subtle pattern with high glow
python3 brand.py "Neon Dreams" --alpha-pattern 10 --alpha-glow 80
```

### Choosing a Font
```bash
python3 brand.py "Project Name" --font press-start
```

### Using Geometric Patterns
```bash
python3 brand.py "Project Name" --pattern hex
```

### Custom Themes & Colors
```bash
python3 brand.py "Project Name" --theme sunset
python3 brand.py "Project Name" --primary "#00FF00" --secondary "#FF00FF"
```

## Available Fonts
- `orbitron`: Industrial/Cyberpunk (Default).
- `space`: Modern/Tech.
- `press-start`: Classic 8-bit gaming.
- `inter`: Clean/Professional.

## Available Patterns
- `grid`, `dots`, `hex`, `rays`.

## Tech Stack
- **Python 3**
- **Pillow (PIL)**: For advanced image processing and procedural rendering.
