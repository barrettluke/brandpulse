#!/usr/bin/env python3
import sys
import os
import argparse
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import random
import urllib.request
import tempfile
from typing import List, Tuple, Optional, Dict, Union, Any

VERSION = "3.0.0-beta"

# Type Aliases
RGBColor = Tuple[int, int, int]
RGBAColor = Tuple[int, int, int, int]
Coords = List[float]

# Theme Presets
THEMES: Dict[str, Tuple[RGBColor, RGBColor, RGBColor, str]] = {
    "cyberpunk": ((13, 17, 23), (0, 232, 232), (232, 0, 232), "grid"),
    "matrix": ((0, 5, 0), (0, 255, 65), (0, 143, 17), "dots"),
    "sunset": ((45, 10, 50), (255, 82, 82), (255, 193, 7), "rays"),
    "forest": ((10, 30, 10), (164, 255, 150), (34, 139, 34), "hex"),
    "ocean": ((5, 20, 40), (0, 191, 255), (30, 144, 255), "waves"),
    "mono": ((10, 10, 10), (240, 240, 240), (100, 100, 100), "dots"),
    "retro90s": ((255, 255, 255), (255, 0, 255), (0, 255, 255), "squiggles"),
    "laser-school": ((15, 30, 80), (100, 240, 255), (255, 80, 200), "yearbook") 
}

# Verified URLs
FONT_URLS: Dict[str, str] = {
    "orbitron": "https://github.com/google/fonts/raw/main/ofl/orbitron/static/Orbitron-Black.ttf",
    "space": "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/static/SpaceGrotesk-Bold.ttf",
    "press-start": "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf",
    "inter": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Black.ttf",
    "lobster": "https://github.com/google/fonts/raw/main/ofl/lobster/Lobster-Regular.ttf",
    "concert": "https://github.com/google/fonts/raw/main/ofl/concertone/ConcertOne-Regular.ttf"
}

SYSTEM_FONTS: List[str] = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
]

def hex_to_rgb(h: str) -> RGBColor:
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join([c*2 for c in c])
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) # type: ignore

def download_font(font_name: str) -> Optional[str]:
    url = FONT_URLS.get(font_name.lower())
    if not url: return None
    target_path = os.path.join(tempfile.gettempdir(), f"bp_v5_{font_name}.ttf")
    if not os.path.exists(target_path):
        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, target_path)
        except:
            for f in SYSTEM_FONTS:
                if os.path.exists(f): return f
    return target_path

def draw_yearbook_laser(draw: ImageDraw.ImageDraw, start: Tuple[float, float], end: Tuple[float, float], color: RGBColor, scale: int, thickness: int):
    """Draws a soft-focus yearbook style laser beam."""
    # 1. Very wide soft diffusion
    draw.line([start, end], fill=(color[0], color[1], color[2], 25), width=thickness * 5 * scale)
    # 2. Focused vibrant glow
    draw.line([start, end], fill=(color[0], color[1], color[2], 120), width=thickness * scale)
    # 3. Inner core (lighter version of the color)
    core_color = tuple(min(255, c + 180) for c in color)
    draw.line([start, end], fill=(*core_color, 200), width=max(2, thickness // 2) * scale)

def draw_pattern(draw: ImageDraw.ImageDraw, pattern: str, width: int, height: int, color1: RGBColor, color2: RGBColor, alpha: int, scale: int) -> None:
    if pattern == "yearbook":
        # ALIGNED DIAGONAL RAYS ONLY
        origin_top = (width * 1.5, -height * 0.5)
        origin_bottom = (width * 1.5, height * 1.5)
        count = 12 
        # Cyan Rays
        for i in range(count):
            offset = (i - count//2) * (200 * scale)
            start = (origin_top[0] + offset, origin_top[1])
            angle = math.radians(155)
            length = width * 6
            end = (start[0] + length * math.cos(angle), start[1] + length * math.sin(angle))
            draw_yearbook_laser(draw, start, end, color1, scale, 5)
        # Pink Rays
        for i in range(count):
            offset = (i - count//2) * (200 * scale)
            start = (origin_bottom[0] + offset, origin_bottom[1])
            angle = math.radians(205)
            length = width * 6
            end = (start[0] + length * math.cos(angle), start[1] + length * math.sin(angle))
            draw_yearbook_laser(draw, start, end, color2, scale, 5)

def create_banner(name: str, output_path: str = "banner.png", theme: str = "laser-school", pattern: str = "yearbook", font_choice: str = "concert") -> str:
    scale = 4
    width, height = 1280 * scale, 400 * scale
    theme_data = THEMES.get(theme.lower(), THEMES["laser-school"])
    theme_bg, p_rgb, s_rgb, _ = theme_data

    # 1. Background Gradient (Pure backdrop)
    bg_top = (30, 70, 160)
    bg_bottom = (10, 15, 45)
    img = Image.new('RGB', (width, height), color=bg_bottom)
    top_layer = Image.new('RGB', (width, height), color=bg_top)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (1 - (y / height)))] * width)
    mask.putdata(mask_data)
    img.paste(top_layer, (0, 0), mask)
    
    # 2. Pattern Layer (Only Lasers)
    layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    draw_pattern(draw, pattern, width, height, p_rgb, s_rgb, 100, scale)
    img.paste(layer, (0,0), layer)
    
    # 3. TEXT ONLY (No Box, No Vignette)
    font_path = download_font(font_choice)
    font = ImageFont.truetype(font_path, (180 * scale if len(name) < 12 else 140 * scale)) if font_path else ImageFont.load_default()
    
    bbox = font.getbbox(name)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (width - tw) // 2, (height - th) // 2
    
    final_draw = ImageDraw.Draw(img)
    # Hard 90s Block Shadow
    shadow_offset = 12 * scale
    final_draw.text((tx + shadow_offset, ty + shadow_offset), name, font=font, fill=(0, 0, 0, 255))
    # Main White Text
    final_draw.text((tx, ty), name, font=font, fill=(255, 255, 255, 255))

    img = img.resize((1280, 400), Image.Resampling.LANCZOS)
    img.save(output_path, quality=100)
    return output_path

def main() -> None:
    parser = argparse.ArgumentParser(description=f"BrandPulse v{VERSION}")
    parser.add_argument("name", help="Project name")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-f", "--font", default="orbitron", help="Font choice")
    parser.add_argument("-t", "--theme", default="cyberpunk", choices=THEMES.keys(), help="Theme preset")
    parser.add_argument("-p", "--pattern", choices=["grid", "dots", "hex", "rays", "waves", "circuit", "stars", "squiggles", "yearbook", "none"], default="grid", help="Pattern")
    parser.add_argument("-a", "--align", default="center", choices=["left", "center", "right"], help="Align")
    parser.add_argument("-b", "--bg", help="Background path")
    parser.add_argument("--primary", help="Primary hex")
    parser.add_argument("--secondary", help="Secondary hex")
    parser.add_argument("--gradient", action="store_true", help="Enable gradient")
    parser.add_argument("--vignette", action="store_true", help="Enable vignette")
    parser.add_argument("--border", type=int, default=0, help="Border width")
    parser.add_argument("--alpha-pattern", type=int, default=30, help="Pattern opacity")
    parser.add_argument("--alpha-scanlines", type=int, default=15, help="Scanline opacity")
    parser.add_argument("--alpha-glow", type=int, default=25, help="Glow opacity")
    parser.add_argument("--no-text", action="store_true", help="Skip text")
    parser.add_argument("--no-scanlines", action="store_true", help="Remove retro lines")
    parser.add_argument("-r", "--random", action="store_true", help="Randomize styles")
    
    args = parser.parse_args()
    
    if args.random:
        print("🎲 Randomizing styles...")
        args.theme = random.choice(list(THEMES.keys()))
        args.pattern = random.choice(["grid", "dots", "hex", "rays", "waves", "circuit", "stars", "squiggles", "yearbook", "none"])
        args.font = random.choice(list(FONT_URLS.keys()))
        args.align = random.choice(["left", "center", "right"])
        args.no_scanlines = random.choice([True, False])
        args.gradient = random.choice([True, False])
        args.vignette = random.choice([True, False])
        args.alpha_pattern = random.randint(20, 60)
        args.alpha_scanlines = random.randint(5, 30)

    output_filename = args.output if args.output else f"{args.name.lower().replace(' ', '_')}_banner.png"
    print(f"🎨 BrandPulse v{VERSION} // Processing...")
    create_banner(args.name, output_filename, args.bg, args.theme, 
                  args.primary, args.secondary, args.pattern, args.align, args.font, args.no_text,
                  args.gradient, args.alpha_pattern, args.alpha_scanlines, args.alpha_glow,
                  args.vignette, args.border, args.no_scanlines)
    print(f"✅ Success! Banner saved to: {output_filename}")

if __name__ == "__main__":
    main()
