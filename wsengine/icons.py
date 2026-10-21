"""Cute cartoon vector art drawn in code (thick outlines, flat colours).

Artwork lookup order for a slug such as "chicken":
  1. assets/images/chicken.png          (AI / designer artwork, preferred in production)
  2. built-in vector icon below         (used for the demo and as a safe fallback)
  3. neutral placeholder tile           (QA warns so you can generate the image)

`outline=True` draws everything white with dark outlines for coloring pages.
"""
import math
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from . import config as cfg

INK = colors.HexColor(cfg.NAVY)
LW = 3.4


class Art:
    """Tiny drawing kit on a 100x100 canvas."""

    def __init__(self, c, outline=False):
        self.c, self.outline = c, outline

    def col(self, hexstr):
        return colors.white if self.outline else colors.HexColor(hexstr)

    def _style(self, fill, lw=LW):
        c = self.c
        c.setStrokeColor(INK)
        c.setLineWidth(lw)
        if fill:
            c.setFillColor(self.col(fill))
        return (1 if fill else 0)

    def ellipse(self, cx, cy, rx, ry, fill=None, lw=LW):
        f = self._style(fill, lw)
        self.c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, stroke=1, fill=f)

    def circle(self, cx, cy, r, fill=None, lw=LW):
        f = self._style(fill, lw)
        self.c.circle(cx, cy, r, stroke=1, fill=f)

    def rrect(self, x, y, w, h, r, fill=None, lw=LW):
        f = self._style(fill, lw)
        self.c.roundRect(x, y, w, h, r, stroke=1, fill=f)

    def poly(self, pts, fill=None, lw=LW):
        f = self._style(fill, lw)
        p = self.c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        self.c.drawPath(p, stroke=1, fill=f)

    def line(self, x1, y1, x2, y2, w=LW, color=None):
        self.c.setStrokeColor(colors.HexColor(color) if color else INK)
        self.c.setLineWidth(w)
        self.c.line(x1, y1, x2, y2)

    def bez(self, start, curves, fill=None, close=False, lw=LW):
        f = self._style(fill, lw)
        p = self.c.beginPath()
        p.moveTo(*start)
        for cv in curves:
            p.curveTo(*cv)
        if close:
            p.close()
        self.c.drawPath(p, stroke=1, fill=f if close else 0)

    def blob(self, circles, fill, lw=LW):
        """Union of circles with ONE clean outer outline (no inner lines)."""
        c = self.c
        c.setFillColor(INK)
        c.setStrokeColor(INK)
        for cx, cy, r in circles:
            c.circle(cx, cy, r + lw / 2, stroke=0, fill=1)
        c.setFillColor(self.col(fill))
        for cx, cy, r in circles:
            c.circle(cx, cy, r - lw / 2, stroke=0, fill=1)
        # fill the seams between touching circles
        for cx, cy, r in circles:
            c.circle(cx, cy, r - lw / 2 - 0.2, stroke=0, fill=1)

    def clip_ellipse(self, cx, cy, rx, ry):
        self.c.saveState()
        p = self.c.beginPath()
        p.ellipse(cx - rx, cy - ry, 2 * rx, 2 * ry)
        self.c.clipPath(p, stroke=0, fill=0)

    def clip_rrect(self, x, y, w, h, r):
        self.c.saveState()
        p = self.c.beginPath()
        p.roundRect(x, y, w, h, r)
        self.c.clipPath(p, stroke=0, fill=0)

    def clip_circle(self, cx, cy, r):
        self.clip_ellipse(cx, cy, r, r)

    def unclip(self):
        self.c.restoreState()

    def dot(self, x, y, r=2.8):
        self.c.setFillColor(INK)
        self.c.circle(x, y, r, stroke=0, fill=1)

    def smile(self, cx, cy, w=6):
        self.c.setStrokeColor(INK)
        self.c.setLineWidth(LW * 0.8)
        p = self.c.beginPath()
        p.moveTo(cx - w, cy)
        p.curveTo(cx - w / 2, cy - w * 0.9, cx + w / 2, cy - w * 0.9, cx + w, cy)
        self.c.drawPath(p, stroke=1, fill=0)

    def face(self, cx, cy, d=8, smile=5):
        self.dot(cx - d, cy)
        self.dot(cx + d, cy)
        self.smile(cx, cy - 5, smile)
        if not self.outline:
            self.c.setFillColor(colors.HexColor("#FFB5C2"))
            self.c.circle(cx - d - 4, cy - 5, 3.2, stroke=0, fill=1)
            self.c.circle(cx + d + 4, cy - 5, 3.2, stroke=0, fill=1)


# ------------------------------------------------------------------ icons (100 x 100 box)
def chicken(a):
    a.line(42, 18, 42, 5)
    a.line(58, 18, 58, 5)
    a.line(42, 5, 34, 5)
    a.line(58, 5, 50, 5)
    a.poly([(28, 52), (8, 76), (16, 50)], "#FFD9A0")
    a.poly([(28, 44), (4, 56), (20, 34)], "#FFD9A0")
    a.ellipse(48, 40, 29, 24, "#FFE8A3")
    a.ellipse(44, 40, 14, 10, "#FFD166")
    for x, y in [(68, 81), (75, 85), (82, 80)]:
        a.circle(x, y, 5, "#FF595E")
    a.circle(74, 66, 14, "#FFE8A3")
    a.poly([(86, 68), (99, 63), (86, 59)], "#FF9F1C")
    a.ellipse(83, 53, 4, 6, "#FF595E")
    a.dot(78, 70, 2.8)


def egg(a):
    a.ellipse(50, 46, 26, 35, "#FFF1D6")
    a.face(50, 46, d=9, smile=6)
    if not a.outline:
        a.c.setStrokeColor(colors.white)
        a.c.setLineWidth(3)
        a.bez((35, 66), [(37, 72, 42, 76, 47, 77)])


def bee(a):
    a.line(36, 66, 28, 86)
    a.line(46, 68, 48, 88)
    a.dot(28, 86, 3.5)
    a.dot(48, 88, 3.5)
    a.ellipse(56, 76, 11, 17, "#D6F0FF")
    a.ellipse(72, 70, 11, 15, "#D6F0FF")
    a.ellipse(50, 44, 33, 25, "#FFD23F")
    a.clip_ellipse(50, 44, 33, 25)
    a.rrect(52, 15, 10, 60, 0, "#2B2D42")
    a.rrect(70, 15, 10, 60, 0, "#2B2D42")
    a.unclip()
    a.ellipse(50, 44, 33, 25, None)
    a.poly([(82, 38), (97, 44), (82, 50)], "#2B2D42")
    a.face(32, 48, d=7, smile=4)


def honey(a):
    a.rrect(18, 12, 64, 56, 12, "#FFB703")
    a.rrect(24, 66, 52, 14, 5, "#B5651D")
    a.ellipse(50, 38, 22, 17, "#FFF3D6")
    pts = [(50 + 10 * math.cos(math.radians(60 * k)), 38 + 10 * math.sin(math.radians(60 * k))) for k in range(6)]
    a.poly(pts, "#FFB703", lw=2.6)


def cow(a):
    a.poly([(33, 74), (28, 94), (44, 80)], "#F4E1B5")
    a.poly([(67, 74), (72, 94), (56, 80)], "#F4E1B5")
    a.ellipse(14, 58, 13, 8, "#FFFFFF")
    a.ellipse(86, 58, 13, 8, "#FFFFFF")
    a.ellipse(14, 58, 6, 3.5, "#FFB5C2", lw=1.5)
    a.ellipse(86, 58, 6, 3.5, "#FFB5C2", lw=1.5)
    a.rrect(20, 14, 60, 68, 24, "#FFFFFF")
    a.clip_rrect(20, 14, 60, 68, 24)
    a.ellipse(32, 72, 13, 11, "#2B2D42")
    a.ellipse(78, 62, 11, 13, "#2B2D42")
    a.unclip()
    a.rrect(20, 14, 60, 68, 24, None)
    a.ellipse(50, 33, 22, 15, "#FFB5C2")
    a.dot(42, 33, 2.8)
    a.dot(58, 33, 2.8)
    a.dot(38, 58, 3.4)
    a.dot(62, 58, 3.4)


def milk(a):
    a.rrect(28, 12, 44, 56, 4, "#FFFFFF")
    a.poly([(28, 68), (37, 84), (63, 84), (72, 68)], "#E8F4FF")
    a.rrect(36, 84, 28, 7, 2, "#4CC9F0")
    a.clip_rrect(28, 12, 44, 56, 4)
    a.rrect(24, 22, 52, 22, 0, "#4CC9F0")
    a.unclip()
    a.circle(50, 30, 5, "#FFFFFF", lw=2)
    a.poly([(46, 32.5), (50, 41), (54, 32.5)], "#FFFFFF", lw=2)
    a.face(50, 57, d=8, smile=5)


def sheep(a):
    a.rrect(35, 6, 9, 24, 3, "#7A6F8F")
    a.rrect(56, 6, 9, 24, 3, "#7A6F8F")
    a.blob([(27, 52, 17), (42, 68, 18), (62, 68, 18), (74, 52, 16), (50, 56, 22), (34, 38, 13), (66, 38, 13)], "#F7F3FF")
    a.ellipse(31, 40, 9, 5, "#F2C9A0")
    a.ellipse(69, 40, 9, 5, "#F2C9A0")
    a.ellipse(50, 38, 16, 19, "#F2C9A0")
    a.dot(43, 43, 2.8)
    a.dot(57, 43, 2.8)
    a.smile(50, 33, 4.5)


def wool(a):
    a.circle(46, 52, 32, "#FF8FAB")
    a.clip_circle(46, 52, 32)
    a.bez((12, 44), [(34, 58, 58, 58, 80, 44)], lw=2.6)
    a.bez((16, 32), [(38, 46, 58, 46, 78, 30)], lw=2.6)
    a.bez((22, 22), [(40, 34, 56, 34, 70, 22)], lw=2.6)
    a.unclip()
    a.circle(46, 52, 32, None)
    a.dot(37, 68, 2.8)
    a.dot(55, 68, 2.8)
    a.smile(46, 62, 5)
    a.bez((70, 28), [(84, 26, 98, 36, 90, 46), (84, 52, 78, 42, 88, 38)], lw=3)


def tree(a):
    a.rrect(42, 6, 16, 48, 4, "#C68642")
    a.blob([(50, 72, 22), (27, 56, 18), (73, 56, 18), (50, 52, 22)], "#6BCB77")
    for x, y in [(30, 66), (68, 74), (74, 48), (32, 46), (50, 88)]:
        a.circle(x, y, 5.5, "#FF595E", lw=2.6)
    a.dot(42, 62, 2.8)
    a.dot(58, 62, 2.8)
    a.smile(50, 56, 5)


def apple(a):
    a.line(50, 68, 54, 86, w=4.5, color="#8B5A2B")
    a.blob([(38, 46, 26), (62, 46, 26), (50, 40, 28)], "#FF595E")
    a.bez((55, 80), [(62, 95, 82, 92, 86, 82), (76, 70, 60, 70, 55, 80)], fill="#6BCB77", close=True, lw=3)
    a.dot(40, 52, 2.8)
    a.dot(60, 52, 2.8)
    a.smile(50, 45, 6)
    if not a.outline:
        a.c.setFillColor(colors.white)
        a.c.ellipse(24, 52, 31, 64, stroke=0, fill=1)


def duck(a):
    a.ellipse(38, 13, 9, 4, "#FF9F1C")
    a.ellipse(56, 13, 9, 4, "#FF9F1C")
    a.poly([(20, 50), (4, 64), (22, 38)], "#FFE066")
    a.ellipse(45, 38, 32, 24, "#FFE066")
    a.ellipse(41, 36, 14, 9, "#FFD23F")
    a.circle(68, 66, 17, "#FFE066")
    a.ellipse(88, 62, 10, 5, "#FF9F1C")
    a.dot(70, 71, 2.8)


def fish(a):
    a.poly([(66, 50), (94, 72), (94, 28)], "#FFB703")
    a.poly([(38, 70), (52, 86), (60, 68)], "#FFB703")
    a.ellipse(44, 50, 32, 22, "#4CC9F0")
    a.dot(28, 56, 3)
    a.smile(26, 46, 4)
    a.circle(14, 80, 4, "#FFFFFF", lw=2.4)
    a.circle(22, 92, 3, "#FFFFFF", lw=2.2)


def grapes(a):
    a.line(50, 76, 52, 92, w=4.5, color="#8B5A2B")
    a.bez((52, 88), [(60, 98, 80, 96, 86, 88), (78, 78, 62, 78, 52, 88)], fill="#6BCB77", close=True, lw=3)
    a.blob([(32, 64, 13), (50, 66, 13), (68, 64, 13), (41, 48, 13), (59, 48, 13), (50, 32, 13)], "#A78BFA")
    a.face(50, 52, d=8, smile=5)


def ice_cream(a):
    a.poly([(28, 52), (72, 52), (50, 4)], "#F4C77A")
    a.line(38, 46, 52, 16, w=2.4)
    a.line(62, 46, 48, 16, w=2.4)
    a.circle(50, 62, 25, "#FFB5C2")
    a.circle(50, 84, 12, "#FFF3D6")
    a.face(50, 58, d=8, smile=5)


def jellyfish(a):
    for x in (34, 45, 56, 67):
        a.bez((x, 40), [(x - 7, 30, x + 7, 22, x, 8)])
    a.ellipse(50, 62, 32, 28, "#E9B6F5")
    a.face(50, 62, d=9, smile=6)


def kite(a):
    a.bez((50, 24), [(38, 14, 62, 10, 46, 0)], lw=3)
    a.circle(46, 12, 4, "#FFD23F", lw=2.4)
    a.circle(52, 5, 3.5, "#6BCB77", lw=2.2)
    a.poly([(50, 94), (80, 62), (50, 24), (20, 62)], "#FF595E")
    a.poly([(20, 62), (80, 62), (50, 24)], "#FFD23F")
    a.face(50, 76, d=7, smile=4.5)


def lemon(a):
    a.ellipse(50, 48, 38, 27, "#FFE74C")
    a.ellipse(88, 48, 5, 4, "#FFE74C", lw=3)
    a.ellipse(12, 48, 5, 4, "#FFE74C", lw=3)
    a.bez((52, 74), [(58, 92, 76, 92, 82, 84), (74, 72, 60, 70, 52, 74)], fill="#6BCB77", close=True, lw=3)
    a.face(50, 48, d=10, smile=6)


def nest(a):
    a.ellipse(38, 68, 11, 16, "#FFF1D6")
    a.ellipse(62, 68, 11, 16, "#CFE8FF")
    for x in (34, 42, 58, 66):
        a.dot(x, 72, 2.3)
    a.smile(38, 68, 3.5)
    a.smile(62, 68, 3.5)
    a.ellipse(50, 36, 40, 24, "#C68642")
    a.clip_ellipse(50, 36, 40, 24)
    a.bez((8, 40), [(30, 30, 70, 30, 92, 40)], lw=2.4)
    a.bez((8, 30), [(30, 20, 70, 20, 92, 30)], lw=2.4)
    a.bez((8, 50), [(30, 40, 70, 40, 92, 50)], lw=2.4)
    a.unclip()
    a.ellipse(50, 36, 40, 24, None)


def orange(a):
    a.circle(50, 46, 34, "#FFA94D")
    a.bez((50, 80), [(58, 96, 76, 94, 82, 86), (74, 74, 58, 74, 50, 80)], fill="#6BCB77", close=True, lw=3)
    a.face(50, 46, d=10, smile=6)


def pig(a):
    a.poly([(22, 74), (32, 96), (46, 80)], "#FFB5C2")
    a.poly([(78, 74), (68, 96), (54, 80)], "#FFB5C2")
    a.ellipse(50, 50, 37, 33, "#FFB5C2")
    a.ellipse(50, 38, 17, 12, "#FF8FAB")
    a.dot(44, 38, 2.6)
    a.dot(56, 38, 2.6)
    a.dot(35, 60, 3.2)
    a.dot(65, 60, 3.2)


def queen(a):
    a.ellipse(50, 40, 36, 36, "#8B5A2B")
    a.circle(50, 44, 25, "#FFE0C2")
    a.face(50, 46, d=10, smile=6)
    a.poly([(26, 66), (30, 92), (42, 76), (50, 94), (58, 76), (70, 92), (74, 66)], "#FFD23F")
    a.circle(50, 74, 3.5, "#FF595E", lw=2)


def rabbit(a):
    a.ellipse(36, 76, 9, 22, "#F3F0FF")
    a.ellipse(64, 76, 9, 22, "#F3F0FF")
    a.ellipse(36, 76, 4, 14, "#FFB5C2", lw=1.8)
    a.ellipse(64, 76, 4, 14, "#FFB5C2", lw=1.8)
    a.ellipse(50, 38, 32, 28, "#F3F0FF")
    a.dot(39, 42, 3.2)
    a.dot(61, 42, 3.2)
    a.ellipse(50, 34, 5, 3.5, "#FFB5C2", lw=2.2)
    a.smile(50, 30, 5)


def umbrella(a):
    a.line(50, 52, 50, 16, w=4)
    a.bez((50, 16), [(50, 4, 32, 4, 32, 14)], lw=4)
    a.bez((8, 52), [(8, 92, 92, 92, 92, 52), (82, 42, 72, 42, 64, 52), (56, 42, 44, 42, 36, 52), (28, 42, 18, 42, 8, 52)],
          fill="#FF595E", close=True)
    a.poly([(50, 80), (36, 52), (64, 52)], "#FFD23F")
    a.line(50, 80, 50, 94, w=4)
    a.face(50, 62, d=5, smile=3.5)


def van(a):
    a.rrect(6, 26, 88, 40, 8, "#4D9DE0")
    a.rrect(14, 40, 34, 18, 4, "#D6F0FF")
    a.rrect(54, 40, 32, 18, 4, "#D6F0FF")
    a.circle(28, 22, 11, "#2B2D42")
    a.circle(28, 22, 4, "#FFFFFF", lw=2)
    a.circle(72, 22, 11, "#2B2D42")
    a.circle(72, 22, 4, "#FFFFFF", lw=2)
    a.circle(90, 36, 3.4, "#FFD23F", lw=2)


def xylophone(a):
    a.line(22, 8, 40, 94)
    a.line(78, 8, 60, 94)
    for x, y, w, col in [(12, 12, 76, "#FF595E"), (18, 28, 64, "#FFB703"), (24, 44, 52, "#6BCB77"),
                         (30, 60, 40, "#4D9DE0"), (36, 76, 28, "#8B7CF6")]:
        a.rrect(x, y, w, 13, 5, col)


def yo_yo(a):
    a.circle(50, 92, 5, None)
    a.line(50, 87, 50, 72, w=3)
    a.circle(50, 40, 32, "#FF595E")
    a.circle(50, 40, 21, "#FFD23F")
    a.face(50, 43, d=7, smile=5)


def zebra(a):
    a.ellipse(30, 84, 8, 11, "#FFFFFF")
    a.ellipse(70, 84, 8, 11, "#FFFFFF")
    a.rrect(26, 16, 48, 68, 22, "#FFFFFF")
    a.clip_rrect(26, 16, 48, 68, 22)
    a.rrect(20, 63, 60, 7, 0, "#2B2D42")
    a.rrect(20, 76, 60, 7, 0, "#2B2D42")
    a.rrect(22, 34, 8, 20, 0, "#2B2D42")
    a.rrect(70, 34, 8, 20, 0, "#2B2D42")
    a.unclip()
    a.rrect(26, 16, 48, 68, 22, None)
    a.ellipse(50, 32, 19, 14, "#E5E7EB")
    a.dot(44, 32, 2.6)
    a.dot(56, 32, 2.6)
    a.dot(38, 54, 3.2)
    a.dot(62, 54, 3.2)


# ---- Indonesian phonics vocabulary icons -------------------------------------------------
def snake(a):
    a.blob([(14, 24, 10), (26, 17, 10), (38, 17, 10), (50, 23, 10), (59, 33, 10), (60, 45, 10), (52, 55, 10),
            (41, 59, 10), (34, 68, 10), (37, 80, 11), (48, 86, 13)], "#6BCB77")
    a.dot(44, 89, 2.8)
    a.dot(55, 89, 2.8)
    a.line(60, 84, 72, 84, w=2.6, color="#FF595E")
    a.line(72, 84, 79, 89, w=2.6, color="#FF595E")
    a.line(72, 84, 79, 79, w=2.6, color="#FF595E")


def wave(a):
    a.bez((6, 22), [(6, 60, 30, 88, 58, 86), (80, 84, 90, 66, 80, 52), (90, 50, 94, 36, 94, 22)], fill="#4CC9F0", close=True)
    a.bez((12, 32), [(24, 42, 36, 22, 48, 32), (60, 42, 72, 22, 88, 32)], lw=2.6)
    a.face(44, 56, d=8, smile=5)


def chili(a):
    a.bez((30, 84), [(70, 80, 90, 48, 70, 12), (60, 30, 50, 50, 22, 62), (12, 72, 20, 82, 30, 84)], fill="#FF595E", close=True)
    a.line(30, 84, 25, 96, w=5, color="#6BCB77")
    a.dot(50, 62, 2.6)
    a.dot(58, 52, 2.6)


def photo(a):
    a.rrect(10, 18, 80, 64, 8, "#C68642")
    a.rrect(18, 26, 64, 48, 4, "#CDEBFF", lw=2.4)
    a.circle(66, 60, 8, "#FFD23F", lw=2.4)
    a.poly([(18, 26), (38, 58), (58, 26)], "#6BCB77", lw=2.6)
    a.poly([(46, 26), (62, 46), (82, 26)], "#4EAD5B", lw=2.6)


def elephant(a):
    a.circle(20, 58, 19, "#B8C4D6")
    a.circle(80, 58, 19, "#B8C4D6")
    a.circle(20, 58, 10, "#FFB5C2", lw=2)
    a.circle(80, 58, 10, "#FFB5C2", lw=2)
    a.circle(50, 56, 28, "#C9D3E3")
    a.rrect(42, 8, 16, 44, 8, "#C9D3E3")
    a.dot(40, 62, 3)
    a.dot(60, 62, 3)


def heart(a):
    a.bez((50, 16), [(8, 44, 8, 86, 32, 86), (42, 86, 50, 80, 50, 70), (50, 80, 58, 86, 68, 86), (92, 86, 92, 44, 50, 16)],
          fill="#FF595E", close=True)
    a.face(50, 58, d=10, smile=6)


def pineapple(a):
    a.poly([(50, 66), (32, 92), (44, 68)], "#6BCB77")
    a.poly([(50, 68), (50, 99), (58, 68)], "#6BCB77")
    a.poly([(50, 66), (70, 92), (56, 68)], "#6BCB77")
    a.ellipse(50, 38, 27, 33, "#FFB703")
    a.clip_ellipse(50, 38, 27, 33)
    for k in range(-3, 4):
        a.line(50 + k * 14 - 30, 8, 50 + k * 14 + 30, 72, w=1.6)
        a.line(50 + k * 14 + 30, 8, 50 + k * 14 - 30, 72, w=1.6)
    a.unclip()
    a.ellipse(50, 38, 27, 33, None)
    a.circle(50, 40, 15, "#FFE9A8", lw=2)
    a.face(50, 41, d=6, smile=4)


def house(a):
    a.rrect(20, 14, 60, 42, 4, "#FFE0B3")
    a.poly([(10, 54), (50, 90), (90, 54)], "#FF595E")
    a.rrect(42, 14, 16, 28, 3, "#C68642")
    a.rrect(25, 32, 12, 12, 2, "#CDEBFF", lw=2.4)
    a.rrect(63, 32, 12, 12, 2, "#CDEBFF", lw=2.4)


def hat(a):
    a.bez((16, 36), [(16, 88, 84, 88, 84, 36)], fill="#4D9DE0", close=True)
    a.ellipse(50, 34, 44, 12, "#FFB703")
    a.circle(50, 78, 6, "#FF595E", lw=2.6)
    a.face(50, 58, d=8, smile=5)


def vase(a):
    a.line(50, 70, 50, 80)
    a.blob([(42, 86, 6), (58, 86, 6), (50, 92, 6)], "#FFB5C2", lw=3)
    a.circle(50, 86, 3.4, "#FFD23F", lw=2)
    a.bez((36, 10), [(8, 22, 12, 58, 38, 62), (38, 64, 38, 68, 38, 70), (46, 70, 54, 70, 62, 70), (62, 68, 62, 64, 62, 62),
                     (88, 58, 92, 22, 64, 10)], fill="#4D9DE0", close=True)
    a.face(50, 38, d=9, smile=6)


def carrot(a):
    a.poly([(42, 70), (34, 94), (50, 72)], "#6BCB77")
    a.poly([(50, 72), (50, 99), (58, 72)], "#6BCB77")
    a.poly([(58, 70), (70, 92), (52, 72)], "#6BCB77")
    a.poly([(30, 70), (70, 70), (50, 6)], "#FF9F1C")
    a.face(50, 54, d=7, smile=4.5)


def star(a):
    pts = []
    for k in range(10):
        r = 46 if k % 2 == 0 else 20
        ang = math.radians(90 + 36 * k)
        pts.append((50 + r * math.cos(ang), 52 + r * math.sin(ang)))
    a.poly(pts, "#FFD23F")
    a.face(50, 50, d=8, smile=5)


def book(a):
    a.rrect(14, 12, 72, 76, 6, "#FF595E")
    a.rrect(14, 12, 12, 76, 4, "#C0262B")
    a.rrect(34, 54, 42, 26, 4, "#FFFFFF", lw=2.6)
    a.line(40, 70, 70, 70, w=2.6)
    a.line(40, 62, 60, 62, w=2.6)
    a.face(56, 32, d=8, smile=5)


def ball(a):
    a.circle(50, 50, 38, "#FF595E")
    a.clip_circle(50, 50, 38)
    a.rrect(10, 10, 22, 80, 0, "#FFD23F")
    a.rrect(68, 10, 22, 80, 0, "#4D9DE0")
    a.unclip()
    a.circle(50, 50, 38, None)
    a.face(50, 52, d=8, smile=5)


def ship(a):
    a.line(50, 56, 50, 90)
    a.poly([(50, 90), (50, 58), (80, 58)], "#FF595E")
    a.rrect(34, 38, 32, 20, 3, "#FFFFFF")
    a.poly([(8, 38), (92, 38), (78, 12), (22, 12)], "#C68642")
    a.dot(43, 48, 2.8)
    a.dot(57, 48, 2.8)


def eye(a):
    a.bez((6, 50), [(30, 86, 70, 86, 94, 50), (70, 14, 30, 14, 6, 50)], fill="#FFFFFF", close=True)
    a.circle(50, 50, 20, "#4D9DE0")
    a.dot(50, 50, 9)
    if not a.outline:
        a.c.setFillColor(colors.white)
        a.c.circle(56, 57, 4, stroke=0, fill=1)


def coffee(a):
    a.bez((68, 56), [(96, 62, 96, 26, 66, 28)], lw=5)
    a.ellipse(44, 14, 38, 6, "#4D9DE0")
    a.bez((20, 64), [(20, 12, 68, 12, 68, 64)], fill="#FFFFFF", close=True)
    a.ellipse(44, 64, 24, 7, "#8B5A2B")
    a.face(44, 40, d=8, smile=5)
    a.bez((38, 76), [(30, 84, 46, 88, 38, 96)], lw=3)
    a.bez((52, 76), [(44, 84, 60, 88, 52, 96)], lw=3)


def fire(a):
    a.bez((50, 8), [(12, 8, 12, 52, 40, 92), (48, 72, 58, 70, 62, 54), (78, 64, 88, 8, 50, 8)], fill="#FF9F1C", close=True)
    a.ellipse(50, 28, 15, 19, "#FFD23F")
    a.face(50, 28, d=6, smile=4)


def bird(a):
    a.line(40, 22, 40, 8)
    a.line(54, 22, 54, 8)
    a.poly([(20, 52), (2, 66), (22, 40)], "#2E9CCB")
    a.ellipse(46, 44, 30, 26, "#4CC9F0")
    a.ellipse(40, 42, 14, 10, "#2E9CCB")
    a.circle(68, 64, 16, "#4CC9F0")
    a.poly([(82, 66), (98, 62), (82, 58)], "#FF9F1C")
    a.dot(72, 68, 2.8)


ICONS = {f.__name__: f for f in (
    chicken, egg, bee, honey, cow, milk, sheep, wool, tree, apple,
    duck, fish, grapes, ice_cream, jellyfish, kite, lemon, nest, orange, pig,
    queen, rabbit, umbrella, van, xylophone, yo_yo, zebra,
    snake, wave, chili, photo, elephant, heart, pineapple, house, hat, vase, carrot, star, book, ball, ship,
    eye, coffee, fire, bird)}


def _placeholder(a, key):
    a.rrect(10, 10, 80, 80, 16, "#EEF3FF")
    a.c.setFillColor(INK)
    a.c.setFont(cfg.F_BOLD, 46)
    a.c.drawCentredString(50, 34, (key[:1] or "?").upper())


# ------------------------------------------------------------------ public API
_outline_cache: dict[str, Path] = {}


def _png_path(slug):
    p = cfg.IMAGE_DIR / f"{slug}.png"
    return p if p.exists() else None


def art_source(slug: str) -> str:
    if _png_path(slug):
        return "png"
    return "vector" if slug in ICONS else "placeholder"


def _png_to_outline(path: Path) -> Path:
    """Rough line-art version of a PNG for coloring pages (use {slug}_outline.png for best results)."""
    custom = path.with_name(path.stem + "_outline.png")
    if custom.exists():
        return custom
    if str(path) in _outline_cache:
        return _outline_cache[str(path)]
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")
    bg.alpha_composite(im)
    edges = bg.convert("L").filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.invert(edges).point(lambda v: 0 if v < 235 else 255).filter(ImageFilter.MinFilter(3))
    out = Path("/tmp") / f"outline_{path.stem}.png"
    edges.convert("RGB").save(out)
    _outline_cache[str(path)] = out
    return out


def draw_object(c, slug: str, x: float, y: float, size: float, outline: bool = False) -> str:
    """Draw artwork for `slug` into the square (x, y, size, size). Returns the source used."""
    src = art_source(slug)
    c.saveState()
    c.setLineJoin(1)
    c.setLineCap(1)
    if src == "png":
        path = _png_path(slug)
        if outline:
            path = _png_to_outline(path)
        c.drawImage(ImageReader(str(path)), x, y, size, size, preserveAspectRatio=True, anchor="c", mask="auto")
    else:
        c.translate(x, y)
        c.scale(size / 100.0, size / 100.0)
        art = Art(c, outline)
        if src == "vector":
            ICONS[slug](art)
        else:
            _placeholder(art, slug)
    c.restoreState()
    return src
