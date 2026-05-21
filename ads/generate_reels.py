"""
Crousty Bowls — Instagram Reels Generator
Generates 3 MP4 videos (1080x1920, 30fps) for @croustybowls
"""

import os, math, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── Config ──────────────────────────────────────────────
W, H = 1080, 1920
FPS = 30
FONT_BOLD   = "/tmp/fonts/Anton-Regular.ttf"
FONT_SYSTEM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Brand colors
BLACK  = (10, 10, 10)
ORANGE = (247, 148, 29)
GREEN  = (140, 198, 63)
PINK   = (233, 30, 140)
BLUE   = (58, 134, 255)
WHITE  = (255, 255, 255)
DARK   = (20, 20, 20)

# ── Helpers ─────────────────────────────────────────────

def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo=0, hi=1):
    return max(lo, min(hi, v))

def progress(frame, start_f, end_f):
    if frame < start_f: return 0.0
    if frame >= end_f:  return 1.0
    return (frame - start_f) / (end_f - start_f)

def font(size, bold=True):
    try:
        return ImageFont.truetype(FONT_BOLD, size)
    except:
        return ImageFont.truetype(FONT_SYSTEM, size)

def draw_text_centered(draw, text, y, fnt, color, img_w=W, shadow=True, shadow_color=(0,0,0), shadow_offset=8):
    bbox = fnt.getbbox(text)
    tw = bbox[2] - bbox[0]
    x = (img_w - tw) // 2
    if shadow:
        draw.text((x + shadow_offset, y + shadow_offset), text, font=fnt, fill=(*shadow_color, 180))
    draw.text((x, y), text, font=fnt, fill=color)
    return tw

def draw_text_left(draw, text, x, y, fnt, color, shadow=True):
    if shadow:
        draw.text((x + 6, y + 6), text, font=fnt, fill=(0, 0, 0, 160))
    draw.text((x, y), text, font=fnt, fill=color)

def alpha_blend(base, overlay_color, alpha):
    a = clamp(alpha)
    return tuple(int(b * (1 - a) + o * a) for b, o in zip(base, overlay_color))

def add_gradient_glow(img, cx, cy, radius, color, strength=0.4):
    arr = np.array(img, dtype=np.float32)
    ys = np.arange(H)[:, None]
    xs = np.arange(W)[None, :]
    dist = np.sqrt((xs - cx)**2 + (ys - cy)**2)
    glow = np.clip(1 - dist / radius, 0, 1) ** 2 * strength
    for c, col in enumerate(color[:3]):
        arr[:, :, c] = np.clip(arr[:, :, c] + glow * col, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def draw_rounded_rect(draw, x1, y1, x2, y2, radius, fill, alpha=255):
    fill_a = (*fill[:3], alpha)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill_a)

def draw_stripe(img, y, height, color1, color2):
    draw = ImageDraw.Draw(img)
    for i in range(height):
        t = i / height
        c = tuple(int(lerp(a, b, t)) for a, b in zip(color1, color2))
        draw.line([(0, y + i), (W, y + i)], fill=c)

def add_grain(img, strength=8):
    arr = np.array(img, dtype=np.int16)
    noise = np.random.randint(-strength, strength + 1, arr.shape[:2])
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def frames_to_video(frames_dir, output_path, fps=FPS):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def save_frames(generator, frames_dir, total_frames):
    os.makedirs(frames_dir, exist_ok=True)
    for i, frame in enumerate(generator(total_frames)):
        frame = add_grain(frame, strength=6)
        frame.save(os.path.join(frames_dir, f"frame_{i:04d}.png"))
        if i % 30 == 0:
            print(f"  Frame {i}/{total_frames}")

# ══════════════════════════════════════════════════════════
# REEL 1 — Brand Reveal
# ══════════════════════════════════════════════════════════

def reel1_frames(total):
    fnt_huge  = font(260)
    fnt_large = font(180)
    fnt_med   = font(90)
    fnt_small = font(60)
    fnt_xs    = font(48)

    for f in range(total):
        img = Image.new("RGB", (W, H), BLACK)
        draw = ImageDraw.Draw(img, "RGBA")

        # Animated background glow
        t_glow = f / total
        glow_x = int(W * 0.5 + math.sin(t_glow * math.pi * 2) * 100)
        img = add_gradient_glow(img, glow_x, H * 0.3, 700, ORANGE, 0.25)
        img = add_gradient_glow(img, W - glow_x, H * 0.75, 600, GREEN, 0.18)
        draw = ImageDraw.Draw(img, "RGBA")

        # Top stripe animated
        stripe_alpha = int(clamp(progress(f, 0, 10)) * 255)
        for i in range(14):
            t = (i / 14 + f / 60) % 1.0
            c = tuple(int(lerp(a, b, t)) for a, b in zip(GREEN, ORANGE))
            draw.line([(0, i), (W, i)], fill=(*c, stripe_alpha))

        # Crown — drops in at frame 8
        p_crown = ease_out(clamp(progress(f, 8, 22)))
        crown_y = int(lerp(-120, 150, p_crown))
        crown_alpha = int(p_crown * 255)
        draw.text((W//2 - 80, crown_y), "👑", font=font(130), fill=(*GREEN, crown_alpha))

        # "CROUSTY" slides in from left
        p_cr = ease_out(clamp(progress(f, 18, 35)))
        cr_x = int(lerp(-800, 50, p_cr))
        cr_alpha = int(p_cr * 255)
        draw_text_left(draw, "CROUSTY", cr_x, 380, fnt_large, (*WHITE, cr_alpha))

        # "BOWLS" slides in from right
        p_bw = ease_out(clamp(progress(f, 24, 42)))
        bw_bbox = fnt_huge.getbbox("BOWLS")
        bw_w = bw_bbox[2] - bw_bbox[0]
        bw_x = int(lerp(W + 100, 50, p_bw))
        bw_alpha = int(p_bw * 255)
        draw_text_left(draw, "BOWLS", bw_x, 540, fnt_huge, (*ORANGE, bw_alpha))

        # Green underline expands
        p_line = ease_out(clamp(progress(f, 42, 55)))
        line_w = int(p_line * 880)
        if line_w > 0:
            draw.rounded_rectangle([50, 820, 50 + line_w, 834], radius=4, fill=GREEN)

        # Tagline fades up
        p_tag = ease_out(clamp(progress(f, 50, 65)))
        tag_y = int(lerp(920, 880, p_tag))
        tag_alpha = int(p_tag * 255)
        draw_text_centered(draw, "Frais • Généreux • Minute", tag_y, fnt_small,
                           (*WHITE, tag_alpha), shadow_color=(0,0,0))

        # Bowl emoji bounces in
        p_bowl = ease_out(clamp(progress(f, 60, 78)))
        bowl_scale = lerp(0.3, 1.0, p_bowl)
        if bowl_scale > 0.1:
            bowl_size = int(220 * bowl_scale)
            try:
                bowl_fnt = font(bowl_size)
                bx = int(W//2 - bowl_size//2)
                draw.text((bx, 980), "🥣", font=bowl_fnt,
                          fill=(*WHITE, int(p_bowl * 255)))
            except:
                pass

        # Address block
        p_addr = ease_out(clamp(progress(f, 75, 90)))
        addr_y = int(lerp(1300, 1260, p_addr))
        addr_alpha = int(p_addr * 255)
        draw_rounded_rect(draw, 80, addr_y, W-80, addr_y + 100, 20, DARK, int(addr_alpha * 0.8))
        draw.text((110, addr_y + 15), "📍  Rue de Carouge 69 · 1205 Genève",
                  font=fnt_xs, fill=(*WHITE, addr_alpha))

        # Phone
        p_phone = ease_out(clamp(progress(f, 82, 96)))
        ph_alpha = int(p_phone * 255)
        draw_text_centered(draw, "022 320 47 07", 1390, fnt_xs,
                           (*GREEN, ph_alpha))

        # Dot separators
        p_dots = ease_out(clamp(progress(f, 86, 100)))
        dots_alpha = int(p_dots * 255)
        draw_text_centered(draw, "•  GENÈVE  •  PLAINPALAIS  •", 1480, fnt_xs,
                           (*WHITE, dots_alpha // 2))

        # Bottom bar
        p_bar = ease_out(clamp(progress(f, 90, 110)))
        bar_h = int(p_bar * 130)
        if bar_h > 0:
            draw.rectangle([0, H - bar_h, W, H], fill=ORANGE)
            if bar_h > 60:
                bar_alpha = int(clamp((bar_h - 60) / 70) * 255)
                draw_text_centered(draw, "@croustybowls", H - 80, fnt_small,
                                   (*BLACK, bar_alpha), shadow=False)

        # Pulsing glow on BOWLS after reveal
        if f > 50:
            pulse = math.sin(f * 0.15) * 0.5 + 0.5
            img = add_gradient_glow(img, W//2, 620, 400, ORANGE, 0.08 * pulse)
            draw = ImageDraw.Draw(img, "RGBA")

        yield img

# ══════════════════════════════════════════════════════════
# REEL 2 — 4 Bowls Menu
# ══════════════════════════════════════════════════════════

BOWLS = [
    ("CLASSIC",     "Poulet croustillant",        "Sauce thaï · Oignons crispy",   ORANGE, "🍗"),
    ("CORDON BLEU", "Cordon bleu croustillant",   "Sauce blanche · Oignons crispy", GREEN,  "🧀"),
    ("POISSON",     "Poisson croustillant",        "Sauce thaï · Persil",           PINK,   "🐟"),
    ("VEGGIE",      "Falafel maison",              "Sauce blanche · Oignons crispy", BLUE,   "🧆"),
]

def reel2_frames(total):
    fnt_title  = font(130)
    fnt_bowl   = font(78)
    fnt_name   = font(55)
    fnt_desc   = font(38)
    fnt_small  = font(52)
    fnt_xs     = font(44)
    fnt_med    = font(65)

    for f in range(total):
        img = Image.new("RGB", (W, H), BLACK)
        draw = ImageDraw.Draw(img, "RGBA")

        # Background glows
        img = add_gradient_glow(img, W*0.8, H*0.1, 600, ORANGE, 0.18)
        img = add_gradient_glow(img, W*0.2, H*0.85, 500, GREEN, 0.14)
        draw = ImageDraw.Draw(img, "RGBA")

        # Top stripe
        for i in range(14):
            t = (i / 14 + f / 80) % 1.0
            c = tuple(int(lerp(a, b, t)) for a, b in zip(GREEN, ORANGE))
            draw.line([(0, i), (W, i)], fill=c)

        # Header logo
        p_hdr = ease_out(clamp(progress(f, 0, 15)))
        hdr_alpha = int(p_hdr * 255)
        draw.text((60, 35), "👑", font=font(65), fill=(*GREEN, hdr_alpha))
        draw_text_left(draw, "CROUSTY", 140, 38, font(54), (*WHITE, hdr_alpha), shadow=False)
        draw_text_left(draw, "BOWLS",   140, 88, font(54), (*ORANGE, hdr_alpha), shadow=False)

        insta_bbox = font(38).getbbox("@croustybowls")
        iw = insta_bbox[2] - insta_bbox[0]
        draw_rounded_rect(draw, W-iw-70, 45, W-30, 115, 30, ORANGE, hdr_alpha//2)
        draw.text((W-iw-52, 55), "@croustybowls", font=font(38), fill=(*BLACK, hdr_alpha))

        # Title
        p_ttl = ease_out(clamp(progress(f, 8, 22)))
        ttl_y = int(lerp(120, 165, p_ttl))
        draw_text_centered(draw, "✦  NOS BOWLS  ✦", ttl_y, font(44),
                           (*GREEN, int(p_ttl*255)), shadow_color=(0,0,0))
        draw_text_centered(draw, "4 AU", ttl_y + 60, font(140),
                           (*WHITE, int(p_ttl*255)))
        draw_text_centered(draw, "CHOIX", ttl_y + 190, font(140),
                           (*ORANGE, int(p_ttl*255)))

        # Price badge
        p_price = ease_out(clamp(progress(f, 22, 36)))
        pr_alpha = int(p_price * 255)
        badge_w, badge_h = 560, 90
        bx = (W - badge_w) // 2
        by = 430
        pr_scale = lerp(0.5, 1.0, p_price)
        draw_rounded_rect(draw, bx, by, bx+badge_w, by+badge_h, 45,
                          ORANGE, int(pr_alpha * pr_scale))
        draw_text_centered(draw, "FORMULE  10 CHF", by + 15, font(55),
                           (*BLACK, pr_alpha), shadow=False)

        # Bowl cards (2x2 grid)
        card_w = 470
        card_h = 300
        grid_top = 555
        grid_gap = 30
        positions = [
            (50, grid_top),
            (50 + card_w + grid_gap, grid_top),
            (50, grid_top + card_h + grid_gap),
            (50 + card_w + grid_gap, grid_top + card_h + grid_gap),
        ]
        accent_colors = [ORANGE, GREEN, PINK, BLUE]

        for idx, (bowl_name, bowl_sub, bowl_sub2, bowl_color, bowl_emoji) in enumerate(BOWLS):
            start_f = 35 + idx * 10
            p_card = ease_out(clamp(progress(f, start_f, start_f + 18)))
            if p_card <= 0:
                continue
            cx, cy = positions[idx]
            card_alpha = int(p_card * 255)

            # Card background
            draw_rounded_rect(draw, cx, cy, cx+card_w, cy+card_h, 24, DARK, card_alpha)
            # Top accent border
            draw.rounded_rectangle([cx, cy, cx+card_w, cy+8], radius=4, fill=(*accent_colors[idx], card_alpha))

            # Number watermark
            num_fnt = font(160)
            num_bbox = num_fnt.getbbox(str(idx+1))
            num_w = num_bbox[2] - num_bbox[0]
            draw.text((cx + card_w - num_w - 10, cy + card_h - 130), str(idx+1),
                      font=num_fnt, fill=(*WHITE, int(card_alpha * 0.07)))

            # Emoji
            draw.text((cx + 22, cy + 18), bowl_emoji, font=font(90),
                      fill=(*WHITE, card_alpha))

            # Name
            draw_text_left(draw, bowl_name, cx + 22, cy + 128, font(52),
                          (*accent_colors[idx], card_alpha), shadow=True)
            # Desc line 1
            draw_text_left(draw, bowl_sub, cx + 22, cy + 196, font(30),
                          (*WHITE, int(card_alpha * 0.6)), shadow=False)
            # Desc line 2
            draw_text_left(draw, bowl_sub2, cx + 22, cy + 238, font(28),
                          (*WHITE, int(card_alpha * 0.4)), shadow=False)

        # Hit Tea bonus block
        p_tea = ease_out(clamp(progress(f, 70, 85)))
        tea_alpha = int(p_tea * 255)
        if tea_alpha > 0:
            tea_y = 1210
            draw_rounded_rect(draw, 50, tea_y, W-50, tea_y + 130, 28, DARK, tea_alpha)
            # Green border
            draw.rounded_rectangle([50, tea_y, W-50, tea_y+4], radius=2,
                                   fill=(*GREEN, tea_alpha))
            draw.text((80, tea_y + 22), "🧃", font=font(80), fill=(*WHITE, tea_alpha))
            draw_text_left(draw, "+ 1L HIT TEA OFFERT", 200, tea_y + 22,
                          font(60), (*GREEN, tea_alpha))
            draw_text_left(draw, "Thé froid inclus dans la formule", 200, tea_y + 84,
                          font(32), (*WHITE, int(tea_alpha * 0.5)), shadow=False)

        # Info row
        p_info = ease_out(clamp(progress(f, 80, 95)))
        info_alpha = int(p_info * 255)
        if info_alpha > 0:
            info_y = 1380
            infos = [("📍", "Rue de Carouge 69"), ("📞", "022 320 47 07"), ("⏰", "Tous les jours")]
            col_w = (W - 100) // 3
            for ii, (icon, txt) in enumerate(infos):
                ix = 50 + ii * col_w
                draw.text((ix + 10, info_y), icon, font=font(50), fill=(*WHITE, info_alpha))
                draw_text_left(draw, txt, ix + 10, info_y + 58, font(28),
                              (*WHITE, int(info_alpha * 0.6)), shadow=False)

        # Bottom bar
        p_bar = ease_out(clamp(progress(f, 88, 105)))
        bar_h2 = int(p_bar * 130)
        if bar_h2 > 0:
            draw.rectangle([0, H - bar_h2, W, H], fill=ORANGE)
            if bar_h2 > 50:
                ba = int(clamp((bar_h2-50)/80)*255)
                cx_txt = W//2
                draw_text_centered(draw, "@croustybowls", H-95, font(48),
                                   (*BLACK, ba), shadow=False)
                tag_bbox = font(36).getbbox("#teamgourmand")
                draw.text((W - (tag_bbox[2]-tag_bbox[0]) - 40, H-50),
                          "#teamgourmand", font=font(36),
                          fill=(*tuple(int(x*0.5) for x in BLACK), ba))

        yield img

# ══════════════════════════════════════════════════════════
# REEL 3 — Formule 10 CHF
# ══════════════════════════════════════════════════════════

def reel3_frames(total):
    fnt_giant = font(380)
    fnt_huge  = font(160)
    fnt_large = font(100)
    fnt_med   = font(70)
    fnt_small = font(52)
    fnt_xs    = font(42)

    for f in range(total):
        img = Image.new("RGB", (W, H), (5, 5, 5))
        draw = ImageDraw.Draw(img, "RGBA")

        # Grid background
        grid_alpha = int(clamp(progress(f, 5, 20)) * 28)
        if grid_alpha > 0:
            for gx in range(0, W, 80):
                draw.line([(gx, 0), (gx, H)], fill=(*ORANGE, grid_alpha // 3))
            for gy in range(0, H, 80):
                offset = (f * 2) % 80
                draw.line([(0, gy + offset - 80), (W, gy + offset - 80)],
                          fill=(*ORANGE, grid_alpha // 3))

        # Dynamic background glows
        pulse = math.sin(f * 0.12) * 0.5 + 0.5
        img = add_gradient_glow(img, int(W*0.8 + math.sin(f*0.05)*50), int(H*0.15), 700, ORANGE, 0.22 + pulse*0.05)
        img = add_gradient_glow(img, int(W*0.2 + math.cos(f*0.04)*40), int(H*0.8), 600, GREEN, 0.16 + pulse*0.04)
        draw = ImageDraw.Draw(img, "RGBA")

        # Flash header
        p_hdr = ease_out(clamp(progress(f, 0, 12)))
        hdr_clip = int(p_hdr * 160)
        if hdr_clip > 0:
            draw.rectangle([0, 0, W, hdr_clip], fill=ORANGE)
            if hdr_clip > 60:
                ha = int(clamp((hdr_clip - 60) / 100) * 255)
                flash_pulse = math.sin(f * 0.3) * 0.5 + 0.5
                draw_text_centered(draw, "⚡  FORMULE DU JOUR  ⚡",
                                   max(0, hdr_clip - 95), font(62),
                                   (*BLACK, ha), shadow=False)

        # Big "10"
        p_10 = ease_out(clamp(progress(f, 10, 28)))
        ten_alpha = int(p_10 * 255)
        ten_y = int(lerp(300, 220, p_10))
        # Glow effect on "10"
        if ten_alpha > 50:
            glow_str = 0.3 + pulse * 0.15
            img = add_gradient_glow(img, W//2, ten_y + 200, 450, ORANGE, glow_str)
            draw = ImageDraw.Draw(img, "RGBA")
        # Shadow layers
        for off in [12, 8, 4]:
            draw.text((W//2 - 190 + off, ten_y + off), "10", font=fnt_giant,
                     fill=(0, 0, 0, int(ten_alpha * 0.4)))
        draw.text((W//2 - 190, ten_y), "10", font=fnt_giant, fill=(*ORANGE, ten_alpha))

        # "SEULEMENT" above
        p_seu = ease_out(clamp(progress(f, 6, 20)))
        draw_text_centered(draw, "SEULEMENT", 175, font(52),
                           (*WHITE, int(p_seu * 140)))

        # "CHF" next to / below 10
        p_chf = ease_out(clamp(progress(f, 20, 34)))
        draw_text_centered(draw, "CHF", 605, fnt_huge,
                          (*WHITE, int(p_chf * 255)))

        # Tagline
        p_tag = ease_out(clamp(progress(f, 28, 42)))
        draw_text_centered(draw, "\"Le goût qui croque !\"", 740, font(44),
                           (*GREEN, int(p_tag * 255)), shadow=True)

        # Includes list
        items = [
            (ORANGE, "🥣", "1 BOWL AU CHOIX",      "Classic · Cordon Bleu · Poisson · Veggie"),
            (GREEN,  "🧃", "1L HIT TEA OFFERT",     "Thé froid inclus — au choix"),
            (PINK,   "🍕", "PAIN PIZZA MOELLEUX",   "Fait maison · Préparé à la commande"),
        ]
        list_top = 840
        for ii, (col, emo, name, detail) in enumerate(items):
            start = 40 + ii * 12
            p_item = ease_out(clamp(progress(f, start, start + 18)))
            ia = int(p_item * 255)
            if ia <= 0: continue
            iy = list_top + ii * 200
            ix = int(lerp(-600, 0, p_item))

            # Card
            draw_rounded_rect(draw, 50 + ix, iy, W-50+ix, iy + 165, 22, DARK, ia)
            draw.rounded_rectangle([50+ix, iy, 56+ix, iy+165], radius=3,
                                   fill=(*col, ia))
            draw.text((80+ix, iy + 25), emo, font=font(90), fill=(*WHITE, ia))
            draw_text_left(draw, name, 200+ix, iy + 22, font(58), (*col, ia))
            draw_text_left(draw, detail, 200+ix, iy + 94, font(32),
                          (*WHITE, int(ia * 0.5)), shadow=False)

        # Badge row
        p_badges = ease_out(clamp(progress(f, 68, 82)))
        ba = int(p_badges * 255)
        if ba > 0:
            badges = [("🏠", "FAIT MAISON"), ("🌿", "PRODUITS FRAIS"), ("⚡", "MINUTE")]
            badge_w2 = (W - 100 - 40) // 3
            badge_y = 1480
            for bi, (bico, btxt) in enumerate(badges):
                bx2 = 50 + bi * (badge_w2 + 20)
                draw_rounded_rect(draw, bx2, badge_y, bx2+badge_w2, badge_y+150, 20, DARK, ba)
                draw.text((bx2 + badge_w2//2 - 35, badge_y + 15), bico,
                          font=font(60), fill=(*WHITE, ba))
                draw_text_centered(draw, btxt, badge_y + 90, font(30),
                                   (*WHITE, int(ba * 0.7)),
                                   img_w=badge_w2, shadow=False)

        # Address / phone
        p_addr = ease_out(clamp(progress(f, 78, 92)))
        aa = int(p_addr * 255)
        if aa > 0:
            draw_text_centered(draw, "📍  Rue de Carouge 69 · 1205 Genève", 1660, font(40),
                               (*WHITE, int(aa * 0.7)))
            draw_text_centered(draw, "📞  022 320 47 07", 1714, font(48),
                               (*GREEN, aa))

        # Bottom bar
        p_bar = ease_out(clamp(progress(f, 88, 105)))
        bh = int(p_bar * 130)
        if bh > 0:
            draw.rectangle([0, H-bh, W, H], fill=ORANGE)
            if bh > 50:
                bba = int(clamp((bh-50)/80)*255)
                draw_text_centered(draw, "@croustybowls", H-95, font(50),
                                   (*BLACK, bba), shadow=False)
                tag_fnt = font(36)
                tag_b = tag_fnt.getbbox("#teamgourmand")
                draw.text((W-(tag_b[2]-tag_b[0])-35, H-50), "#teamgourmand",
                          font=tag_fnt, fill=(*tuple(int(x*0.45) for x in BLACK), bba))

        yield img

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def make_reel(name, generator_fn, seconds=14):
    total = FPS * seconds
    frames_dir = f"/tmp/crousty_{name}_frames"
    output = os.path.join(OUT_DIR, f"{name}.mp4")
    print(f"\n🎬 Generating {name} ({seconds}s, {total} frames)...")
    save_frames(generator_fn, frames_dir, total)
    print(f"  Compiling video...")
    frames_to_video(frames_dir, output)
    shutil.rmtree(frames_dir)
    size_mb = os.path.getsize(output) / 1024 / 1024
    print(f"  ✅ {output} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    print("🍽️  CROUSTY BOWLS — Instagram Reels Generator")
    print("=" * 50)
    make_reel("reel-1-brand",   reel1_frames, seconds=15)
    make_reel("reel-2-menu",    reel2_frames, seconds=15)
    make_reel("reel-3-formule", reel3_frames, seconds=15)
    print("\n✅ Tous les Reels sont générés dans le dossier ads/")
