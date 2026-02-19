#!/usr/bin/env python3
import sys
import os
import argparse
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import random
import urllib.request
import tempfile

VERSION = "0.9.0"

# Theme Presets
THEMES = {
    "cyberpunk": ((13, 17, 23), (0, 232, 232), (232, 0, 232), "grid"),
    "matrix": ((0, 5, 0), (0, 255, 65), (0, 143, 17), "dots"),
    "sunset": ((45, 10, 50), (255, 82, 82), (255, 193, 7), "rays"),
    "forest": ((10, 30, 10), (164, 255, 150), (34, 139, 34), "hex"),
    "ocean": ((5, 20, 40), (0, 191, 255), (30, 144, 255), "grid"),
    "mono": ((10, 10, 10), (240, 240, 240), (100, 100, 100), "dots")
}

# Verified Direct URLs (Using Google's raw Git sources)
FONT_URLS = {
    "orbitron": "https://github.com/google/fonts/raw/main/ofl/orbitron/static/Orbitron-Black.ttf",
    "space": "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/static/SpaceGrotesk-Bold.ttf",
    "press-start": "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf",
    "inter": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Black.ttf"
}

# System font fallbacks
SYSTEM_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
]

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def download_font(font_name):
    url = FONT_URLS.get(font_name.lower())
    if not url: return None
    
    target_path = os.path.join(tempfile.gettempdir(), f"brandpulse_v3_{font_name}.ttf")
    if not os.path.exists(target_path):
        print(f"📥 Downloading font: {font_name}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                with open(target_path, 'wb') as out_file:
                    out_file.write(response.read())
        except Exception as e:
            print(f"⚠️ Cloud font failed ({e}), using system fallback.")
            for f in SYSTEM_FONTS:
                if os.path.exists(f): return f
            return None
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
        spacing = 40 * scale
        for x in range(0, width, spacing):
            draw.line([(x, 0), (x, height)], fill=p_color, width=1*scale)
        for y in range(0, height, spacing):
            draw.line([(0, y), (width, y)], fill=p_color, width=1*scale)
    elif pattern == "dots":
        spacing = 25 * scale
        for x in range(0, width, spacing):
            for y in range(0, height, spacing):
                draw.ellipse([x-1*scale, y-1*scale, x+1*scale, y+1*scale], fill=p_color)
    elif pattern == "hex":
        size = 30 * scale
        h = size * math.sqrt(3)
        for x in range(0, width + int(size), int(size * 1.5)):
            for y in range(0, height + int(h), int(h)):
                offset = (h / 2) if (x // int(size * 1.5)) % 2 else 0
                py = y + offset
                points = []
                for i in range(6):
                    angle = math.radians(i * 60)
                    points.append((x + size * math.cos(angle), py + size * math.sin(angle)))
                draw.polygon(points, outline=p_color)

def create_banner(name, output_path="banner.png", bg_path=None, theme="cyberpunk", 
                  primary=None, secondary=None, pattern=None, align="center", 
                  font_choice="orbitron", no_text=False, gradient=False,
                  alpha_pattern=30, alpha_scanlines=15, alpha_glow=25):
    # RENDER AT 3X SIZE FOR ULTRA-CRISPNESS
    scale = 3
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
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
        img.paste(overlay, (0, 0), overlay)
    else:
        img = Image.new('RGB', (width, height), color=theme_bg)
    
    layer = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    
    # 2. Pattern
    if active_pattern != "none":
        draw_pattern(draw, active_pattern, width, height, p_color, alpha_pattern, scale)
    
    # 3. Scanlines
    s_alpha = int(255 * (alpha_scanlines/100))
    for y in range(0, height, 4 * scale):
        draw.line([(0, y), (width, y)], fill=(p_color[0], p_color[1], p_color[2], s_alpha), width=1*scale)
        
    # 4. Brand Glow
    g_alpha = int(255 * (alpha_glow/100))
    draw.ellipse([width//2-400*scale, height//2-300*scale, width//2+400*scale, height//2+300*scale], fill=(p_color[0], p_color[1], p_color[2], g_alpha)) 
    draw.ellipse([width//4-200*scale, height//4-200*scale, width//4+200*scale, height//4+200*scale], fill=(s_color[0], s_color[1], s_color[2], int(g_alpha*0.8))) 

    # 5. Project Text (Scaled up for 3X)
    if not no_text:
        font_path = download_font(font_choice)
        if font_path:
            # Sizing adjusted for 3X scale
            font_size = (180 if len(name) < 15 else 140) * scale
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()

        bbox = font.getbbox(name)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        padding = 100 * scale
        tx = padding if align == "left" else (width - tw - padding if align == "right" else (width - tw) // 2)
        ty = (height - th) // 2
        
        # HD Glitch Offset
        offset = 4 * scale
        draw.text((tx-offset, ty), name, font=font, fill=(s_color[0], s_color[1], s_color[2], 255)) 
        draw.text((tx+offset, ty), name, font=font, fill=(p_color[0], p_color[1], p_color[2], 255)) 
        draw.text((tx, ty), name, font=font, fill=(255, 255, 255, 255)) 
    
    img.paste(layer, (0,0), layer)
    
    # 6. Branding Footer
    footer_font_path = download_font("inter")
    if footer_font_path:
        small_font = ImageFont.truetype(footer_font_path, 28 * scale)
        sub_text = "LOCALOPS AI // UTILITY ENGINE"
        s_bbox = small_font.getbbox(sub_text)
        s_tw = s_bbox[2] - s_bbox[0]
        footer_y = height - 100 * scale
        draw.text(((width - s_tw)//2, footer_y), sub_text, font=small_font, fill=(139, 148, 158, 255))

    # FINAL SUPER-SAMPLING (Downscale for crispness)
    img = img.resize((1280, 400), Image.Resampling.LANCZOS)
    img.save(output_path, quality=95)
    return output_path

def main():
    parser = argparse.ArgumentParser(description=f"BrandPulse v{VERSION}")
    parser.add_argument("name", help="Project name")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-f", "--font", default="orbitron", choices=FONT_URLS.keys(), help="Font choice")
    parser.add_argument("-t", "--theme", default="cyberpunk", choices=THEMES.keys(), help="Theme preset")
    parser.add_argument("-p", "--pattern", choices=["grid", "dots", "hex", "rays", "none"], help="Background pattern")
    parser.add_argument("-a", "--align", default="center", choices=["left", "center", "right"], help="Text alignment")
    parser.add_argument("-b", "--bg", help="Background image path")
    parser.add_argument("--primary", help="Primary hex color")
    parser.add_argument("--secondary", help="Secondary hex color")
    parser.add_argument("--gradient", action="store_true", help="Enable background gradient")
    parser.add_argument("--alpha-pattern", type=int, default=30, help="Pattern opacity")
    parser.add_argument("--alpha-scanlines", type=int, default=15, help="Scanline opacity")
    parser.add_argument("--alpha-glow", type=int, default=25, help="Glow opacity")
    parser.add_argument("--no-text", action="store_true", help="Skip project title text")
    
    args = parser.parse_args()
    output_filename = args.output if args.output else f"{args.name.lower().replace(' ', '_')}_banner.png"
    
    print(f"🎨 BrandPulse v{VERSION} // HD Rendering...")
    create_banner(args.name, output_filename, args.bg, args.theme, 
                  args.primary, args.secondary, args.pattern, args.align, args.font, args.no_text,
                  args.gradient, args.alpha_pattern, args.alpha_scanlines, args.alpha_glow)
    print(f"✅ Success! Banner saved to: {output_filename}")

if __name__ == "__main__":
    main()
