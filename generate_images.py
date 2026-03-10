#!/usr/bin/env python3
"""Generate 7 branded LinkedIn images for XSeller.AI Week 1 campaign."""

from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# Brand colours
BLUE_START = (30, 64, 175)    # #1E40AF
BLUE_END = (15, 23, 42)       # #0F172A
PURPLE = (139, 92, 246)       # #8B5CF6
WHITE = (255, 255, 255)

# Image dimensions
WIDTH = 1200
HEIGHT = 627

# Output directory
OUTPUT_DIR = os.path.expanduser("~/Desktop/xseller-weekly-content/week1/images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Also output to repo
REPO_DIR = "/home/user/xseller-ai/xseller-agents/output/images"
os.makedirs(REPO_DIR, exist_ok=True)

def create_gradient(width, height, start_color, end_color):
    """Create a diagonal gradient image."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            # Diagonal gradient factor
            factor = (x / width * 0.6 + y / height * 0.4)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)
            pixels[x, y] = (r, g, b)
    return img

def draw_accent_elements(draw, variant=0):
    """Draw purple accent geometric elements."""
    if variant == 0:
        # Diagonal lines
        for i in range(3):
            offset = 80 + i * 40
            draw.line([(WIDTH - offset, 0), (WIDTH, offset)], fill=(*PURPLE, 80), width=2)
            draw.line([(0, HEIGHT - offset), (offset, HEIGHT)], fill=(*PURPLE, 60), width=2)
    elif variant == 1:
        # Circle accent
        draw.ellipse([WIDTH - 200, 50, WIDTH - 50, 200], outline=PURPLE, width=3)
        draw.ellipse([WIDTH - 180, 70, WIDTH - 70, 180], outline=(*PURPLE,), width=1)
    elif variant == 2:
        # Corner accents
        draw.line([(0, 0), (100, 0)], fill=PURPLE, width=4)
        draw.line([(0, 0), (0, 60)], fill=PURPLE, width=4)
        draw.line([(WIDTH, HEIGHT), (WIDTH - 100, HEIGHT)], fill=PURPLE, width=4)
        draw.line([(WIDTH, HEIGHT), (WIDTH, HEIGHT - 60)], fill=PURPLE, width=4)
    elif variant == 3:
        # Dots pattern
        for i in range(5):
            x = 50 + i * 30
            draw.ellipse([x-4, HEIGHT-80, x+4, HEIGHT-72], fill=PURPLE)
        for i in range(3):
            x = WIDTH - 150 + i * 30
            draw.ellipse([x-4, 60, x+4, 68], fill=PURPLE)
    elif variant == 4:
        # Hexagonal dots
        for i in range(4):
            x = WIDTH - 180 + i * 40
            y = 80
            draw.regular_polygon((x, y, 12), 6, fill=None, outline=PURPLE)
    elif variant == 5:
        # Timeline dots
        y = HEIGHT - 100
        for i in range(4):
            x = 100 + i * 120
            draw.ellipse([x-8, y-8, x+8, y+8], fill=PURPLE if i < 3 else WHITE)
            if i < 3:
                draw.line([(x+8, y), (x+112, y)], fill=PURPLE, width=2)
    else:
        # Minimal bar
        draw.rectangle([50, HEIGHT - 40, 200, HEIGHT - 36], fill=PURPLE)

def wrap_text(text, max_chars=35):
    """Wrap text to fit within image."""
    return textwrap.fill(text, width=max_chars)

def create_image(headline, filename, variant=0):
    """Create a branded image with headline text."""
    # Create gradient background
    img = create_gradient(WIDTH, HEIGHT, BLUE_START, BLUE_END)
    draw = ImageDraw.Draw(img)

    # Draw accent elements
    draw_accent_elements(draw, variant)

    # Draw purple accent bar at top
    draw.rectangle([0, 0, WIDTH, 5], fill=PURPLE)

    # Try to use a good font, fall back to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except OSError:
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 42)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 20)
            font_logo = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_logo = ImageFont.load_default()

    # Wrap and draw headline text
    wrapped = wrap_text(headline, max_chars=32)
    lines = wrapped.split('\n')

    # Calculate text position (centered vertically in upper 2/3)
    line_height = 55
    total_text_height = len(lines) * line_height
    start_y = (HEIGHT * 0.55 - total_text_height) / 2 + 40

    for i, line in enumerate(lines):
        y = start_y + i * line_height
        bbox = draw.textbbox((0, 0), line, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) / 2

        # Draw text shadow
        draw.text((x + 2, y + 2), line, fill=(0, 0, 0), font=font_large)
        # Draw main text
        draw.text((x, y), line, fill=WHITE, font=font_large)

    # Draw subtle divider line
    div_y = start_y + total_text_height + 30
    draw.line([(WIDTH * 0.3, div_y), (WIDTH * 0.7, div_y)], fill=PURPLE, width=2)

    # Draw "XSeller.AI" subtitle below headline
    subtitle = "AI-Powered Reception for NZ Healthcare"
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    sub_width = bbox[2] - bbox[0]
    draw.text(((WIDTH - sub_width) / 2, div_y + 15), subtitle, fill=(*WHITE,), font=font_small)

    # Draw logo "xseller.ai" bottom-right
    logo_text = "xseller.ai"
    bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    logo_width = bbox[2] - bbox[0]
    draw.text((WIDTH - logo_width - 30, HEIGHT - 45), logo_text, fill=WHITE, font=font_logo)

    # Save to both locations
    for output_dir in [OUTPUT_DIR, REPO_DIR]:
        filepath = os.path.join(output_dir, filename)
        img.save(filepath, "PNG")
        print(f"  Created: {filepath}")

# Image data: (headline, filename, variant)
images = [
    ("Every missed call has a name, a toothache, and a credit card.", "day1-mon.png", 0),
    ("Patients don't stop calling because your receptionist needs to eat.", "day2-tue.png", 1),
    ("Your competitor answers at 9pm. Do you?", "day3-wed.png", 2),
    ("A physio can't answer the phone with their hands on a patient's shoulder.", "day4-thu.png", 3),
    ("Your AI should understand ACC, not HIPAA.", "day5-fri.png", 4),
    ("What if your AI receptionist was answering calls by Friday?", "day6-sat.png", 5),
    ("You already know you are missing calls.", "day7-sun.png", 6),
]

print("Generating 7 branded LinkedIn images...")
for headline, filename, variant in images:
    print(f"\n  [{filename}]")
    create_image(headline, filename, variant)

print("\nAll 7 images generated successfully!")
