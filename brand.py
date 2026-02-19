#!/usr/bin/env python3
import sys
import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import random

VERSION = "0.3.0"

def create_banner(name, output_path="banner.png", bg_path=None, no_text=False):
    width, height = 1280, 400
    
    # 1. Create Background
    if bg_path and os.path.exists(bg_path):
        try:
            bg_img = Image.open(bg_path).convert('RGB')
            # Center crop and resize to 1280x400
            img = ImageOps.fit(bg_img, (width, height), centering=(0.5, 0.5))
            
            # If we are drawing text, we need a dark overlay for readability
            # If no_text is true, we keep it lighter just to unify the vibe
            overlay_alpha = 160 if not no_text else 60
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, overlay_alpha))
            img.paste(overlay, (0, 0), overlay)
            print(f"📸 Using custom background: {bg_path}")
        except Exception as e:
            print(f"⚠️ Error loading background: {e}")
            img = Image.new('RGB', (width, height), color=(13, 17, 23))
    else:
        img = Image.new('RGB', (width, height), color=(13, 17, 23))
    
    draw = ImageDraw.Draw(img)
    
    # 2. Add signature "Scanline" pattern
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(20, 24, 30, 40), width=1)
        
    # 3. Add Brand Glow
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.ellipse([width//2-400, height//2-300, width//2+400, height//2+300], fill=(0, 232, 232, 25)) # Cyan
    ov_draw.ellipse([width//4-200, height//4-200, width//4+200, height//4+200], fill=(232, 0, 232, 20)) # Magenta
    img.paste(overlay, (0,0), overlay)

    # 4. Text Handling (Skip if no_text is True)
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
        
        # Apply Glitch Effect
        draw.text((tx-3, ty), name, font=font, fill=(232, 0, 232)) # Magenta
        draw.text((tx+3, ty), name, font=font, fill=(0, 232, 232)) # Cyan
        draw.text((tx, ty), name, font=font, fill=(255, 255, 255)) # White
    else:
        print("✍️ Skipping title text (already in background image).")

    # 5. Global "Branding" line (Always added to unify the repo style)
    small_font = None
    for p in font_paths:
        if os.path.exists(p):
            small_font = ImageFont.truetype(p, 16)
            break
    if small_font:
        sub_text = "LOCALOPS AI // UTILITY ENGINE"
        s_bbox = small_font.getbbox(sub_text)
        s_tw = s_bbox[2] - s_bbox[0]
        # Draw small dark bar behind footer for readability on light backgrounds
        footer_y = height - 60
        draw.rectangle([0, footer_y-5, width, height], fill=(13, 17, 23, 200))
        draw.text(((width - s_tw)//2, footer_y), sub_text, font=small_font, fill=(139, 148, 158))

    # Save
    img.save(output_path)
    return output_path

def main():
    parser = argparse.ArgumentParser(description=f"BrandPulse v{VERSION}")
    parser.add_argument("name", help="The project name (used for footer/filename)")
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument("-b", "--bg", help="Path to custom background image")
    parser.add_argument("--no-text", action="store_true", help="Skip drawing the large title text")
    
    args = parser.parse_args()
    
    output_filename = args.output if args.output else f"{args.name.lower().replace(' ', '_')}_banner.png"
    
    print(f"🎨 BrandPulse v{VERSION} // Processing: {args.name}...")
    path = create_banner(args.name, output_filename, args.bg, args.no_text)
    print(f"✅ Success! Banner saved to: {path}")

if __name__ == "__main__":
    main()
