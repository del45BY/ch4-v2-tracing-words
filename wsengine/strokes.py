"""Capital letters A-Z as numbered pen strokes (stroke order for 'cara menulis').

Each letter is a list of strokes; each stroke is a list of (x, y) points in a unit box
(x: 0..1 left->right, y: 0..1 bottom->top). Strokes are listed in writing order,
starting from the top, moving top->bottom and left->right as taught in preschool.
"""
import math

from reportlab.lib import colors

from . import config as cfg

hx = colors.HexColor


def arc(cx, cy, rx, ry, a0, a1, n=26):
    """Points on an ellipse arc, angles in degrees (counter-clockwise positive)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _bowl_top(x0=0.0):  # upper bowl of B / P / R
    return [(x0, 1.0), (0.5, 1.0)] + arc(0.5, 0.75, 0.45, 0.25, 90, -90) + [(x0, 0.5)]


LETTERS: dict[str, list[list[tuple[float, float]]]] = {
    "A": [[(0.5, 1), (0, 0)], [(0.5, 1), (1, 0)], [(0.2, 0.38), (0.8, 0.38)]],
    "B": [[(0, 1), (0, 0)],
          [(0, 1), (0.5, 1)] + arc(0.5, 0.75, 0.45, 0.25, 90, -90) + [(0, 0.5)],
          [(0, 0.5), (0.55, 0.5)] + arc(0.55, 0.25, 0.45, 0.25, 90, -90) + [(0, 0)]],
    "C": [arc(0.55, 0.5, 0.5, 0.5, 40, 320)],
    "D": [[(0, 1), (0, 0)], [(0, 1), (0.45, 1)] + arc(0.45, 0.5, 0.55, 0.5, 90, -90) + [(0, 0)]],
    "E": [[(0, 1), (0, 0)], [(0, 1), (0.9, 1)], [(0, 0.5), (0.75, 0.5)], [(0, 0), (0.9, 0)]],
    "F": [[(0, 1), (0, 0)], [(0, 1), (0.9, 1)], [(0, 0.5), (0.75, 0.5)]],
    "G": [arc(0.5, 0.5, 0.5, 0.5, 40, 360) + [(0.55, 0.5)]],
    "H": [[(0, 1), (0, 0)], [(1, 1), (1, 0)], [(0, 0.5), (1, 0.5)]],
    "I": [[(0.5, 1), (0.5, 0)]],
    "J": [[(0.75, 1), (0.75, 0.32)] + arc(0.4, 0.32, 0.35, 0.32, 0, -180)],
    "K": [[(0, 1), (0, 0)], [(1, 1), (0, 0.38)], [(0.3, 0.6), (1, 0)]],
    "L": [[(0, 1), (0, 0)], [(0, 0), (0.85, 0)]],
    "M": [[(0, 1), (0, 0)], [(0, 1), (0.5, 0.3), (1, 1)], [(1, 1), (1, 0)]],
    "N": [[(0, 1), (0, 0)], [(0, 1), (1, 0)], [(1, 0), (1, 1)]],
    "O": [arc(0.5, 0.5, 0.5, 0.5, 90, 450, 36)],
    "P": [[(0, 1), (0, 0)], [(0, 1), (0.55, 1)] + arc(0.55, 0.725, 0.45, 0.275, 90, -90) + [(0, 0.45)]],
    "Q": [arc(0.5, 0.5, 0.5, 0.5, 90, 450, 36), [(0.6, 0.3), (1.0, -0.05)]],
    "R": [[(0, 1), (0, 0)], [(0, 1), (0.55, 1)] + arc(0.55, 0.725, 0.45, 0.275, 90, -90) + [(0, 0.45)],
          [(0.4, 0.45), (1, 0)]],
    "S": [arc(0.5, 0.75, 0.45, 0.25, 30, 270) + arc(0.5, 0.25, 0.45, 0.25, 90, -150)],
    "T": [[(0, 1), (1, 1)], [(0.5, 1), (0.5, 0)]],
    "U": [[(0, 1), (0, 0.35)] + arc(0.5, 0.35, 0.5, 0.35, 180, 360) + [(1, 1)]],
    "V": [[(0, 1), (0.5, 0), (1, 1)]],
    "W": [[(0, 1), (0.25, 0), (0.5, 0.7), (0.75, 0), (1, 1)]],
    "X": [[(0, 1), (1, 0)], [(1, 1), (0, 0)]],
    "Y": [[(0, 1), (0.5, 0.45)], [(1, 1), (0.5, 0.45), (0.5, 0)]],
    "Z": [[(0, 1), (1, 1), (0, 0), (1, 0)]],
}
ASPECT = {"I": 0.25, "J": 0.75, "L": 0.7, "M": 1.0, "W": 1.15, "Q": 0.85}  # width / height, default 0.8


def letter_width(letter: str, h: float) -> float:
    return h * ASPECT.get(letter, 0.8)


# ------------------------------------------------------------------ small letters
# Units are "line spaces": baseline y=0, x-height (dashed middle line) y=1, ascender line y=2, descender line y=-1.
# x starts at 0 and runs in the same units. Most letters sit on 0..1; b d f h k l t reach 2; g j p q y drop to -1.
SMALL: dict[str, list[list[tuple[float, float]]]] = {
    "a": [arc(0.45, 0.5, 0.45, 0.5, 45, 405, 34), [(0.9, 1), (0.9, 0)]],
    "b": [[(0, 2), (0, 0)], arc(0.5, 0.5, 0.5, 0.5, 180, -180, 34)],
    "c": [arc(0.5, 0.5, 0.45, 0.5, 45, 315, 28)],
    "d": [arc(0.45, 0.5, 0.45, 0.5, 45, 405, 34), [(0.9, 2), (0.9, 0)]],
    "e": [[(0.025, 0.5), (0.925, 0.5)] + arc(0.475, 0.5, 0.45, 0.5, 0, 320, 30)],
    "f": [arc(0.75, 1.65, 0.35, 0.35, 70, 180, 16) + [(0.4, 0)], [(0.0, 1), (0.85, 1)]],
    "g": [arc(0.45, 0.5, 0.45, 0.5, 45, 405, 34), [(0.9, 1), (0.9, -0.35)] + arc(0.45, -0.35, 0.45, 0.4, 0, -150, 20)],
    "h": [[(0, 2), (0, 0)], arc(0.45, 0.55, 0.45, 0.45, 180, 0, 20) + [(0.9, 0)]],
    "i": [[(0.2, 1), (0.2, 0)], [(0.2, 1.5), (0.2, 1.53)]],
    "j": [[(0.5, 1), (0.5, -0.4)] + arc(0.15, -0.4, 0.35, 0.4, 0, -160, 16), [(0.5, 1.5), (0.5, 1.53)]],
    "k": [[(0, 2), (0, 0)], [(0.85, 1), (0, 0.4)], [(0.25, 0.62), (0.9, 0)]],
    "l": [[(0.15, 2), (0.15, 0)]],
    "m": [[(0, 1), (0, 0)], arc(0.35, 0.62, 0.35, 0.38, 180, 0, 16) + [(0.7, 0)],
          arc(1.05, 0.62, 0.35, 0.38, 180, 0, 16) + [(1.4, 0)]],
    "n": [[(0, 1), (0, 0)], arc(0.4, 0.62, 0.4, 0.38, 180, 0, 18) + [(0.8, 0)]],
    "o": [arc(0.5, 0.5, 0.45, 0.5, 90, 450, 36)],
    "p": [[(0, 1), (0, -1)], arc(0.5, 0.5, 0.5, 0.5, 180, -180, 34)],
    "q": [arc(0.45, 0.5, 0.45, 0.5, 45, 405, 34), [(0.9, 1), (0.9, -1)]],
    "r": [[(0, 1), (0, 0)], arc(0.5, 0.6, 0.5, 0.4, 180, 70, 16)],
    "s": [arc(0.45, 0.75, 0.4, 0.25, 30, 270, 16) + arc(0.45, 0.25, 0.4, 0.25, 90, -150, 16)],
    "t": [[(0.35, 1.6), (0.35, 0.3)] + arc(0.65, 0.3, 0.3, 0.3, 180, 270, 10), [(0.0, 1), (0.75, 1)]],
    "u": [[(0, 1), (0, 0.35)] + arc(0.4, 0.35, 0.4, 0.35, 180, 360, 18) + [(0.8, 1)], [(0.8, 1), (0.8, 0)]],
    "v": [[(0, 1), (0.45, 0), (0.9, 1)]],
    "w": [[(0, 1), (0.25, 0), (0.5, 0.65), (0.75, 0), (1, 1)]],
    "x": [[(0, 1), (0.9, 0)], [(0.9, 1), (0, 0)]],
    "y": [[(0, 1), (0.585, 0.1)], [(0.9, 1), (0.2, -1)]],
    "z": [[(0, 1), (0.9, 1), (0, 0), (0.9, 0)]],
}


def _bounds(strokes):
    xs = [p[0] for s in strokes for p in s]
    return min(xs), max(xs)


def small_width(letter: str, u: float) -> float:
    lo, hi = _bounds(SMALL[letter])
    return (hi - lo) * u


# ------------------------------------------------------------------ rendering
def _render(c, cs, mode, color, numbers, lw_solid, lw_pale, r):
    """cs = strokes already in canvas coordinates."""
    def path(s):
        p = c.beginPath()
        p.moveTo(*s[0])
        for q in s[1:]:
            p.lineTo(*q)
        return p

    c.saveState()
    c.setLineCap(1)
    c.setLineJoin(1)
    if mode == "solid":
        c.setStrokeColor(hx(color))
        c.setLineWidth(lw_solid)
        for s in cs:
            c.drawPath(path(s), stroke=1, fill=0)
    else:
        c.setStrokeColor(hx("#E3E9F5"))
        c.setLineWidth(lw_pale)
        for s in cs:
            c.drawPath(path(s), stroke=1, fill=0)
        c.setStrokeColor(hx("#7C8497"))
        c.setLineWidth(1.3)
        c.setDash(3, 3)
        for s in cs:
            c.drawPath(path(s), stroke=1, fill=0)
        c.setDash([], 0)
    if numbers:
        placed = []
        for i, s in enumerate(cs, 1):
            sx, sy = s[0]
            dx, dy = s[1][0] - s[0][0], s[1][1] - s[0][1]
            norm = max((dx * dx + dy * dy) ** 0.5, 1e-6)
            for _ in range(4):  # starts on the same spot -> slide badge along the stroke
                if any((sx - px) ** 2 + (sy - py) ** 2 < (1.7 * r) ** 2 for px, py in placed):
                    sx, sy = sx + dx / norm * 1.9 * r, sy + dy / norm * 1.9 * r
            placed.append((sx, sy))
            c.setFillColor(hx(cfg.NAVY))
            c.setStrokeColor(hx("#FFFFFF"))
            c.setLineWidth(1.4)
            c.circle(sx, sy, r, stroke=1, fill=1)
            c.setFillColor(hx("#FFFFFF"))
            c.setFont(cfg.F_BOLD, r * 1.25)
            c.drawCentredString(sx, sy - r * 0.42, str(i))
    c.restoreState()


def draw_letter(c, letter, x, y, h, mode="solid", color=cfg.NAVY, numbers=True):
    """CAPITAL letter: baseline at y, left edge at x, cap-height h. Returns width.

    mode 'solid' = thick coloured model; 'trace' = pale guide with dashed centre line.
    """
    w = letter_width(letter, h)
    cs = [[(x + px * w, y + py * h) for px, py in s] for s in LETTERS[letter]]
    _render(c, cs, mode, color, numbers, h * 0.15, h * 0.17, max(5.2, h * 0.075))
    return w


def draw_small(c, letter, x, base, u, mode="solid", color=cfg.NAVY, numbers=True):
    """SMALL letter: left edge at x, baseline at `base`, u = points per line space (x-height). Returns width."""
    lo, hi = _bounds(SMALL[letter])
    cs = [[(x + (px - lo) * u, base + py * u) for px, py in s] for s in SMALL[letter]]
    _render(c, cs, mode, color, numbers, 0.24 * u, 0.30 * u, max(5.0, 0.17 * u))
    return (hi - lo) * u
