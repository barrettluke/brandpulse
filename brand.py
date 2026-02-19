#!/usr/bin/env python3
import sys
import os
import argparse
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import random
import urllib.request
import tempfile

VERSION = "1.0.0"

# Theme Presets
THEMES = {
    "cyberpunk": ((13, 17, 23), (0, 232, 232), (232, 0, 232), "grid"),
    "matrix": ((0, 5, 0), (0, 255, 65), (0, 143, 17), "dots"),
    "sunset": ((45, 10, 50), (255, 82, 82), (255, 193, 7), "rays"),
    "forest": ((10, 30, 10), (164, 255, 150), (34, 139, 34), "hex"),
    "ocean": ((5, 20, 40), (0, 191, 255), (30, 144, 255), "grid"),
    "mono": ((10, 10, 10), (240, 240, 240), (100, 100, 100), "dots")
}

# Verified URLs
FONT_URLS = {
    "orbitron": "https://github.com/google/fonts/raw/main/ofl/orbitron/static/Orbitron-Black.ttf",
    "space": "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/static/SpaceGrotesk-Bold.ttf",
    "press-start": "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf",
    "inter": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Black.ttf"
}

SYSTEM_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
]

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def download_font(font_name):
    url = FONT_URLS.get(font_name.lower())
    if not url: return None
    target_path = os.path.join(tempfile.gettempdir(), f"bp_v4_{font_name}.ttf")
    if not os.path.exists(target_path):
        print(f"📥 Downloading font: {font_name}...")
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

def create_gradient(width, height, color1, color2):
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def draw_pattern(draw, pattern, width, height, color, alpha, scale):
    p_color = (color[0], color[1], color[2], int(255 * (alpha/100)))
    if pattern == "grid":
        spacing = 60 * scale
        for x in range(0, width, spacing):
            draw.line([(x, 0), (x, height)], fill=p_color, width=2*scale)
        for y in range(0, height, spacing):
            draw.line([(0, y), (width, y)], fill=p_color, width=2*scale)
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

def create_banner(name, output_path="banner.png", bg_path=None, theme="cyberpunk", 
                  primary=None, secondary=None, pattern=None, align="center", 
                  font_choice="orbitron", no_text=False, gradient=False,
                  alpha_pattern=30, alpha_scanlines=15, alpha_glow=25):
    # USE SCALE 4 FOR MASSIVE SOURCE RESOLUTION
    scale = 4
    width, height = 1280 * scale, 400 * scale
    
    theme_data = THEMES.get(theme.lower(), THEMES["cyberpunk"])
    theme_bg, theme_p, theme_s, theme_pattern = theme_data
    
    p_color = hex_to_rgb(primary) if primary else theme_p
    s_color = hex_to_rgb(secondary) if secondary else theme_s
    active_pattern = pattern if pattern else theme_pattern

    # 1. Background
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
    
    layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    
    # 2. Pattern (Behind the glow)
    if active_pattern != "none":
        draw_pattern(draw, active_pattern, width, height, p_color, alpha_pattern, scale)
    
    # 3. Brand Glow (Big and blurry)
    glow_p = (p_color[0], p_color[1], p_color[2], int(255 * (alpha_glow/100)))
    glow_s = (s_color[0], s_color[1], s_color[2], int(255 * (alpha_glow/100 * 0.8)))
    draw.ellipse([width//2-600*scale, height//2-400*scale, width//2+600*scale, height//2+400*scale], fill=glow_p) 
    draw.ellipse([width//5-300*scale, height//5-300*scale, width//5+300*scale, height//5+300*scale], fill=glow_s) 

    # 4. Text Handling
    if not no_text:
        font_path = download_font(font_choice)
        if font_path:
            # GIANT FONT FOR SCALE 4
            size = 120 * scale if len(name) < 12 else 90 * scale
            font = ImageFont.truetype(font_path, size)
        else:
            font = ImageFont.load_default()

        bbox = font.getbbox(name)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        padding = 100 * scale
        tx = padding if align == "left" else (width - tw - padding if align == "right" else (width - tw) // 2)
        ty = (height - th) // 2
        
        # Chromatic Aberration Offset
        offset = 3 * scale
        draw.text((tx-offset, ty), name, font=font, fill=(s_color[0], s_color[1], s_color[2], 255)) 
        draw.text((tx+offset, ty), name, font=font, fill=(p_color[0], p_color[1], p_color[2], 255)) 
        draw.text((tx, ty), name, font=font, fill=(255, 255, 255, 255)) 
    
    # 5. Scanlines (Added AFTER text for texture)
    s_alpha = int(255 * (alpha_scanlines/100))
    for y in range(0, height, 4 * scale):
        draw.line([(0, y), (width, y)], fill=(p_color[0], p_color[1], p_color[2], s_alpha), width=1*scale)

    img.paste(layer, (0,0), layer)
    
    # 6. Footer (Inter)
    footer_font_path = download_font("inter")
    if footer_font_path:
        small_font = ImageFont.truetype(footer_font_path, 22 * scale)
        sub_text = "LOCALOPS AI // UTILITY ENGINE"
        s_bbox = small_font.getbbox(sub_text)
        s_tw = s_bbox[2] - s_bbox[0]
        footer_y = height - 60 * scale
        draw.text(((width - s_tw)//2, footer_y), sub_text, font=small_font, fill=(139, 148, 158, 200))

    # FINAL HIGH QUALITY DOWNSCALE
    img = img.resize((1280, 400), Image.Resampling.LANCZOS)
    img.save(output_path, quality=100) # Max quality
    return output_path

def main():
    parser = argparse.ArgumentParser(description=f"BrandPulse v{VERSION}")
    parser.add_argument("name", help="Project name")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-f", "--font", default="orbitron", choices=FONT_URLS.keys(), help="Font")
    parser.add_argument("-t", "--theme", default="cyberpunk", choices=THEMES.keys(), help="Theme")
    parser.add_argument("-p", "--pattern", choices=["grid", "dots", "hex", "rays", "none"], help="Pattern")
    parser.add_argument("-a", "--align", default="center", choices=["left", "center", "right"], help="Align")
    parser.add_argument("-b", "--bg", help="Background path")
    parser.add_argument("--primary", help="Primary hex")
    parser.add_argument("--secondary", help="Secondary hex")
    parser.add_argument("--gradient", action="store_true", help="Enable gradient")
    parser.add_argument("--alpha-pattern", type=int, default=30, help="Pattern opacity")
    parser.add_argument("--alpha-scanlines", type=int, default=15, help="Scanline opacity")
    parser.add_argument("--alpha-glow", type=int, default=25, help="Glow opacity")
    parser.add_argument("--no-text", action="store_true", help="Skip text")
    
    args = parser.parse_args()
    output_filename = args.output if args.output else f"{args.name.lower().replace(' ', '_')}_banner.png"
    
    print(f"🎨 BrandPulse v{VERSION} // 4X Super-sampling Render...")
    create_banner(args.name, output_filename, args.bg, args.theme, 
                  args.primary, args.secondary, args.pattern, args.align, args.font, args.no_text,
                  args.gradient, args.alpha_pattern, args.alpha_scanlines, args.alpha_glow)
    print(f"✅ Success! Banner saved to: {output_filename}")

if __name__ == "__main__":
    main()
