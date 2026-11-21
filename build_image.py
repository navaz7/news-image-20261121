#!/usr/bin/env python3
"""Compose entry.png — a newspaper front page summing up 21 November 2026.

Layout: masthead + date line, a hero story with a hand-drawn map graphic,
two rows of two story panels (each with its own drawn graphic strip) and
a navy ticker band along the bottom. Every graphic is drawn with Pillow
shapes — no external images. All text is shrink-to-fit wrapped so that
nothing overflows its box.

Stories (reported 20-21 Nov 2026): Russia's 400-drone / 110-missile
barrage on Ukraine with missiles down in Poland; the AI stock rout that
put the S&P 500 in correction; the ICJ genocide ruling against Myanmar;
the UK-EU post-Brexit reset deal; Cyclone Akvan's Odisha landfall; plus
ticker briefs on Peru's quake, COP31, the Palisades verdict and the
Las Vegas Grand Prix.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width = 952

CREAM = (244, 236, 216)
NAVY = (20, 33, 61)
NAVY_LIGHT = (38, 58, 99)
CRIMSON = (179, 32, 44)
GOLD = (216, 164, 65)
PAPER_PANEL = (250, 246, 235)
SKY = (198, 219, 226)
TEAL = (23, 107, 122)
WHITE = (245, 245, 240)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_BLACK = [FONT_DIR / "DejaVuSerif-Bold.ttf"]
SERIF = [FONT_DIR / "DejaVuSerif.ttf"]
SANS_BLACK = [FONT_DIR / "DejaVuSans-Bold.ttf"]
SANS_BOLD = [FONT_DIR / "DejaVuSans-Bold.ttf"]
SANS = [FONT_DIR / "DejaVuSans.ttf"]


def font(candidates, size):
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise FileNotFoundError(candidates)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def fit_one_line(draw, s, candidates, max_w, start, minimum=12):
    """Largest font (<= start) whose single line fits max_w."""
    size = start
    while size > minimum:
        f = font(candidates, size)
        if text_w(draw, s, f) <= max_w:
            return f
        size -= 1
    return font(candidates, minimum)


def wrap(draw, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_wrapped(draw, s, candidates, max_w, max_lines, start, minimum=11):
    """Largest font whose wrapped text fits within max_lines lines."""
    size = start
    while size > minimum:
        f = font(candidates, size)
        lines = wrap(draw, s, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = font(candidates, minimum)
    return f, wrap(draw, s, f, max_w)[:max_lines]


def line_h(f, ratio=1.22):
    return int(f.size * ratio)


def draw_lines(draw, lines, f, x, y, fill, lh=None, anchor_center_x=None):
    lh = lh or line_h(f)
    for ln in lines:
        if anchor_center_x is not None:
            draw.text((anchor_center_x - text_w(draw, ln, f) / 2, y), ln, font=f, fill=fill)
        else:
            draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def draw_tracked(draw, s, f, cx, y, fill, tracking=4):
    """Draw text centered at cx with extra letter tracking."""
    widths = [text_w(draw, ch, f) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += wch + tracking
    return y + line_h(f)


def star(draw, cx, cy, r_outer, r_inner, fill, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def burst(draw, cx, cy, r, fill):
    """Jagged explosion burst."""
    pts = []
    n = 12
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(i * 180 / n + 8)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill)


# ---------------------------------------------------------------- graphics

def hero_map(draw, box):
    """Stylised map: Poland | Ukraine | Russia, missile arcs, bursts."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    # Land zones (schematic, west to east)
    pol_x1 = x + int(w * 0.30)
    ukr_x1 = x + int(w * 0.66)
    draw.rectangle([x, y, pol_x1, y + h - 1], fill=(52, 74, 112))          # Poland
    draw.rectangle([pol_x1, y, ukr_x1, y + h - 1], fill=(74, 96, 128))     # Ukraine
    draw.rectangle([ukr_x1, y, x + w - 1, y + h - 1], fill=(34, 48, 78))   # Russia
    draw.line([(pol_x1, y), (pol_x1, y + h)], fill=GOLD, width=2)
    draw.line([(ukr_x1, y), (ukr_x1, y + h)], fill=GOLD, width=2)
    lf = font(SANS_BLACK, 21)
    draw.text((x + 18, y + 12), "POLAND", font=lf, fill=WHITE)
    draw.text(((pol_x1 + ukr_x1) / 2 - text_w(draw, "UKRAINE", lf) / 2, y + 12),
              "UKRAINE", font=lf, fill=WHITE)
    draw.text((x + w - 18 - text_w(draw, "RUSSIA", lf), y + 12), "RUSSIA", font=lf, fill=WHITE)
    nf = font(SANS_BOLD, 15)
    draw.text((x + 18, y + h - 30), "NATO MEMBER", font=nf, fill=GOLD)
    # Kyiv: star + burst inside Ukraine, near its western side
    kyiv = (pol_x1 + int((ukr_x1 - pol_x1) * 0.38), y + int(h * 0.52))
    burst(draw, kyiv[0], kyiv[1], 30, CRIMSON)
    burst(draw, kyiv[0], kyiv[1], 19, GOLD)
    star(draw, kyiv[0], kyiv[1], 9, 4, WHITE)
    draw.text((kyiv[0] - 22, kyiv[1] + 34), "KYIV", font=nf, fill=WHITE)
    # Burst in Poland, close to the border
    pol_hit = (pol_x1 - 52, y + int(h * 0.40))
    burst(draw, pol_hit[0], pol_hit[1], 24, CRIMSON)
    burst(draw, pol_hit[0], pol_hit[1], 14, GOLD)
    # Missile arcs from the east (low lifts, kept inside the box)
    for (tx, ty), lift in [(kyiv, 18), (kyiv, 30), (pol_hit, 22)]:
        sx, sy = x + w - 26, y + int(h * 0.36)
        pts = []
        for t in range(21):
            u = t / 20
            px = sx + (tx - sx) * u
            py = sy + (ty - sy) * u - math.sin(u * math.pi) * lift
            pts.append((px, py))
        draw.line(pts, fill=CRIMSON, width=4)
        draw.ellipse([tx - 5, ty - 5, tx + 5, ty + 5], fill=WHITE)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def chart_graphic(draw, box):
    """Falling market line on a navy field."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    for gy in range(1, 4):
        yy = y + h * gy / 4
        draw.line([(x + 8, yy), (x + w - 8, yy)], fill=NAVY_LIGHT, width=1)
    pts = [(x + 14, y + 12), (x + w * 0.28, y + 18), (x + w * 0.48, y + h * 0.42),
           (x + w * 0.66, y + h * 0.52), (x + w * 0.86, y + h - 14)]
    draw.line(pts, fill=CRIMSON, width=5)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=GOLD)
    # Down arrow head at the end
    ex, ey = pts[-1]
    draw.polygon([(ex + 2, ey - 12), (ex + 16, ey + 2), (ex - 10, ey + 6)], fill=CRIMSON)
    tf = font(SANS_BLACK, 22)
    draw.text((x + 16, y + h - 32), "S&P 500  -3.7%", font=tf, fill=GOLD)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def court_graphic(draw, box):
    """Courthouse portico for the ICJ ruling."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=PAPER_PANEL)
    cx = x + w / 2
    top = y + 8
    draw.polygon([(cx - 92, top + 22), (cx + 92, top + 22), (cx, top)], fill=NAVY)
    draw.rectangle([cx - 100, top + 26, cx + 100, top + 32], fill=NAVY)
    for i in range(4):
        colx = cx - 78 + i * 52
        draw.rectangle([colx, top + 36, colx + 16, y + h - 20], fill=NAVY)
    draw.rectangle([cx - 104, y + h - 16, cx + 104, y + h - 8], fill=CRIMSON)
    tf = font(SANS_BLACK, 15)
    draw.text((x + 12, y + h - 34), "THE HAGUE · ICJ", font=tf, fill=CRIMSON)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def flags_graphic(draw, box):
    """UK flag (simplified) meets EU flag, gold arrow between them."""
    x, y, w, h = box
    mid = x + w // 2
    # UK half
    draw.rectangle([x, y, mid - 14, y + h - 1], fill=(30, 50, 110))
    ukw = mid - 14 - x
    draw.line([(x, y), (x + ukw, y + h)], fill=WHITE, width=7)
    draw.line([(x + ukw, y), (x, y + h)], fill=WHITE, width=7)
    draw.rectangle([x + ukw / 2 - 13, y, x + ukw / 2 + 13, y + h - 1], fill=WHITE)
    draw.rectangle([x, y + h / 2 - 13, x + ukw, y + h / 2 + 13], fill=WHITE)
    draw.rectangle([x + ukw / 2 - 7, y, x + ukw / 2 + 7, y + h - 1], fill=CRIMSON)
    draw.rectangle([x, y + h / 2 - 7, x + ukw, y + h / 2 + 7], fill=CRIMSON)
    # EU half
    draw.rectangle([mid + 14, y, x + w - 1, y + h - 1], fill=(24, 52, 130))
    ecx, ecy = mid + 14 + (x + w - mid - 14) / 2, y + h / 2
    for i in range(12):
        a = math.radians(i * 30 - 90)
        star(draw, ecx + 30 * math.cos(a), ecy + 30 * math.sin(a), 7, 3, GOLD, points=5)
    star(draw, ecx, ecy, 8, 3.5, GOLD)
    # Gold double arrow across the join
    ay = y + h / 2
    draw.line([(mid - 26, ay), (mid + 26, ay)], fill=GOLD, width=6)
    draw.polygon([(mid + 26, ay), (mid + 12, ay - 9), (mid + 12, ay + 9)], fill=GOLD)
    draw.polygon([(mid - 26, ay), (mid - 12, ay - 9), (mid - 12, ay + 9)], fill=GOLD)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


def cyclone_graphic(draw, box):
    """Cyclone spiral over a coastline."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=SKY)
    cx, cy = x + w * 0.34, y + h / 2
    for r, a0 in [(44, 20), (34, 150), (24, 280)]:
        draw.arc([cx - r, cy - r * 0.78, cx + r, cy + r * 0.78],
                 start=a0, end=a0 + 250, fill=TEAL, width=6)
    draw.ellipse([cx - 8, cy - 7, cx + 8, cy + 7], fill=NAVY)
    # Coastline + land on the right
    coast = [(x + w * 0.66, y), (x + w * 0.60, y + h * 0.35),
             (x + w * 0.68, y + h * 0.62), (x + w * 0.63, y + h - 1),
             (x + w - 1, y + h - 1), (x + w - 1, y)]
    draw.polygon(coast, fill=(214, 196, 150))
    lf = font(SANS_BLACK, 16)
    draw.text((x + w * 0.70, y + h - 30), "ODISHA COAST", font=lf, fill=NAVY)
    gf = font(SANS_BLACK, 19)
    draw.text((x + 14, y + 10), "GUSTS 90 km/h", font=gf, fill=CRIMSON)
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=2)


# ------------------------------------------------------------------- panels

def panel(draw, x, y, w, row_h, graphic, headline, sub):
    """Graphic strip on top, then headline, then a 2-line summary."""
    art_h = 68
    graphic(draw, (x, y, w, art_h))
    cy = y + art_h + 7
    hf, hlines = fit_wrapped(draw, headline, SERIF_BLACK, w, 2, 25, 17)
    cy = draw_lines(draw, hlines, hf, x, cy, NAVY, lh=line_h(hf, 1.2))
    sf, slines = fit_wrapped(draw, sub, SANS, w, 3, 16, 12)
    draw_lines(draw, slines, sf, x, cy + 2, NAVY, lh=line_h(sf, 1.18))
    return y + row_h


def main():
    page = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(page)
    cx = W // 2

    # --- Masthead -------------------------------------------------------
    draw.line([(MARGIN, 26), (W - MARGIN, 26)], fill=NAVY, width=2)
    mf = fit_one_line(draw, "THE WORLD TODAY", SERIF_BLACK, CW, 104)
    y = 36
    draw.text((cx - text_w(draw, "THE WORLD TODAY", mf) / 2, y),
              "THE WORLD TODAY", font=mf, fill=NAVY)
    y += line_h(mf, 1.04)
    draw.rectangle([MARGIN, y + 2, W - MARGIN, y + 8], fill=CRIMSON)
    y += 16

    # --- Date line ------------------------------------------------------
    df = fit_one_line(draw, "SATURDAY · 21 NOVEMBER 2026", SANS_BLACK, CW - 40, 34)
    y = draw_tracked(draw, "SATURDAY · 21 NOVEMBER 2026", df, cx, y, NAVY, tracking=3)
    draw.line([(MARGIN, y + 2), (W - MARGIN, y + 2)], fill=NAVY, width=2)
    y += 14

    # --- Hero -----------------------------------------------------------
    hero_h = 186
    hero_map(draw, (MARGIN, y, CW, hero_h))
    y += hero_h + 10
    hf = fit_one_line(draw, "MISSILES FALL IN POLAND", SERIF_BLACK, CW, 52)
    draw.text((cx - text_w(draw, "MISSILES FALL IN POLAND", hf) / 2, y),
              "MISSILES FALL IN POLAND", font=hf, fill=NAVY)
    y += line_h(hf, 1.06) + 2
    sf, slines = fit_wrapped(
        draw,
        "Russia fires 400+ drones and 110 missiles at Ukraine — at least 8 dead in Kyiv; "
        "two missiles and a drone come down on NATO soil, and Poland's PM Tusk calls it a deliberate provocation",
        SANS_BOLD, CW, 2, 23, 15)
    y = draw_lines(draw, slines, sf, 0, y, NAVY, lh=line_h(sf, 1.16), anchor_center_x=cx)
    y += 8
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=NAVY, width=2)
    y += 12

    # --- Story rows -----------------------------------------------------
    ticker_h = 106
    rows_top = y
    row_h = (H - ticker_h - rows_top - 14) // 2
    col_w = (CW - 48) // 2
    col2_x = MARGIN + col_w + 48
    div_x = MARGIN + col_w + 24

    panel(draw, MARGIN, rows_top, col_w, row_h, chart_graphic,
          "AI ROUT WIPES $4 TRILLION OFF WALL ST",
          "S&P 500 sinks 3.7% into correction and Nasdaq falls 5.3% as Anthropic's record IPO fizzles and Nvidia drops 14%")
    panel(draw, col2_x, rows_top, col_w, row_h, court_graphic,
          "MYANMAR GUILTY OF GENOCIDE",
          "World Court rules 9–6 that Myanmar committed genocide against the Rohingya — its first such verdict — and orders reparations")
    draw.line([(div_x, rows_top + 4), (div_x, rows_top + row_h - 6)], fill=NAVY, width=1)

    row2_y = rows_top + row_h + 14
    draw.line([(MARGIN, row2_y - 8), (W - MARGIN, row2_y - 8)], fill=NAVY, width=1)
    panel(draw, MARGIN, row2_y, col_w, row_h, flags_graphic,
          "UK AND EU SEAL RESET DEAL",
          "Brussels summit agrees food-trade, carbon and youth deals: 100,000 young people each way, worth 0.5% of UK GDP")
    panel(draw, col2_x, row2_y, col_w, row_h, cyclone_graphic,
          "CYCLONE AKVAN SOAKS ODISHA",
          "Storm crosses at Gopalpur then weakens: 440,000 people moved to safety, heavy rain, no major damage reported")
    draw.line([(div_x, row2_y + 4), (div_x, row2_y + row_h - 6)], fill=NAVY, width=1)

    # --- Ticker ---------------------------------------------------------
    ty = H - ticker_h
    draw.rectangle([0, ty, W, H], fill=NAVY)
    draw.rectangle([0, ty, W, ty + 5], fill=CRIMSON)
    ticker = ("IN BRIEF — Magnitude 6.7 earthquake shakes Peru's Andes, no casualties · "
              "COP31 climate talks in Antalya run overtime with no deal · "
              "Man convicted of starting California's deadly Palisades fire · "
              "Las Vegas GP: Antonelli fastest, but penalty hands Verstappen pole")
    tf, tlines = fit_wrapped(draw, ticker, SANS_BOLD, CW, 3, 20, 13)
    total_h = line_h(tf, 1.25) * len(tlines)
    draw_lines(draw, tlines, tf, MARGIN, ty + (ticker_h - total_h) // 2 + 2,
               CREAM, lh=line_h(tf, 1.25))

    page.save(OUT, optimize=True)
    size = OUT.stat().st_size
    print(f"saved {OUT} {page.size} {size} bytes")
    if size > 1024 * 1024:
        q = page.quantize(colors=256, method=Image.MEDIANCUT)
        q.save(OUT, optimize=True)
        print(f"quantized -> {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
