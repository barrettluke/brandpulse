# 🎨 BrandPulse

A high-utility CLI tool to generate professional GitHub README banners with a consistent "Retro-Arcade Glitch" aesthetic.

![Banner](banner.png)

## Features
- [x] **Glitch Aesthetic**: Automated chromatic aberration (Cyan/Magenta offsets).
- [x] **Custom Backgrounds**: Support for using your own images (AI-generated or photos) as the banner backdrop.
- [x] **Auto-Formatting**: Automatically crops and darkens backgrounds to ensure text readability.
- [x] **Cyberpunk Styling**: Subtle scanlines and radial glows.
- [x] **High Resolution**: Optimized for GitHub's 1280x400 standard.

## Usage
Requires Python 3 and the `Pillow` library.

### Default Style
```bash
python3 brand.py "Project Name"
```

### Custom Background (Gemini/Grok/DALL-E)
If you have an AI-generated image or your own photo, you can use it as the background:
```bash
python3 brand.py "Project Name" --bg my_ai_image.png -o custom_banner.png
```

## Tech Stack
- **Python 3**
- **Pillow (PIL)**: For advanced image processing and typography rendering.

## Philosophy
*   **Ship Beats Perfect**: Get your repo looking professional instantly.
*   **Utility over Novelty**: A tool that solves the "ugly README" problem without opening an image editor.
