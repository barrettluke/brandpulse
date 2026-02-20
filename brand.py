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

VERSION = "1.9.0"

# Type Aliases for readability
RGBColor = Tuple[int, int, int]
RGBAColor = Tuple[int, int, int, int]
Coords = List[float]

# Theme Presets: (BG_Color, Primary_Color, Secondary_Color, Default_Pattern)
THEMES: Dict[str, Tuple[RGBColor, RGBColor, RGBColor, str]] = {
    "cyberpunk": ((13, 17, 23), (0, 232, 232), (232, 0, 232), "grid"),
    "matrix": ((0, 5, 0), (0, 255, 65), (0, 143, 17), "dots"),
    "sunset": ((45, 10, 50), (255, 82, 82), (255, 193, 7), "rays"),
    "forest": ((10, 30, 10), (164, 255, 150), (34, 139, 34), "hex"),
    "ocean": ((5, 20, 40), (0, 191, 255), (30, 144, 255), "waves"),
    "mono": ((10, 10, 10), (240, 240, 240), (100, 100, 100), "dots")
}

# Verified URLs
FONT_URLS: Dict[str, str] = {
    "orbitron": "https://github.com/google/fonts/raw/main/ofl/orbitron/static/Orbitron-Black.ttf",
    "space": "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/static/SpaceGrotesk-Bold.ttf",
    "press-start": "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf",
    "inter": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Black.ttf"
}

SYSTEM_FONTS: List[str] = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
]

SHAPE_TYPES: List[str] = ["circle", "rect", "diamond", "triangle"]

def hex_to_rgb(h: str) -> RGBColor:
    """Converts hex color string to RGB tuple."""
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join([c*2 for c in h])
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) # type: ignore

def download_font(font_name: str) -> Optional[str]:
    """Downloads a TTF font from GitHub or returns a system fallback."""
    url = FONT_URLS.get(font_name.lower())
    if not url: return None
    
    target_path = os.path.join(tempfile.gettempdir(), f"bp_v4_{font_name}.ttf")
    if not os.path.exists(target_path):
        try:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', user_agent)]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, target_path)
        except:
            for f in SYSTEM_FONTS:
                if os.path.exists(f): return f
    return target_path

def create_gradient(width: int, height: int, color1: RGBColor, color2: RGBColor) -> Image.Image:
    """Creates a vertical RGB gradient image."""
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
    """Applies a dark vignette overlay to an image."""
    width, height = img.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(100):
        alpha = int(255 * intensity * (i / 100)**2)
        inset = i * 2
        draw.rectangle([inset, inset, width-inset, height-inset], outline=(0, 0, 0, alpha), width=2)
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

def draw_shape(draw: ImageDraw.ImageDraw, shape_type: str, coords: Coords, color: RGBAColor) -> None:
    """Draws a specific geometric shape onto an ImageDraw object."""
    if shape_type == "circle":
        draw.ellipse(coords, fill=color)
    elif shape_type == "rect":
        draw.rectangle(coords, fill=color)
    elif shape_type == "diamond":
        x1, y1, x2, y2 = coords
        cx, cy = (x1+x2)/2, (y1+y2)/2
        draw.polygon([(cx, y1), (x2, cy), (cx, y2), (x1, cy)], fill=color)
    elif shape_type == "triangle":
        x1, y1, x2, y2 = coords
        draw.polygon([(x1, y2), ((x1+x2)/2, y1), (x2, y2)], fill=color)

def draw_pattern(draw: ImageDraw.ImageDraw, pattern: str, width: int, height: int, color: RGBColor, alpha: int, scale: int) -> None:
    """Renders procedural background patterns."""
    p_color: RGBAColor = (color[0], color[1], color[2], int(255 * (alpha/100)))
    if pattern == "grid":
        spacing = 60 * scale
        for x in range(0, width, spacing):
            draw.line([(x, 0), (x, height)], fill=p_color, width=1*scale)
        for y in range(0, height, spacing):
            draw.line([(0, y), (width, y)], fill=p_color, width=1*scale)
    elif pattern == "dots":
        spacing = 40 * scale
        for x in range(0, width, spacing):
            for y in range(0, height, spacing):
                draw.ellipse([x-2*scale, y-2*scale, x+2*scale, y+2*scale], fill=p_color)
    elif pattern == "hex":
        size = 40 * scale
        h = size * math.sqrt(3)
        for x in range(0, width + int(size), int(size * 1.5)):
            for y in range(0, height + int(h), int(h)):
                offset = (h / 2) if (x // int(size * 1.5)) % 2 else 0
                py = y + offset
                points = []
                for i in range(6):
                    angle = math.radians(i * 60)
                    points.append((x + size * math.cos(angle), py + size * math.sin(angle)))
                draw.polygon(points, outline=p_color, width=2*scale)
    elif pattern == "rays":
        for i in range(0, 360, 15):
            angle = math.radians(i)
            end_x = width // 2 + 3000 * math.cos(angle)
            end_y = height // 2 + 3000 * math.sin(angle)
            draw.line([(width//2, height//2), (end_x, end_y)], fill=p_color, width=3*scale)
    elif pattern == "waves":
        amplitude, wavelength = 20 * scale, 150 * scale
        for y in range(0, height + 100, 40 * scale):
            points = [(x, y + amplitude * math.sin((x / wavelength) * 2 * math.pi)) for x in range(0, width + 10, 10)]
            draw.line(points, fill=p_color, width=2*scale)
    elif pattern == "circuit":
        for _ in range(30):
            x, y = random.randint(0, width), random.randint(0, height)
            length, d = random.randint(100, 400) * scale, random.choice([(1,0), (0,1), (1,1), (-1,1)])
            draw.line([(x, y), (x + d[0]*length, y + d[1]*length)], fill=p_color, width=2*scale)
            draw.ellipse([x-4*scale, y-4*scale, x+4*scale, y+4*scale], fill=p_color)
    elif pattern == "stars":
        for _ in range(200):
            x, y = random.randint(0, width), random.randint(0, height)
            s_size = random.randint(1, 3) * scale
            draw.ellipse([x, y, x+s_size, y+s_size], fill=p_color)

def create_banner(name: str, output_path: str = "banner.png", bg_path: Optional[str] = None, theme: str = "cyberpunk", 
                  primary: Optional[str] = None, secondary: Optional[str] = None, pattern: Optional[str] = None, 
                  align: str = "center", font_choice: str = "orbitron", no_text: bool = False, gradient: bool = False,
                  alpha_pattern: int = 30, alpha_scanlines: int = 15, alpha_glow: int = 25, 
                  vignette: bool = False, border_width: int = 0, glow_mode: str = "center", 
                  glow_shape: str = "circle", shape_count: int = 2, no_scanlines: bool = False) -> str:
    """Core banner rendering engine."""
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
        img = create_gradient(width, height, theme_bg, p_color)
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 120))
        img.paste(overlay, (0, 0), overlay)
    else:
        img = Image.new('RGB', (width, height), color=theme_bg)
    
    if vignette: img = draw_vignette(img)
    layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    
    if active_pattern != "none":
        draw_pattern(draw, active_pattern, width, height, p_color, alpha_pattern, scale)
    
    if glow_mode != "none":
        g_alpha = int(255 * (alpha_glow/100))
        colors = [
            (p_color[0], p_color[1], p_color[2], g_alpha),
            (s_color[0], s_color[1], s_color[2], int(g_alpha * 0.7))
        ]
        
        for i in range(shape_count):
            cur_shape = random.choice(SHAPE_TYPES) if glow_shape == "mixed" else glow_shape
            cur_color = colors[i % 2]
            
            if glow_mode == "center":
                s_scale = 1.0 - (i * 0.2)
                sz_w, sz_h = 600 * s_scale * scale, 400 * s_scale * scale
                draw_shape(draw, cur_shape, [width//2-sz_w, height//2-sz_h, width//2+sz_w, height//2+sz_h], cur_color)
            elif glow_mode == "sides":
                side_x = -200*scale if i % 2 == 0 else width-400*scale
                draw_shape(draw, cur_shape, [side_x, -200*scale, side_x+600*scale, 600*scale], cur_color)
            elif glow_mode == "corners":
                sz = 350*scale
                coords = [-sz, -sz, sz, sz] if i % 2 == 0 else [width-sz, height-sz, width+sz, height+sz]
                draw_shape(draw, cur_shape, coords, cur_color)
            elif glow_mode == "scatter":
                sx, sy = random.randint(0, width), random.randint(0, height)
                sr = random.randint(100, 400) * scale
                draw_shape(draw, cur_shape, [sx-sr, sy-sr, sx+sr, sy+sr], cur_color)

    if not no_text:
        font_path = download_font(font_choice)
        if font_path:
            font = ImageFont.truetype(font_path, (120 * scale if len(name) < 12 else 90 * scale))
        else:
            font = ImageFont.load_default()
        bbox = font.getbbox(name)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        padding = 100 * scale
        tx = padding if align == "left" else (width - tw - padding if align == "right" else (width - tw) // 2)
        ty = (height - th) // 2
        offset = 3 * scale
        draw.text((tx-offset, ty), name, font=font, fill=(s_color[0], s_color[1], s_color[2], 255)) 
        draw.text((tx+offset, ty), name, font=font, fill=(p_color[0], p_color[1], p_color[2], 255)) 
        draw.text((tx, ty), name, font=font, fill=(255, 255, 255, 255)) 

    if not no_scanlines:
        s_alpha = int(255 * (alpha_scanlines/100))
        for y in range(0, height, 4 * scale):
            draw.line([(0, y), (width, y)], fill=(p_color[0], p_color[1], p_color[2], s_alpha), width=1*scale)
    
    if border_width > 0:
        b_px = border_width * scale
        draw.rectangle([0, 0, width, height], outline=(p_color[0], p_color[1], p_color[2], 200), width=b_px)

    img.paste(layer, (0,0), layer)
    footer_font_path = download_font("inter")
    if footer_font_path:
        small_font = ImageFont.truetype(footer_font_path, 22 * scale)
        sub_text = "LOCALOPS AI // UTILITY ENGINE"
        s_bbox = small_font.getbbox(sub_text)
        s_tw = s_bbox[2] - s_bbox[0]
        footer_y = height - 60 * scale
        draw.text(((width - s_tw)//2, footer_y), sub_text, font=small_font, fill=(139, 148, 158, 200))

    img = img.resize((1280, 400), Image.Resampling.LANCZOS)
    img.save(output_path, quality=100)
    return output_path

def main() -> None:
    parser = argparse.ArgumentParser(description=f"BrandPulse v{VERSION}")
    parser.add_argument("name", help="Project name")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-f", "--font", default="orbitron", help="Font choice")
    parser.add_argument("-t", "--theme", default="cyberpunk", help="Theme preset")
    parser.add_argument("-p", "--pattern", choices=["grid", "dots", "hex", "rays", "waves", "circuit", "stars", "none"], help="Pattern")
    parser.add_argument("-a", "--align", default="center", choices=["left", "center", "right"], help="Align")
    parser.add_argument("-b", "--bg", help="Background path")
    parser.add_argument("--primary", help="Primary hex")
    parser.add_argument("--secondary", help="Secondary hex")
    parser.add_argument("--gradient", action="store_true", help="Enable gradient")
    parser.add_argument("--vignette", action="store_true", help="Enable vignette")
    parser.add_argument("--border", type=int, default=0, help="Border width")
    parser.add_argument("--glow", default="center", choices=["center", "sides", "corners", "scatter", "none"], help="Glow style")
    parser.add_argument("--glow-shape", default="circle", choices=["circle", "rect", "diamond", "triangle", "mixed"], help="Glow shape")
    parser.add_argument("--shape-count", type=int, default=2, help="Number of shapes")
    parser.add_argument("--no-scanlines", action="store_true", help="Remove retro lines")
    parser.add_argument("--alpha-pattern", type=int, default=30, help="Pattern opacity")
    parser.add_argument("--alpha-scanlines", type=int, default=15, help="Scanline opacity")
    parser.add_argument("--alpha-glow", type=int, default=25, help="Glow opacity")
    parser.add_argument("--no-text", action="store_true", help="Skip text")
    parser.add_argument("-r", "--random", action="store_true", help="Randomize styles")
    
    args = parser.parse_args()
    
    if args.random:
        args.theme = random.choice(list(THEMES.keys()))
        args.pattern = random.choice(["grid", "dots", "hex", "rays", "waves", "circuit", "stars", "none"])
        args.font = random.choice(list(FONT_URLS.keys()))
        args.align = random.choice(["left", "center", "right"])
        args.glow = random.choice(["center", "sides", "corners", "scatter", "none"])
        args.glow_shape = random.choice(["circle", "rect", "diamond", "triangle", "mixed"])
        args.shape_count = random.randint(2, 8)
        args.no_scanlines = random.choice([True, False])
        args.gradient = random.choice([True, False])
        args.vignette = random.choice([True, False])
        args.alpha_pattern = random.randint(10, 80)
        args.alpha_scanlines = random.randint(5, 40)
        args.alpha_glow = random.randint(10, 90)

    output_filename = args.output if args.output else f"{args.name.lower().replace(' ', '_')}_banner.png"
    print(f"🎨 BrandPulse v{VERSION} // Processing...")
    create_banner(args.name, output_filename, args.bg, args.theme, 
                  args.primary, args.secondary, args.pattern, args.align, args.font, args.no_text,
                  args.gradient, args.alpha_pattern, args.alpha_scanlines, args.alpha_glow,
                  args.vignette, args.border, args.glow, args.glow_shape, args.shape_count, args.no_scanlines)
    print(f"✅ Success! Banner saved to: {output_filename}")

if __name__ == "__main__":
    main()
