# 🎨 BrandPulse

A high-utility CLI tool to generate professional GitHub README banners with a consistent "Retro-Arcade Glitch" aesthetic.

![Banner](banner.png)

## Features
- [x] **Glitch Aesthetic**: Automated chromatic aberration (Cyan/Magenta offsets).
- [x] **Custom Backgrounds**: Support for using your own images (AI-generated or photos) as the banner backdrop.
- [x] **Stealth Text Mode**: Skip drawing text if your AI background already includes the project name.
- [x] **Local Branding**: Always adds a clean metadata footer to unify your repos.
- [x] **Auto-Formatting**: Automatically crops and darkens backgrounds for high-fidelity output.

## Usage
Requires Python 3 and the `Pillow` library.

### Default Style
```bash
python3 brand.py "Project Name"
```

### Custom AI Background (Gemini/Grok/DALL-E)
If you have an AI-generated image, use it as the background:
```bash
python3 brand.py "Project Name" --bg my_ai_image.png
```

### If your AI image already has the name:
Use the `--no-text` flag. BrandPulse will still add the scanlines, glow, and footer to make it look like part of your official ecosystem:
```bash
python3 brand.py "Project Name" --bg image_with_name.png --no-text
```

## Tech Stack
- **Python 3**
- **Pillow (PIL)**: For advanced image processing and typography rendering.
