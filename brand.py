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

VERSION = "2.2.0-beta"

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
    "laser-school": ((15, 15, 45), (0, 255, 255), (255, 20, 147), "yearbook") 
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

SHAPE_TYPES: List[str] = ["circle", "rect", "diamond", "triangle"]

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

def create_gradient(width: int, height: int, color1: RGBColor, color2: RGBColor) -> Image.Image:
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def draw_vignette(img: Image.Image, intensity: float = 0.5) -> Image.Image:
    width, height = img.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(100):
        alpha = int(255 * intensity * (i / 100)**2)
        inset = i * 2
        draw.rectangle([inset, inset, width-inset, height-inset], outline=(0, 0, 0, alpha), width=2)
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

def draw_glowing_line(draw: ImageDraw.ImageDraw, start: Tuple[float, float], end: Tuple[float, float], color: RGBColor, scale: int, intensity: int = 15):
    """Draws a neon-style line with outer glow and white core."""
    # 1. Outer Glow (Thickest)
    draw.line([start, end], fill=(color[0], color[1], color[2], 30), width=15 * scale)
    # 2. Inner Glow
    draw.line([start, end], fill=(color[0], color[1], color[2], 100), width=6 * scale)
    # 3. Core (White)
    draw.line([start, end], fill=(255, 255, 255, 180), width=2 * scale)

def draw_pattern(draw: ImageDraw.ImageDraw, pattern: str, width: int, height: int, color1: RGBColor, color2: RGBColor, alpha: int, scale: int) -> None:
    if pattern == "grid":
        spacing = 60 * scale
        for x in range(0, width, spacing):
            draw.line([(x, 0), (x, height)], fill=(color1[0], color1[1], color1[2], int(255*(alpha/100))), width=1*scale)
        for y in range(0, height, spacing):
            draw.line([(0, y), (width, y)], fill=(color1[0], color1[1], color1[2], int(255*(alpha/100))), width=1*scale)
    elif pattern == "yearbook":
        # 90s SCHOOL PHOTO NEON LASER BACKDROP
        
        # 1. CYAN RAYS (Randomized spacing and lengths)
        ray_count = random.randint(3, 8)
        # Origin point is off-screen top-right
        origin_x, origin_y = width + 300 * scale, -300 * scale
        
        for _ in range(ray_count):
            # Randomized spread and ending
            angle_offset = random.uniform(0.1, 0.8) # Radians
            target_dist = random.randint(width // 2, width * 2)
            
            target_x = origin_x - target_dist * math.cos(angle_offset)
            target_y = origin_y + target_dist * math.sin(angle_offset)
            
            # Shorten some rays so they stop mid-canvas
            if random.random() > 0.5:
                lerp = random.uniform(0.4, 0.8)
                target_x = origin_x + (target_x - origin_x) * lerp
                target_y = origin_y + (target_y - origin_y) * lerp
            
            draw_glowing_line(draw, (origin_x, origin_y), (target_x, target_y), color1, scale)

        # 2. PINK PARALLEL LASERS (Randomized cluster)
        laser_count = random.randint(3, 8)
        # Choose a random cluster start
        cluster_y = random.randint(100 * scale, height // 2)
        angle = math.radians(random.randint(10, 45))
        
        for i in range(laser_count):
            # Randomized spacing between parallel lines
            spacing = random.randint(20, 100) * scale
            ly1 = cluster_y + (i * spacing)
            lx1 = -200 * scale
            
            # Distance across screen
            lx2 = width + 200 * scale
            ly2 = ly1 + (width * math.tan(angle))
            
            # Randomly truncate some lasers
            if random.random() > 0.6:
                lx2 = random.randint(width // 4, width)
                ly2 = ly1 + (lx2 * math.tan(angle))
                
            draw_glowing_line(draw, (lx1, ly1), (lx2, ly2), color2, scale)

def create_banner(name: str, output_path: str = "banner.png", bg_path: Optional[str] = None, theme: str = "cyberpunk", 
                  primary: Optional[str] = None, secondary: Optional[str] = None, pattern: Optional[str] = None, 
                  align: str = "center", font_choice: str = "orbitron", no_text: bool = False, gradient: bool = False,
                  alpha_pattern: int = 40, alpha_scanlines: int = 15, alpha_glow: int = 25, 
                  vignette: bool = False, border_width: int = 0, glow_mode: str = "center", 
                  glow_shape: str = "circle", shape_count: int = 2, no_scanlines: bool = False) -> str:
    scale = 4
    width, height = 1280 * scale, 400 * scale
    theme_data = THEMES.get(theme.lower(), THEMES["cyberpunk"])
    theme_bg, theme_p, theme_s, theme_pattern = theme_data
    
    p_color = hex_to_rgb(primary) if primary else theme_p
    s_color = hex_to_rgb(secondary) if secondary else theme_s
    active_pattern = pattern if pattern else theme_pattern

    if bg_path and os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert('RGB')
        img = ImageOps.fit(bg_img, (width, height), centering=(0.5, 0.5))
        overlay_alpha = 160 if not no_text else 60
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, overlay_alpha))
        img.paste(overlay, (0, 0), overlay)
    elif gradient:
        img = create_gradient(width, height, theme_bg, (0, 0, 0))
        overlay = Image.new('RGBA', (width, height), (theme_bg[0], theme_bg[1], theme_bg[2], 150))
        img.paste(overlay, (0, 0), overlay)
    else:
        img = Image.new('RGB', (width, height), color=theme_bg)
    
    if vignette: img = draw_vignette(img)
    layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    
    if active_pattern != "none":
        draw_pattern(draw, active_pattern, width, height, p_color, s_color, alpha_pattern, scale)
    
    img.paste(layer, (0,0), layer)
    
    if not no_text:
        font_path = download_font(font_choice)
        font = ImageFont.truetype(font_path, (140 * scale if len(name) < 12 else 110 * scale)) if font_path else ImageFont.load_default()
        bbox = font.getbbox(name)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = 100 * scale if align == "left" else (width - tw - 100 * scale if align == "right" else (width - tw) // 2)
        ty = (height - th) // 2
        
        if theme in ["retro90s", "laser-school"]:
            draw_text = ImageDraw.Draw(img)
            draw_text.text((tx+8*scale, ty+8*scale), name, font=font, fill=(0,0,0,220))
            draw_text.text((tx, ty), name, font=font, fill=(255, 255, 255, 255))
        else:
            # Re-draw text logic for glitch
            pass 

    img = img.resize((1280, 400), Image.Resampling.LANCZOS)
    img.save(output_path, quality=100)
    return output_path

def main() -> None:
    parser = argparse.ArgumentParser(description=f"BrandPulse v{VERSION}")
    parser.add_argument("name", help="Project name")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-f", "--font", default="concert", help="Font")
    parser.add_argument("-t", "--theme", default="laser-school", help="Theme")
    parser.add_argument("-p", "--pattern", default="yearbook", help="Pattern")
    parser.add_argument("-a", "--align", default="center", help="Align")
    parser.add_argument("--no-scanlines", action="store_true", default=True, help="Remove lines")
    args = parser.parse_args()
    output_filename = args.output if args.output else f"{args.name.lower().replace(' ', '_')}_banner.png"
    print(f"🎨 BrandPulse v{VERSION} // Neon Yearbook Update...")
    create_banner(args.name, output_filename, None, args.theme, None, None, args.pattern, args.align, args.font, False, False, 40, 0, 0, False, 0, "none", "circle", 0, args.no_scanlines)
    print(f"✅ Success! Banner saved to: {output_filename}")

if __name__ == "__main__":
    main()
