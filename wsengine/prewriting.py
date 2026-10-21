"""Pre-writing & fine-motor series, templates A-J (default product).

Every page is a stack of short numbered exercises. All guides share one visual language:
pale thick line + dashed centre line, a GREEN start dot, small direction arrows and a red flag at the end.
Picture "rewards" (bee -> honey, rabbit -> carrot ...) come from sheet 'Words' via config.PREWRITE_CONTENT.
"""
from __future__ import annotations

import math

from . import config as cfg
from . import icons
from .database import Word
from .icons import Art
from .letters import AVAIL_W, X0
from .modules import M, W, card_box, footer, header, hx, instruction, text

TOP = cfg.CONTENT_TOP
PALE, DASH = "#E3E9F5", "#6B7280"
GREEN, RED = "#3FB984", "#FF595E"
PI = math.pi


class PrewriteCtx:
    def __init__(self, template: str, page_no: int, page_total: int, words: dict[str, Word]):
        self.template, self.page_no, self.page_total, self.words = template, page_no, page_total, words
        self.spec = cfg.PREWRITE_TEMPLATES[template]
        self.content = cfg.PREWRITE_CONTENT.get(template)

    @property
    def color(self):
        return cfg.TEMPLATE_COLORS[self.template]

    def fill(self, t):
        return t

    def w(self, key: str) -> Word:
        return self.words[key.lower()]


# ------------------------------------------------------------------ geometry (canvas coordinates, y up)
def seg(p0, p1):
    return [p0, p1]


def sine(x0, x1, yc, amp, cycles, n=90):
    return [(x0 + (x1 - x0) * i / n, yc + amp * math.sin(2 * PI * cycles * i / n)) for i in range(n + 1)]


def sine_v(xc, y0, y1, amp, cycles, n=70):
    return [(xc + amp * math.sin(2 * PI * cycles * i / n), y0 + (y1 - y0) * i / n) for i in range(n + 1)]


def zig(x0, x1, y_lo, y_hi, peaks):
    n = peaks * 2
    return [(x0 + (x1 - x0) * i / n, y_lo if i % 2 == 0 else y_hi) for i in range(n + 1)]


def zig_v(xc, y0, y1, amp, peaks):
    n = peaks * 2
    return [(xc + (amp if i % 2 else -amp) if 0 < i < n else xc, y0 + (y1 - y0) * i / n) for i in range(n + 1)]


def arc(cx, cy, rx, ry, a0, a1, n=48):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def hops(x0, x1, y0, h, k, n=20):
    """k half-circle hops from x0 to x1 (arches above y0)."""
    pts = []
    rx = (x1 - x0) / (2 * k)
    for j in range(k):
        cx = x0 + rx * (2 * j + 1)
        pts += arc(cx, y0, rx, h, 180, 0, n)
    return pts


def circle(cx, cy, r, start=90, ccw=True, n=72):
    return [(cx + r * math.cos(math.radians(start + (360 if ccw else -360) * i / n)),
             cy + r * math.sin(math.radians(start + (360 if ccw else -360) * i / n))) for i in range(n + 1)]


def spiral(cx, cy, rmax, turns, n=260):
    """From the centre outwards, counter-clockwise."""
    return [(cx + rmax * (i / n) * math.cos(math.radians(90) + 2 * PI * turns * i / n),
             cy + rmax * (i / n) * math.sin(math.radians(90) + 2 * PI * turns * i / n)) for i in range(n + 1)]


def loops(x0, x1, yc, r, k, n=220):
    """k cursive loops (prolate trochoid) from x0 to x1."""
    a = (x1 - x0 - 2 * r) / (2 * PI * k)
    pts = []
    for i in range(n + 1):
        th = 2 * PI * k * i / n
        pts.append((x0 + r + a * th - r * math.sin(th), yc - r * math.cos(th)))
    return pts


def heart(cx, cy, size, n=90):
    raw = []
    for i in range(n + 1):
        t = 2 * PI * i / n
        raw.append((16 * math.sin(t) ** 3, 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
    k = size / 34.0
    return [(cx + x * k, cy + (y - 3) * k) for x, y in raw]


def star(cx, cy, r, inner=0.42):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(90 - 36 * i)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts + [pts[0]]


def poly_closed(pts):
    return pts + [pts[0]]


def length(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def point_at(pts, frac):
    target, run = length(pts) * frac, 0.0
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        if run + d >= target and d > 0:
            t = (target - run) / d
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t), pts[i], pts[i + 1]
        run += d
    return pts[-1], pts[-2], pts[-1]


# ------------------------------------------------------------------ drawing primitives
def stroke(c, pts, color, lw, dash=None):
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.saveState()
    c.setStrokeColor(hx(color))
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)
    if dash:
        c.setDash(*dash)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def guide(c, pts, lw=10):
    stroke(c, pts, PALE, lw)
    stroke(c, pts, DASH, 1.4, (3, 3))


def road(c, pts, width=22):
    stroke(c, pts, "#9FB4D6", width + 4)
    stroke(c, pts, "#FFFFFF", width)
    stroke(c, pts, "#C9D6EA", 1.4, (5, 5))


def start_marker(c, p, color=GREEN):
    c.saveState()
    c.setFillColor(hx(color))
    c.setStrokeColor(hx("#FFFFFF"))
    c.setLineWidth(1.6)
    c.circle(p[0], p[1], 7.5, stroke=1, fill=1)
    c.setFillColor(hx("#FFFFFF"))
    t = c.beginPath()
    t.moveTo(p[0] - 2.5, p[1] - 3.6)
    t.lineTo(p[0] + 3.8, p[1])
    t.lineTo(p[0] - 2.5, p[1] + 3.6)
    t.close()
    c.drawPath(t, stroke=0, fill=1)
    c.restoreState()


def flag(c, p, color=RED):
    c.saveState()
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(1.8)
    c.line(p[0], p[1], p[0], p[1] + 17)
    c.setFillColor(hx(color))
    t = c.beginPath()
    t.moveTo(p[0], p[1] + 17)
    t.lineTo(p[0] + 11, p[1] + 13)
    t.lineTo(p[0], p[1] + 9)
    t.close()
    c.drawPath(t, stroke=1, fill=1)
    c.restoreState()


def arrow_at(c, pts, frac, color=cfg.NAVY, size=5.5):
    (x, y), a, b = point_at(pts, frac)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    c.saveState()
    c.setFillColor(hx(color))
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    t = c.beginPath()
    t.moveTo(size, 0)
    t.lineTo(-size * 0.7, size * 0.8)
    t.lineTo(-size * 0.7, -size * 0.8)
    t.close()
    c.drawPath(t, stroke=0, fill=1)
    c.restoreState()


def trace(c, pts, end="flag", arrows=(0.5,), lw=10, closed=False):
    """The standard exercise guide."""
    guide(c, pts, lw)
    for f in arrows:
        arrow_at(c, pts, f)
    start_marker(c, pts[0])
    if end == "flag" and not closed:
        flag(c, (pts[-1][0] + 2, pts[-1][1] - 2))
    elif end == "dot" and not closed:
        c.setFillColor(hx(RED))
        c.setStrokeColor(hx("#FFFFFF"))
        c.setLineWidth(1.4)
        c.circle(pts[-1][0], pts[-1][1], 5, stroke=1, fill=1)


def dots(c, pts, r=3.0):
    c.saveState()
    c.setFillColor(hx(DASH))
    for x, y in pts:
        c.circle(x, y, r, stroke=0, fill=1)
    c.restoreState()


def connect_example(c, p, q, color):
    stroke(c, [p, q], color, 3)
    dots(c, [p, q], 3.4)


def sec(c, ctx, y, n, id_t, en_t):
    c.setFillColor(hx(ctx.color))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(1.6)
    c.circle(X0 + 10, y - 10, 9, stroke=1, fill=1)
    text(c, str(n), X0 + 10, y - 14, cfg.F_BOLD, 10, "#FFFFFF", "center")
    text(c, id_t, X0 + 26, y - 8, cfg.F_BOLD, 10, cfg.NAVY, max_width=AVAIL_W - 30)
    text(c, en_t, X0 + 26, y - 19, cfg.F_IT, 8, cfg.GREY, max_width=AVAIL_W - 30)
    return y - 28


def cloud(c, x0, x1, yc):
    n = max(int((x1 - x0) / 20), 2)
    circ = [(x0 + (x1 - x0) * i / (n - 1), yc + (4 if i % 2 else -1) + (3 if i % 3 == 0 else 0), 14 + (4 if i % 2 else 0))
            for i in range(n)]
    Art(c).blob(circ, "#D6F0FF")


def pic(c, ctx, key, x, y, size):
    icons.draw_object(c, ctx.w(key).slug, x, y, size)


def pair_row(c, ctx, a: str, b: str, y_mid, path_fn, icon=36, pad=44, lw=10, arrows=(0.5,)):
    """start picture - guide path - goal picture."""
    x0, x1 = X0 + 4, X0 + AVAIL_W - 4
    pic(c, ctx, a, x0, y_mid - icon / 2, icon)
    pic(c, ctx, b, x1 - icon, y_mid - icon / 2, icon)
    trace(c, path_fn(x0 + icon + 10, x1 - icon - 18, y_mid), lw=lw, arrows=arrows)


def dot_rows_h(c, ctx, y_top, rows, row_h, color):
    for i in range(rows):
        y = y_top - 8 - i * row_h
        p, q = (X0 + 12, y), (X0 + AVAIL_W - 12, y)
        dots(c, [p, q], 3.2)
        if i == 0:
            connect_example(c, p, q, color)


# ====================================================================== A: vertical lines
def page_a(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan garis tegak dari atas ke bawah. Mulai dari titik hijau.",
                "Trace the vertical lines from top to bottom. Start at the green dot.")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Hujan turun dari awan", "Rain falls from the cloud")
    cloud(c, X0 + 24, X0 + AVAIL_W - 24, y - 20)
    for i in range(8):
        x = X0 + 30 + i * (AVAIL_W - 60) / 7
        trace(c, seg((x, y - 46), (x, y - 98)), end="dot", arrows=(0.55,))
    y -= 108
    y = sec(c, ctx, y, 2, "Pagar kayu", "A wooden fence")
    for yy in (y - 30, y - 62):
        c.setFillColor(hx("#E7C9A0"))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(1.6)
        c.roundRect(X0 + 6, yy - 7, AVAIL_W - 12, 14, 4, stroke=1, fill=1)
    for i in range(9):
        x = X0 + 28 + i * (AVAIL_W - 56) / 8
        trace(c, seg((x, y - 6), (x, y - 94)), end="dot", arrows=(0.5,), lw=9)
    y -= 108
    y = sec(c, ctx, y, 3, "Balon dengan tali", "Balloons with strings")
    for i in range(6):
        x = X0 + 45 + i * (AVAIL_W - 90) / 5
        c.setFillColor(hx(cfg.SWATCHES[i % len(cfg.SWATCHES)]))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.ellipse(x - 14, y - 36, x + 14, y - 2, stroke=1, fill=1)
        trace(c, seg((x, y - 38), (x, y - 98)), end="dot", arrows=(0.5,))
    y -= 108
    y = sec(c, ctx, y, 4, "Tarik garis tegak dari titik atas ke titik bawah", "Draw a line from each top dot to the dot below")
    xs = [X0 + 20 + i * (AVAIL_W - 40) / 9 for i in range(10)]
    dots(c, [(x, y - 8) for x in xs] + [(x, y - 82) for x in xs], 3.2)
    connect_example(c, (xs[0], y - 8), (xs[0], y - 82), ctx.color)
    footer(c, ctx)


# ====================================================================== B: horizontal lines
def page_b(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan garis datar dari kiri ke kanan. Mulai dari titik hijau.",
                "Trace the horizontal lines from left to right. Start at the green dot.")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Antar ke tujuannya", "Take each one to its goal")
    for i, (a, b) in enumerate(ctx.content):
        pair_row(c, ctx, a, b, y - 22 - i * 44, lambda xa, xb, ym: seg((xa, ym), (xb, ym)))
    y -= 4 * 44 + 6
    y = sec(c, ctx, y, 2, "Jalan lurus: tarik garis di dalam jalan", "Straight road: draw a line inside the road")
    for i in range(3):
        ym = y - 18 - i * 36
        pts = seg((X0 + 30, ym), (X0 + AVAIL_W - 36, ym))
        road(c, pts, 22)
        start_marker(c, pts[0])
        flag(c, (pts[1][0] + 2, pts[1][1] - 2))
    y -= 3 * 36 + 6
    y = sec(c, ctx, y, 3, "Tarik garis datar dari titik kiri ke titik kanan", "Draw a line from each left dot to the dot on the right")
    dot_rows_h(c, ctx, y, 5, 19, ctx.color)
    footer(c, ctx)


# ====================================================================== C: diagonal lines
def page_c(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan garis miring. Ikuti arah panah dari titik hijau.",
                "Trace the diagonal lines. Follow the arrows from the green dot.")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Perosotan ke kanan dan ke kiri", "Slides going right and left")
    for i in range(6):
        xs = X0 + 28 + i * 80
        a, b = (xs, y - 6), (xs + 50, y - 94)
        trace(c, seg(a, b) if i % 2 == 0 else seg((b[0], a[1]), (a[0], b[1])), end="dot", arrows=(0.5,))
    y -= 104
    y = sec(c, ctx, y, 2, "Atap rumah", "House roofs")
    for i in range(3):
        cx = X0 + 85 + i * 170
        c.setFillColor(hx(["#FFE0B3", "#D6F0FF", "#FFD9E6"][i]))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2.2)
        c.rect(cx - 50, y - 98, 100, 44, stroke=1, fill=1)
        c.setFillColor(hx("#C68642"))
        c.rect(cx - 9, y - 98, 18, 28, stroke=1, fill=1)
        trace(c, [(cx - 60, y - 54), (cx, y - 6), (cx + 60, y - 54)], end="dot", arrows=(0.25, 0.75))
    y -= 108
    y = sec(c, ctx, y, 3, "Tanda silang: garis 1 lalu garis 2", "Crosses: line 1 and then line 2")
    for i in range(5):
        cx = X0 + 55 + i * 100
        trace(c, seg((cx - 28, y - 8), (cx + 28, y - 92)), end="dot", arrows=(0.5,), lw=9)
        trace(c, seg((cx + 28, y - 8), (cx - 28, y - 92)), end="dot", arrows=(0.5,), lw=9)
    y -= 108
    y = sec(c, ctx, y, 4, "Tarik garis miring dari titik atas ke titik bawah", "Draw a line from each top dot to the dot below")
    xs = [X0 + 20 + i * (AVAIL_W - 90) / 8 for i in range(9)]
    dots(c, [(x, y - 8) for x in xs] + [(x + 50, y - 78) for x in xs], 3.2)
    connect_example(c, (xs[0], y - 8), (xs[0] + 50, y - 78), ctx.color)
    footer(c, ctx)


# ====================================================================== D: zigzag
def page_d(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan garis zigzag. Naik, turun, naik, turun!",
                "Trace the zigzag lines. Up, down, up, down!")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Pegunungan", "Mountains")
    for i in range(3):
        ym = y - 20 - i * 36
        trace(c, zig(X0 + 16, X0 + AVAIL_W - 26, ym - 12, ym + 12, 12), arrows=(0.3, 0.7), lw=9)
    y -= 3 * 36 + 6
    y = sec(c, ctx, y, 2, "Terbang berkelok-kelok ke tujuan", "Zigzag all the way to the goal")
    for i, (a, b) in enumerate(ctx.content):
        pair_row(c, ctx, a, b, y - 20 - i * 40, lambda xa, xb, ym: zig(xa, xb, ym - 13, ym + 13, 9), icon=34, lw=9)
    y -= 3 * 40 + 6
    y = sec(c, ctx, y, 3, "Petir dari awan", "Lightning from the clouds")
    for i in range(6):
        cx = X0 + 40 + i * 86
        trace(c, zig_v(cx, y - 6, y - 92, 13, 6), end="dot", arrows=(0.5,), lw=9)
    y -= 100
    y = sec(c, ctx, y, 4, "Hubungkan titik-titik menjadi zigzag", "Join the dots to make a zigzag")
    for r in range(2):
        ym = y - 22 - r * 30
        pts = [(X0 + 20 + i * (AVAIL_W - 40) / 13, ym - 10 if i % 2 == 0 else ym + 10) for i in range(14)]
        dots(c, pts, 3.2)
        if r == 0:
            stroke(c, pts[:4], ctx.color, 3)
    footer(c, ctx)


# ====================================================================== E: curved lines
def page_e(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan garis lengkung dengan gerakan yang halus.",
                "Trace the curved lines with a smooth movement.")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Pelangi: merah, kuning, biru", "A rainbow: red, yellow, blue")
    cx, base = X0 + AVAIL_W / 2, y - 112
    for r, col in ((104, RED), (80, "#FFB703"), (56, "#4D9DE0")):
        pts = arc(cx, base, r, r, 180, 0, 60)
        stroke(c, pts, col, 9)
        stroke(c, pts, "#FFFFFF", 1.4, (3, 3))
        arrow_at(c, pts, 0.5)
        start_marker(c, pts[0])
        flag(c, (pts[-1][0] + 2, pts[-1][1] - 2))
    cloud(c, cx - 200, cx - 140, base + 8)
    cloud(c, cx + 140, cx + 200, base + 8)
    y -= 122
    y = sec(c, ctx, y, 2, "Bola melompat ke bintang", "The ball bounces to the star")
    a, b = ctx.content[0]
    for i in range(2):
        ym = y - 28 - i * 52
        pair_row(c, ctx, a, b, ym, lambda xa, xb, yy, h=22 + 8 * i, k=5 - i: hops(xa, xb, yy - 10, h, k), icon=34,
                 arrows=(0.2, 0.7))
    y -= 2 * 52 + 6
    y = sec(c, ctx, y, 3, "Senyum dan bukit", "Smiles and hills")
    for r in range(2):
        ym = y - 6 - r * 42
        for i in range(6):
            x0 = X0 + 22 + i * 80
            pts = arc(x0 + 30, ym - 8, 30, 14, 180, 360, 30) if r == 0 else arc(x0 + 30, ym - 28, 30, 16, 180, 0, 30)
            trace(c, pts, end="dot", arrows=(0.5,), lw=8)
    y -= 2 * 42 + 8
    y = sec(c, ctx, y, 4, "Hubungkan titik-titik menjadi lengkungan", "Join the dots to make arches")
    for i in range(4):
        cx2 = X0 + 66 + i * 125
        pts = arc(cx2, y - 70, 40, 44, 180, 0, 11)
        dots(c, pts, 3.2)
        if i == 0:
            stroke(c, pts, ctx.color, 3)
    footer(c, ctx)


# ====================================================================== F: wavy lines
def page_f(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan garis gelombang. Bergelombang seperti air!",
                "Trace the wavy lines. Wavy like water!")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Ombak: besar, sedang, kecil", "Waves: big, medium, small")
    for i, (amp, cyc) in enumerate(((13, 5), (10, 8), (7, 12))):
        ym = y - 18 - i * 34
        trace(c, sine(X0 + 16, X0 + AVAIL_W - 26, ym, amp, cyc), arrows=(0.3, 0.7), lw=9)
    y -= 3 * 34 + 8
    y = sec(c, ctx, y, 2, "Berenang dan meliuk ke tujuan", "Wiggle all the way to the goal")
    for i, (a, b) in enumerate(ctx.content):
        pair_row(c, ctx, a, b, y - 22 - i * 44, lambda xa, xb, ym: sine(xa, xb, ym, 13, 6), icon=36, lw=9)
    y -= 3 * 44 + 6
    y = sec(c, ctx, y, 3, "Air mengalir ke bawah", "Water flowing down")
    for i in range(7):
        cx = X0 + 36 + i * 74
        trace(c, sine_v(cx, y - 6, y - 78, 9, 3), end="dot", arrows=(0.5,), lw=9)
    y -= 88
    y = sec(c, ctx, y, 4, "Hubungkan titik-titik menjadi gelombang", "Join the dots to make a wave")
    for r in range(3):
        ym = y - 14 - r * 22
        pts = sine(X0 + 16, X0 + AVAIL_W - 16, ym, 8, 4, 40)
        dots(c, pts[::2], 2.8)
        if r == 0:
            stroke(c, pts[:14], ctx.color, 3)
    footer(c, ctx)


# ====================================================================== G: circles and spirals
def page_g(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan lingkaran dan spiral. Berputar berlawanan arah jarum jam.",
                "Trace the circles and spirals. Turn counter-clockwise.")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Lingkaran besar sampai kecil", "Circles from big to small")
    for i, r in enumerate((38, 31, 24, 17)):
        cx = X0 + 62 + i * 128
        pts = circle(cx, y - 46, r)
        guide(c, pts, 9)
        arrow_at(c, pts[:19], 0.5)
        start_marker(c, pts[0])
    y -= 98
    y = sec(c, ctx, y, 2, "Spiral: mulai dari tengah", "Spirals: start in the middle")
    for i in range(2):
        cx = X0 + AVAIL_W / 4 + i * AVAIL_W / 2
        pts = spiral(cx, y - 62, 58, 3)
        guide(c, pts, 8)
        arrow_at(c, pts, 0.45)
        start_marker(c, pts[0])
        flag(c, (pts[-1][0] + 2, pts[-1][1] - 2))
    y -= 132
    y = sec(c, ctx, y, 3, "Lilitan seperti pegas", "Loops like a spring")
    for i in range(3):
        ym = y - 18 - i * 36
        trace(c, loops(X0 + 16, X0 + AVAIL_W - 30, ym, 14, 6), arrows=(0.25, 0.75), lw=8)
    y -= 3 * 36 + 8
    y = sec(c, ctx, y, 4, "Hubungkan titik-titik menjadi lingkaran", "Join the dots to make circles")
    for i in range(4):
        cx = X0 + 62 + i * 128
        pts = circle(cx, y - 38, 28, 90, True, 14)
        dots(c, pts[:-1], 3.0)
        if i == 0:
            stroke(c, circle(cx, y - 38, 28), ctx.color, 3)
    footer(c, ctx)


# ====================================================================== H: mixed patterns
def _period(kind):
    if kind == "square":
        return [(0, 0), (0, 1), (0.5, 1), (0.5, 0), (1, 0)]
    if kind == "saw":
        return [(0, 0), (1, 1), (1, 0)]
    if kind == "hop":
        return [(0.5 + 0.35 * math.cos(math.radians(180 - 180 * i / 14)), math.sin(math.radians(180 - 180 * i / 14))) for i in range(15)] + [(1, 0)]
    if kind == "double":
        return [(0, 0), (0.25, 1), (0.5, 0), (0.75, 1), (1, 0)]
    if kind == "wave_flat":
        return [(0.7 * i / 20, 0.5 + 0.5 * math.sin(2 * PI * i / 20)) for i in range(21)] + [(1, 0.5)]
    if kind == "tick":
        return [(0, 0), (0.15, 0), (0.15, 1), (0.15, 0), (0.55, 0), (0.55, 0.6), (0.55, 0), (1, 0)]
    raise KeyError(kind)


def _pattern(kind, x0, x1, y0, h, n):
    per = _period(kind)
    w = (x1 - x0) / n
    pts = []
    for k in range(n):
        for (u, v) in per:
            pts.append((x0 + (k + u) * w, y0 + v * h))
    return pts, len(per) * 2


def page_h(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Lihat pola di awal garis, lalu lanjutkan dengan menebalkan garis putus-putus.",
                "Look at the pattern at the start of the line, then trace the dashed line to continue it.")
    y = TOP - 40
    kinds = ["square", "saw", "hop", "double", "wave_flat", "tick"]
    for i, kind in enumerate(kinds):
        ym = y - 12 - i * 76
        pts, nper = _pattern(kind, X0 + 22, X0 + AVAIL_W - 30, ym - 40, 36, 8)
        # first two periods are the finished example, the rest is traced
        cut = len(_period(kind)) * 2
        example, rest = pts[:cut], pts[cut - 1:]
        guide(c, rest, 9)
        arrow_at(c, rest, 0.4)
        stroke(c, example, cfg.SWATCHES[(i + 4) % len(cfg.SWATCHES)], 4.5)
        start_marker(c, example[0])
        flag(c, (rest[-1][0] + 2, rest[-1][1] - 2))
        text(c, str(i + 1), X0 - 2, ym - 26, cfg.F_BOLD, 10, ctx.color, "right")
    footer(c, ctx)


# ====================================================================== I: path tracing
def _paths(ctx):
    def s_curve(x0, x1, ym, h):
        return sine(x0, x1, ym, h * 0.36, 1.5)

    def stairs(x0, x1, ym, h):
        w = x1 - x0
        lo, hi = ym - h * 0.36, ym + h * 0.36
        return [(x0, lo), (x0 + w * 0.28, lo), (x0 + w * 0.28, hi), (x0 + w * 0.62, hi), (x0 + w * 0.62, lo), (x1, lo)]

    def zigzag(x0, x1, ym, h):
        return zig(x0, x1, ym - h * 0.36, ym + h * 0.36, 4)

    def loop(x0, x1, ym, h):
        """straight - full circle - straight - full circle - straight (loop-the-loop)."""
        R, yl = h * 0.27, ym - h * 0.30
        w = x1 - x0
        pts = [(x0, yl)]
        for f in (0.30, 0.68):
            cx = x0 + w * f
            pts.append((cx - 2, yl))
            pts += [(cx + R * math.cos(math.radians(270 + 360 * i / 40)), yl + R + R * math.sin(math.radians(270 + 360 * i / 40)))
                    for i in range(41)]
        pts.append((x1, yl))
        return pts
    return [s_curve, stairs, zigzag, loop]


def page_i(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tarik garis di dalam jalan, dari titik hijau sampai tujuan.",
                "Draw a line inside the path, from the green dot to the goal.")
    y = TOP - 40
    h = 122
    for i, ((a, b), fn) in enumerate(zip(ctx.content, _paths(ctx))):
        ym = y - 12 - i * (h + 6) - h / 2
        x0, x1 = X0 + 4, X0 + AVAIL_W - 4
        pic(c, ctx, a, x0, ym - 24, 48)
        pic(c, ctx, b, x1 - 48, ym - 24, 48)
        pts = fn(x0 + 62, x1 - 62, ym, h - 20)
        road(c, pts, 24)
        arrow_at(c, pts, 0.3)
        start_marker(c, pts[0])
        flag(c, (pts[-1][0] + 2, pts[-1][1] - 2))
    footer(c, ctx)


# ====================================================================== J: basic shapes
def _shapes(cx, cy, w, h):
    r = min(w, h) / 2
    return [
        ("lingkaran", "circle", circle(cx, cy, r)),
        ("persegi", "square", poly_closed([(cx - r, cy + r), (cx + r, cy + r), (cx + r, cy - r), (cx - r, cy - r)])),
        ("segitiga", "triangle", poly_closed([(cx, cy + r), (cx + r, cy - r), (cx - r, cy - r)])),
        ("persegi panjang", "rectangle", poly_closed([(cx - w / 2, cy + r * 0.6), (cx + w / 2, cy + r * 0.6),
                                                       (cx + w / 2, cy - r * 0.6), (cx - w / 2, cy - r * 0.6)])),
        ("oval", "oval", [(cx + (w / 2) * math.cos(math.radians(90 + 360 * i / 72)), cy + r * 0.72 * math.sin(math.radians(90 + 360 * i / 72)))
                          for i in range(73)]),
        ("belah ketupat", "diamond", poly_closed([(cx, cy + r), (cx + r * 0.8, cy), (cx, cy - r), (cx - r * 0.8, cy)])),
        ("bintang", "star", star(cx, cy, r * 1.05)),
        ("hati", "heart", heart(cx, cy, r * 2)),
    ]


def page_j(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan setiap bentuk. Mulai dari titik hijau.", "Trace each shape. Start at the green dot.")
    y = TOP - 40
    y = sec(c, ctx, y, 1, "Bentuk dasar", "Basic shapes")
    cw = (AVAIL_W - 30) / 4
    for i in range(8):
        r_, k = divmod(i, 4)
        x, yy = X0 + k * (cw + 10), y - r_ * 104
        card_box(c, x, yy - 98, cw, 98, ctx.color, fill="#FFFFFF", lw=2, r=12)
        name_id, name_en, pts = _shapes(x + cw / 2, yy - 41, 54, 54)[i]
        guide(c, pts, 8)
        start_marker(c, pts[0])
        text(c, name_id, x + cw / 2, yy - 86, cfg.F_BOLD, 9.5, cfg.NAVY, "center", max_width=cw - 8)
        text(c, name_en, x + cw / 2, yy - 95, cfg.F_IT, 7.2, cfg.GREY, "center", max_width=cw - 8)
    y -= 2 * 104 + 6
    y = sec(c, ctx, y, 2, "Rumah dari bentuk dasar", "A house made of basic shapes")
    k = 1.3
    cx, base = X0 + AVAIL_W / 2 - 10, y - 236
    body = poly_closed([(cx - 90 * k, base), (cx - 90 * k, base + 100 * k), (cx + 90 * k, base + 100 * k), (cx + 90 * k, base)])
    roof = [(cx - 105 * k, base + 100 * k), (cx, base + 166 * k), (cx + 105 * k, base + 100 * k)]
    door = poly_closed([(cx - 16 * k, base + 52 * k), (cx + 16 * k, base + 52 * k), (cx + 16 * k, base), (cx - 16 * k, base)])
    win1 = poly_closed([(cx - 70 * k, base + 82 * k), (cx - 40 * k, base + 82 * k), (cx - 40 * k, base + 52 * k), (cx - 70 * k, base + 52 * k)])
    win2 = poly_closed([(cx + 40 * k, base + 82 * k), (cx + 70 * k, base + 82 * k), (cx + 70 * k, base + 52 * k), (cx + 40 * k, base + 52 * k)])
    sun = circle(cx + 190 * k, base + 150 * k, 24)
    for pts in (body, roof, door, win1, win2, sun):
        guide(c, pts, 8)
        start_marker(c, pts[0])
    footer(c, ctx)


PREWRITE_FUNCS = {"A": page_a, "B": page_b, "C": page_c, "D": page_d, "E": page_e,
                  "F": page_f, "G": page_g, "H": page_h, "I": page_i, "J": page_j}
