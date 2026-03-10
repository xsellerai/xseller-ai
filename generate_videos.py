#!/usr/bin/env python3
"""Generate 7 branded MP4 videos for XSeller.AI Week 1 campaign.
Each video: 8-10 seconds, 1080x1080, animated text reveal over branded gradient.
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# Brand colours
BLUE_START = np.array([30, 64, 175])    # #1E40AF
BLUE_END = np.array([15, 23, 42])       # #0F172A
PURPLE = (139, 92, 246)                  # #8B5CF6
WHITE = (255, 255, 255)

# Video dimensions (square for social)
SIZE = 1080
FPS = 24
DURATION = 9  # seconds

# Output directories
OUTPUT_DIR = os.path.expanduser("~/Desktop/xseller-weekly-content/week1/videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

REPO_DIR = "/home/user/xseller-ai/xseller-agents/output/videos"
os.makedirs(REPO_DIR, exist_ok=True)


def get_font(size):
    """Get the best available font."""
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_gradient_frame(size):
    """Create a gradient background as numpy array."""
    img = Image.new('RGB', (size, size))
    pixels = img.load()
    for y in range(size):
        for x in range(size):
            factor = (x / size * 0.5 + y / size * 0.5)
            r = int(BLUE_START[0] + (BLUE_END[0] - BLUE_START[0]) * factor)
            g = int(BLUE_START[1] + (BLUE_END[1] - BLUE_START[1]) * factor)
            b = int(BLUE_START[2] + (BLUE_END[2] - BLUE_START[2]) * factor)
            pixels[x, y] = (r, g, b)
    return img


def create_frame(bg_img, stat_text, logo_text, progress, logo_alpha):
    """Create a single video frame with animated text.

    progress: 0.0-1.0 for text reveal animation
    logo_alpha: 0.0-1.0 for logo fade-in
    """
    import textwrap

    frame = bg_img.copy()
    draw = ImageDraw.Draw(frame)

    # Purple accent bar at top
    draw.rectangle([0, 0, SIZE, 4], fill=PURPLE)

    # Purple accent elements
    # Top-right corner accent
    draw.line([(SIZE - 120, 0), (SIZE, 0)], fill=PURPLE, width=4)
    draw.line([(SIZE - 1, 0), (SIZE - 1, 80)], fill=PURPLE, width=4)
    # Bottom-left corner accent
    draw.line([(0, SIZE - 1), (120, SIZE - 1)], fill=PURPLE, width=4)
    draw.line([(0, SIZE - 80), (0, SIZE)], fill=PURPLE, width=4)

    # Animated stat text — character-by-character reveal
    font_stat = get_font(64)
    font_logo = get_font(28)

    # Wrap text
    wrapped = textwrap.fill(stat_text, width=18)
    lines = wrapped.split('\n')

    total_chars = sum(len(line) for line in lines)
    chars_to_show = int(total_chars * progress)

    line_height = 80
    total_height = len(lines) * line_height
    start_y = (SIZE - total_height) / 2 - 40

    chars_used = 0
    for i, line in enumerate(lines):
        y = start_y + i * line_height

        # Calculate how many chars of this line to show
        remaining = chars_to_show - chars_used
        if remaining <= 0:
            break
        visible = line[:remaining]
        chars_used += len(line)

        # Center text
        bbox = draw.textbbox((0, 0), visible, font=font_stat)
        full_bbox = draw.textbbox((0, 0), line, font=font_stat)
        full_width = full_bbox[2] - full_bbox[0]
        x = (SIZE - full_width) / 2

        # Text shadow
        draw.text((x + 2, y + 2), visible, fill=(0, 0, 0), font=font_stat)
        # Main text
        draw.text((x, y), visible, fill=WHITE, font=font_stat)

    # Purple divider after text
    if progress > 0.5:
        div_width = int((progress - 0.5) * 2 * SIZE * 0.4)
        div_y = start_y + total_height + 20
        div_x = (SIZE - div_width) / 2
        draw.rectangle([div_x, div_y, div_x + div_width, div_y + 3], fill=PURPLE)

    # Logo fade-in
    if logo_alpha > 0:
        logo = "xseller.ai"
        bbox = draw.textbbox((0, 0), logo, font=font_logo)
        logo_width = bbox[2] - bbox[0]
        # Simulate alpha with colour blending
        bg_approx = BLUE_END  # approximate background at bottom-right
        alpha = logo_alpha
        color = tuple(int(WHITE[j] * alpha + bg_approx[j] * (1 - alpha)) for j in range(3))
        draw.text((SIZE - logo_width - 40, SIZE - 60), logo, fill=color, font=font_logo)

    return np.array(frame)


def generate_video(stat_text, filename):
    """Generate a single branded video."""
    from moviepy import VideoClip

    print(f"    Creating gradient background...")
    bg = create_gradient_frame(SIZE)

    total_frames = FPS * DURATION

    def make_frame(t):
        # Animation timeline:
        # 0-1s: blank (just gradient)
        # 1-6s: text reveal (character by character)
        # 6-7s: hold
        # 7-8s: logo fade in
        # 8-9s: hold everything

        if t < 1.0:
            progress = 0.0
            logo_alpha = 0.0
        elif t < 6.0:
            progress = (t - 1.0) / 5.0  # 5 seconds for full reveal
            logo_alpha = 0.0
        elif t < 7.0:
            progress = 1.0
            logo_alpha = 0.0
        elif t < 8.0:
            progress = 1.0
            logo_alpha = (t - 7.0) / 1.0
        else:
            progress = 1.0
            logo_alpha = 1.0

        return create_frame(bg, stat_text, "xseller.ai", progress, logo_alpha)

    clip = VideoClip(make_frame, duration=DURATION)

    for output_dir in [OUTPUT_DIR, REPO_DIR]:
        filepath = os.path.join(output_dir, filename)
        clip.write_videofile(
            filepath,
            fps=FPS,
            codec='libx264',
            audio=False,
            preset='ultrafast',
            logger=None
        )
        print(f"    Saved: {filepath}")

    clip.close()


# Video data: (stat_text, filename)
videos = [
    ("$150K+ lost annually to missed calls", "day1-mon.mp4"),
    ("12pm - 1pm Peak missed calls", "day2-tue.mp4"),
    ("35% of calls happen after hours", "day3-wed.mp4"),
    ("Hands-on. Phones off.", "day4-thu.mp4"),
    ("Built for NZ. Not the US.", "day5-fri.mp4"),
    ("Live in 3 days", "day6-sat.mp4"),
    ("Never miss another call", "day7-sun.mp4"),
]

print("Generating 7 branded MP4 videos (1080x1080)...\n")
for i, (stat_text, filename) in enumerate(videos, 1):
    print(f"  [{i}/7] {filename}: \"{stat_text}\"")
    generate_video(stat_text, filename)
    print()

print("All 7 videos generated successfully!")
