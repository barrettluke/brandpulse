#!/usr/bin/env python3
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

VERSION = "0.1.0"

def create_banner(name, output_path="banner.png"):
    width, height = 1280, 400
    
    # 1. Create Background (Cyberpunk Dark)
    img = Image.new('RGB', (width, height), color=(13, 17, 23)) # GitHub dark theme color
    draw = ImageDraw.Draw(img)
    
    # 2. Add subtle "Scanline" pattern
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(20, 24, 30), width=1)
        
    # 3. Add Glow/Background Gradient
    # Drawing a soft cyan/magenta radial-like glow
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.ellipse([width//2-400, height//2-300, width//2+400, height//2+300], fill=(0, 232, 232, 20)) # Cyan
    ov_draw.ellipse([width//4-200, height//4-200, width//4+200, height//4+200], fill=(232, 0, 232, 15)) # Magenta
    img.paste(overlay, (0,0), overlay)

    # 4. Text Handling
    # Use a standard system font fallback
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    font = None
    for p in font_paths:
        if os.path.exists(p):
            font = ImageFont.truetype(p, 80)
            break
    if not font:
        font = ImageFont.load_default()

    # Calculate text position
    # Fix for newer Pillow versions: use font.getbbox
    bbox = font.getbbox(name)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (width - tw) // 2, (height - th) // 2
    
    # 5. Apply "Glitch" Effect (Magenta/Cyan offsets)
    # Draw Magenta Offset
    draw.text((tx-3, ty), name, font=font, fill=(232, 0, 232))
    # Draw Cyan Offset
    draw.text((tx+3, ty), name, font=font, fill=(0, 232, 232))
    # Draw Main White Text
    draw.text((tx, ty), name, font=font, fill=(255, 255, 255))
    
    # 6. Final "Branding" line
    small_font = None
    for p in font_paths:
        if os.path.exists(p):
            small_font = ImageFont.truetype(p, 16)
            break
    if small_font:
        sub_text = "LOCALOPS AI // UTILITY ENGINE"
        s_bbox = small_font.getbbox(sub_text)
        s_tw = s_bbox[2] - s_bbox[0]
        draw.text(((width - s_tw)//2, ty + th + 40), sub_text, font=small_font, fill=(139, 148, 158))

    # Save
    img.save(output_path)
    return output_path

def main():
    if len(sys.argv) < 2:
        print(f"BrandPulse v{VERSION}")
        print("Usage: python3 brand.py \"Project Name\" [output.png]")
        return
    
    name = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "banner.png"
    
    print(f"🎨 Generating banner for: {name}...")
    path = create_banner(name, output)
    print(f"✅ Success! Banner saved to: {path}")

if __name__ == "__main__":
    main()
