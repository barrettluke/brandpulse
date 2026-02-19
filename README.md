# 🎨 BrandPulse

A high-utility CLI tool to generate professional GitHub README banners with consistent branding aesthetics.

![Banner](banner.png)

## Features
- [x] **Theme Presets**: Switch between styles like `Cyberpunk`, `Matrix`, `Sunset`, `Forest`, and `Ocean`.
- [x] **Glitch Aesthetic**: Automated chromatic aberration (Primary/Secondary offsets).
- [x] **Custom Backgrounds**: Support for using your own images (AI-generated or photos) as the banner backdrop.
- [x] **Stealth Text Mode**: Skip drawing text if your AI background already includes the project name.
- [x] **Local Branding**: Always adds a clean metadata footer to unify your repos.
- [x] **Hex Color Overrides**: Specify exact primary/secondary colors via CLI.

## Usage
Requires Python 3 and the `Pillow` library.

### Basic Generation
```bash
python3 brand.py "Project Name"
```

### Using Themes
```bash
python3 brand.py "Project Name" --theme matrix
python3 brand.py "Project Name" --theme sunset
```

### Custom Colors (Hex)
```bash
python3 brand.py "Project Name" --primary "#00FF00" --secondary "#FF00FF"
```

### Custom AI Background
```bash
python3 brand.py "Project Name" --bg my_ai_image.png
```

## Available Themes
- `cyberpunk` (Default)
- `matrix`
- `sunset`
- `forest`
- `ocean`
- `mono`

## Tech Stack
- **Python 3**
- **Pillow (PIL)**: For advanced image processing and typography rendering.
