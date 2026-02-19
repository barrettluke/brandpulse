# 🎨 BrandPulse

A high-utility CLI tool to generate professional GitHub README banners with consistent branding aesthetics.

![Banner](banner.png)

## Features
- [x] **Theme Presets**: Switch between styles like `Cyberpunk`, `Matrix`, `Sunset`, `Forest`, and `Ocean`.
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

### Using Geometric Patterns
```bash
python3 brand.py "Project Name" --pattern hex
python3 brand.py "Project Name" --pattern grid --align left
```

### Custom Themes & Colors
```bash
python3 brand.py "Project Name" --theme sunset
python3 brand.py "Project Name" --primary "#00FF00" --secondary "#FF00FF"
```

### AI-Generated Backgrounds
```bash
python3 brand.py "Project Name" --bg my_ai_image.png --no-text
```

## Available Patterns
- `grid`: Engineering blueprint style.
- `dots`: Minimalist digital style.
- `hex`: Futuristic honeycomb style.
- `rays`: Dynamic radial energy style.

## Tech Stack
- **Python 3**
- **Pillow (PIL)**: For advanced image processing and procedural shape rendering.
