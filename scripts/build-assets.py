"""One-off asset builder for the Orange Chinese marketing site."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

ICON = ASSETS / "source-logo.png"
src = Image.open(ICON).convert("RGBA")
# In-page icon (nav, cards, CTA) — 256px is plenty for a 64px render at 3x.
src.resize((256, 256), Image.LANCZOS).save(ASSETS / "app-icon.png", optimize=True)

PAPER = (250, 246, 239)
INK = (22, 19, 14)
ORANGE = (255, 90, 0)

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SERIF = r"C:\Windows\Fonts\georgiab.ttf"
FONT_CJK = r"C:\Windows\Fonts\msyhbd.ttc"


def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], radius, fill=255)
    out = img.copy()
    out.putalpha(mask)
    return out


def compose_icon(size: int, bg, pad_ratio: float) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), bg)
    inner = int(size * (1 - pad_ratio * 2))
    art = src.resize((inner, inner), Image.LANCZOS)
    canvas.alpha_composite(art, ((size - inner) // 2, (size - inner) // 2))
    return canvas


# ---- Home-screen / manifest icons (opaque, so iOS doesn't paint transparency black)
for size in (192, 512):
    compose_icon(size, PAPER + (255,), 0.12).convert("RGB").save(ASSETS / f"icon-{size}.png", optimize=True)
compose_icon(512, INK + (255,), 0.18).convert("RGB").save(ASSETS / "icon-maskable-512.png", optimize=True)
compose_icon(180, PAPER + (255,), 0.10).convert("RGB").save(ASSETS / "apple-touch-icon.png", optimize=True)

# ---- Favicon: ink tile so the orange stays legible at 16-32px
for size in (32, 64):
    tile = compose_icon(size, INK + (255,), 0.14)
    rounded(tile, max(2, size // 5)).save(ASSETS / f"favicon-{size}.png", optimize=True)

# ---- Open Graph card 1200x630
W, H = 1200, 630
og = Image.new("RGB", (W, H), INK)
d = ImageDraw.Draw(og)

# faint technical grid
for x in range(0, W, 72):
    d.line([(x, 0), (x, H)], fill=(32, 28, 22), width=1)
for y in range(0, H, 72):
    d.line([(0, y), (W, y)], fill=(32, 28, 22), width=1)

# orange glow behind the icon
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([700, 40, 1240, 580], fill=(255, 90, 0, 92))
glow = glow.filter(ImageFilter.GaussianBlur(110))
og = Image.alpha_composite(og.convert("RGBA"), glow)

d = ImageDraw.Draw(og)

# oversized outlined hanzi, low in the corner
try:
    cjk = ImageFont.truetype(FONT_CJK, 340)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((880, 300), "学", font=cjk, fill=255)
    stroke_mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(stroke_mask).text((880, 300), "学", font=cjk, fill=0,
                                     stroke_width=2, stroke_fill=255)
    hanzi = Image.new("RGBA", (W, H), (255, 90, 0, 0))
    hanzi.putalpha(stroke_mask.point(lambda v: int(v * 0.28)))
    og = Image.alpha_composite(og, hanzi)
except OSError:
    pass

# app icon floating
icon = src.resize((250, 250), Image.LANCZOS)
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).ellipse([840, 220, 1180, 560], fill=(0, 0, 0, 120))
shadow = shadow.filter(ImageFilter.GaussianBlur(40))
og = Image.alpha_composite(og, shadow)
og.alpha_composite(icon, (900, 100))

d = ImageDraw.Draw(og)
f_eyebrow = ImageFont.truetype(FONT_BOLD, 20)
f_head = ImageFont.truetype(FONT_SERIF, 64)
f_sub = ImageFont.truetype(FONT_REG, 23)
f_chip = ImageFont.truetype(FONT_BOLD, 21)
f_small = ImageFont.truetype(FONT_REG, 19)

d.text((80, 96), "O R A N G E   C H I N E S E", font=f_eyebrow, fill=(255, 122, 47))

d.text((78, 148), "Stop juggling apps.", font=f_head, fill=PAPER)
line2 = "Start studying"
d.text((78, 224), line2, font=f_head, fill=ORANGE)
gap = 14
x = 78 + d.textlength(line2, font=f_head) + gap
d.text((x, 224), "Chinese.", font=f_head, fill=PAPER)

d.text((82, 330), "AI tutor  ·  Smart flashcards  ·  Stroke order  ·  Photo reader",
       font=f_sub, fill=(176, 166, 152))

# bottom chips
chip_y = 404
chip_h = 56
label = "Free on iOS & Android"
chip_w = 30 + 22 + 12 + d.textlength(label, font=f_chip) + 30
d.rounded_rectangle([80, chip_y, 80 + chip_w, chip_y + chip_h], radius=chip_h // 2, fill=PAPER)
d.ellipse([98, chip_y + 18, 120, chip_y + 40], fill=ORANGE)
d.text((132, chip_y + 15), label, font=f_chip, fill=INK)

x2 = 80 + chip_w + 16
label2 = "4.9 / 5 rating"
w2 = 32 + d.textlength(label2, font=f_chip) + 32
d.rounded_rectangle([x2, chip_y, x2 + w2, chip_y + chip_h], radius=chip_h // 2,
                    outline=(96, 86, 74), width=2)
d.text((x2 + 32, chip_y + 15), label2, font=f_chip, fill=PAPER)

d.text((82, 512), "orangechinese.net", font=f_small, fill=(128, 118, 104))

og.convert("RGB").save(ASSETS / "og-image.png", optimize=True)

manifest = {
    "name": "Orange Chinese",
    "short_name": "Orange",
    "description": "AI tutor, smart flashcards, stroke-order guides and a photo reader in one Chinese-learning app.",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#FAF6EF",
    "theme_color": "#16130E",
    "icons": [
        {"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "assets/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
(ROOT / "site.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

for p in sorted(ASSETS.iterdir()):
    if not p.is_file():
        continue
    im = Image.open(p)
    print(f"{p.name:26} {im.size[0]}x{im.size[1]}  {p.stat().st_size/1024:.1f} KB")
