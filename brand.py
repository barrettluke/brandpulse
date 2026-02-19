#!/usr/bin/env python3
import sys
import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import random

VERSION = "0.4.0"

# Theme Presets: (BG_Color, Primary_Color, Secondary_Color)
THEMES = {
    "cyberpunk": ((13, 17, 23), (0, 232, 232), (232, 0, 232)), # Cyan, Magenta
    "matrix": ((0, 5, 0), (0, 255, 65), (0, 143, 17)),        # Lime, Dark Green
    "sunset": ((45, 10, 50), (255, 82, 82), (255, 193, 7)),    # Pink-Red, Amber
    "forest": ((10, 30, 10), (164, 255, 150), (34, 139, 34)),  # Mint, Forest Green
    "ocean": ((5, 20, 40), (0, 191, 255), (30, 144, 255)),     # DeepSkyBlue, DodgerBlue
    "mono": ((10, 10, 10), (240, 240, 240), (100, 100, 100))   # White, Gray
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def create_banner(name, output_path="banner.png", bg_path=None, theme="cyberpunk", primary=None, secondary=None, no_text=False):
    width, height = 1280, 400
    
    # Load Theme
    theme_data = THEMES.get(theme.lower(), THEMES["cyberpunk"])
    bg_color, theme_p, theme_s = theme_data
    
    # Override with custom colors if provided
    p_color = hex_to_rgb(primary) if primary else theme_p
    s_color = hex_to_rgb(secondary) if secondary else theme_s

    # 1. Create Background
    if bg_path and os.path.exists(bg_path):
        try:
            bg_img = Image.open(bg_path).convert('RGB')
            img = ImageOps.fit(bg_img, (width, height), centering=(0.5, 0.5))
            overlay_alpha = 160 if not no_text else 60
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, overlay_alpha))
            img.paste(overlay, (0, 0), overlay)
        except Exception as e:
            print(f"⚠️ Error loading background: {e}")
            img = Image.new('RGB', (width, height), color=bg_color)
    else:
        img = Image.new('RGB', (width, height), color=bg_color)
    
    draw = ImageDraw.Draw(img)
    
    # 2. Add signature "Scanline" pattern
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(p_color[0], p_color[1], p_color[2], 20), width=1)
        
    # 3. Add Brand Glow (using primary/secondary colors)
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.ellipse([width//2-400, height//2-300, width//2+400, height//2+300], fill=(p_color[0], p_color[1], p_color[2], 25)) 
    ov_draw.ellipse([width//4-200, height//4-200, width//4+200, height//4+200], fill=(s_color[0], s_color[1], s_color[2], 20)) 
    img.paste(overlay, (0,0), overlay)

    # 4. Text Handling
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    
    if not no_text:
        font = None
        for p in font_paths:
            if os.path.exists(p):
                font = ImageFont.truetype(p, 100 if len(name) < 15 else 80)
                break
        if not font:
            font = ImageFont.load_default()

        bbox = font.getbbox(name)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx, ty = (width - tw) // 2, (height - th) // 2
        
        # Apply Glitch Effect (using Primary and Secondary colors)
        draw.text((tx-3, ty), name, font=font, fill=s_color) # Secondary Offset
        draw.text((tx+3, ty), name, font=font, fill=p_color) # Primary Offset
        draw.text((tx, ty), name, font=font, fill=(255, 255, 255)) # White
    
    # 5. Global "Branding" line
    small_font = None
    for p in font_paths:
        if os.path.exists(p):
            small_font = ImageFont.truetype(p, 16)
            break
    if small_font:
        sub_text = "LOCALOPS AI // UTILITY ENGINE"
        s_bbox = small_font.getbbox(sub_text)
        s_tw = s_bbox[2] - s_bbox[0]
        footer_y = height - 60
        draw.rectangle([0, footer_y-5, width, height], fill=(bg_color[0], bg_color[1], bg_color[2], 200))
        draw.text(((width - s_tw)//2, footer_y), sub_text, font=small_font, fill=(139, 148, 158))

    # Save
    img.save(output_path)
    return output_path

def main():
    parser = argparse.ArgumentParser(description=f"BrandPulse v{VERSION}")
    parser.add_argument("name", help="The project name")
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument("-b", "--bg", help="Path to custom background image")
    parser.add_argument("-t", "--theme", default="cyberpunk", choices=THEMES.keys(), help="Style theme preset")
    parser.add_argument("--primary", help="Custom primary hex color (e.g. #00FF00)")
    parser.add_argument("--secondary", help="Custom secondary hex color")
    parser.add_argument("--no-text", action="store_true", help="Skip project title text")
    
    args = parser.parse_args()
    
    output_filename = args.output if args.output else f"{args.name.lower().replace(' ', '_')}_banner.png"
    
    print(f"🎨 BrandPulse v{VERSION} // Theme: {args.theme} // Project: {args.name}...")
    path = create_banner(args.name, output_filename, args.bg, args.theme, args.primary, args.secondary, args.no_text)
    print(f"✅ Success! Banner saved to: {path}")

if __name__ == "__main__":
    main()
