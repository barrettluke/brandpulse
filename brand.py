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

VERSION = "2.8.0-beta"

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

def draw_vignette(img: Image.Image, intensity: float = 0.5) -> Image.Image:
    width, height = img.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(120):
        alpha = int(255 * intensity * (i / 120)**2)
        inset = i * 2
        draw.rectangle([inset, inset, width-inset, height-inset], outline=(0, 0, 0, alpha), width=3)
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

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
        # Perfectly aligned diagonal rays to form repeating diamond grid
        origin_top = (width * 1.5, -height * 0.5)
        origin_bottom = (width * 1.5, height * 1.5)
        
        count = 12 # More rays for a tighter grid
        
        # Cyan Rays (Downward slant)
        for i in range(count):
            offset = (i - count//2) * (200 * scale)
            start = (origin_top[0] + offset, origin_top[1])
            angle = math.radians(155)
            length = width * 6
            end = (start[0] + length * math.cos(angle), start[1] + length * math.sin(angle))
            draw_yearbook_laser(draw, start, end, color1, scale, 5)

        # Pink Rays (Upward slant)
        for i in range(count):
            offset = (i - count//2) * (200 * scale)
            start = (origin_bottom[0] + offset, origin_bottom[1])
            angle = math.radians(205)
            length = width * 6
            end = (start[0] + length * math.cos(angle), start[1] + length * math.sin(angle))
            draw_yearbook_laser(draw, start, end, color2, scale, 5)

def create_banner(name: str, output_path: str = "banner.png", bg_path: Optional[str] = None, theme: str = "cyberpunk", 
                  primary: Optional[str] = None, secondary: Optional[str] = None, pattern: Optional[str] = None, 
                  align: str = "center", font_choice: str = "orbitron", no_text: bool = False, gradient: bool = False,
                  alpha_pattern: int = 40, alpha_scanlines: int = 15, alpha_glow: int = 25, 
                  vignette: bool = False, border_width: int = 0, no_scanlines: bool = False) -> str:
    scale = 4
    width, height = 1280 * scale, 400 * scale
    theme_data = THEMES.get(theme.lower(), THEMES["cyberpunk"])
    theme_bg, theme_p, theme_s, theme_pattern = theme_data
    
    p_color = hex_to_rgb(primary) if primary else theme_p
    s_color = hex_to_rgb(secondary) if secondary else theme_s
    active_pattern = pattern if pattern else theme_pattern

    # Backdrop
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
    
    # Draw Patterns
    layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    if active_pattern != "none":
        draw_pattern(draw, active_pattern, width, height, p_color, s_color, alpha_pattern, scale)
    img.paste(layer, (0,0), layer)
    
    # Studio Vignette
    img = draw_vignette(img, 0.45)
    
    if not no_text:
        font_path = download_font(font_choice)
        font = ImageFont.truetype(font_path, (180 * scale if len(name) < 12 else 140 * scale)) if font_path else ImageFont.load_default()
        bbox = font.getbbox(name)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (width - tw) // 2
        ty = (height - th) // 2
        
        # 90s Block Shadow (ONLY THE SHADOW, NO BOX)
        draw_text = ImageDraw.Draw(img)
        # Deep, hard offset shadow
        draw_text.text((tx+10*scale, ty+10*scale), name, font=font, fill=(0,0,0,255))
        # Main white text
        draw_text.text((tx, ty), name, font=font, fill=(255, 255, 255, 255))

    img = img.resize((1280, 400), Image.Resampling.LANCZOS)
    img.save(output_path, quality=100)
    return output_path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("-o", "--output")
    parser.add_argument("-f", "--font", default="concert")
    parser.add_argument("-t", "--theme", default="laser-school")
    parser.add_argument("-p", "--pattern", default="yearbook")
    args = parser.parse_args()
    out = args.output if args.output else "banner.png"
    print(f"🎨 BrandPulse v{VERSION} // Clean Neon Grid Engine...")
    create_banner(args.name, out, None, args.theme, None, None, args.pattern, "center", args.font)
    print(f"✅ Success! {out}")

if __name__ == "__main__":
    main()
