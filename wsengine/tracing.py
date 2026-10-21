"""Tracing Words series (templates A-T): one themed page = 4 words.

NOTHING is drawn as artwork by code. Every picture is a file you place in assets/images/ :
    assets/images/{word_en}.png   e.g. cow.png, ice_cream.png, t_rex.png, police_officer.png
(.jpg / .jpeg also work; {word_id} file names such as sapi.png work too; sheet column Image_File overrides).
A missing picture is shown as an empty dashed box printed with the file name it expects.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from . import config as cfg
from . import strokes
from .database import TraceTheme, TraceWord
from .letters import AVAIL_W, X0
from .linguistics import syllabify_id
from .modules import W, card_box, dashed_rrect, dashed_text, fit_size, footer, header, hx, instruction, text  # noqa: F401

TOP = cfg.CONTENT_TOP


class TracingCtx:
    def __init__(self, template: str, page_no: int, page_total: int, theme: TraceTheme):
        self.template, self.page_no, self.page_total, self.theme = template, page_no, page_total, theme
        self.spec = theme.spec

    @property
    def color(self):
        return cfg.TEMPLATE_COLORS[self.template]

    def fill(self, t):
        return t


# ------------------------------------------------------------------ pictures (files only)
def find_image(wd: TraceWord) -> Path | None:
    """Look in assets/images/ (case-insensitive): Image_File, then {word_en}, then {word_id}; png, jpg, jpeg."""
    if not cfg.IMAGE_DIR.exists():
        return None
    files = {f.name.lower(): f for f in cfg.IMAGE_DIR.iterdir() if f.is_file()}
    names = ([wd.image_file] if wd.image_file else []) + [wd.slug_en, wd.slug_id]
    for n in names:
        base = Path(n)
        if base.suffix.lower() in cfg.TRACING_SET["image_exts"]:
            cands = [base.name.lower()]
        else:
            cands = [base.name.lower() + ext for ext in cfg.TRACING_SET["image_exts"]]
        for cand in cands:
            if cand in files:
                return files[cand]
    return None


@lru_cache(maxsize=256)
def _load(path: str) -> ImageReader:
    im = Image.open(path)
    im = im.convert("RGBA")
    im.thumbnail((700, 700))          # keeps the PDF small even if you drop in 4000 px art
    return ImageReader(im)


def image_slot(c, x, y, s, wd: TraceWord) -> bool:
    """White rounded slot; the picture if the file exists, otherwise an empty box that names the file."""
    c.setFillColor(hx("#FFFFFF"))
    c.setStrokeColor(hx(cfg.LINE))
    c.setLineWidth(1.4)
    c.roundRect(x, y, s, s, 12, stroke=1, fill=1)
    path = find_image(wd)
    if path:
        pad = 5
        c.drawImage(_load(str(path)), x + pad, y + pad, s - 2 * pad, s - 2 * pad, preserveAspectRatio=True, anchor="c", mask="auto")
        return True
    dashed_rrect(c, x + 4, y + 4, s - 8, s - 8, 9, cfg.GREY, 1.2)
    text(c, "gambar", x + s / 2, y + s / 2 + 3, cfg.F_MED, 10, cfg.GREY, "center")
    text(c, wd.expected_file, x + s / 2, y + s / 2 - 10, cfg.F_REG, 7.5, cfg.GREY, "center", max_width=s - 14)
    return False


# ------------------------------------------------------------------ page parts
def step_strip(c, ctx, y):
    steps = [("Lihat & sebutkan", "Look and say"), ("Tepuk suku katanya", "Clap the syllables"), ("Tebalkan hurufnya", "Trace the letters")]
    w = (W - 2 * 34 - 16) / 3
    for i, (idn, en) in enumerate(steps):
        x = 34 + 8 + i * w
        c.setFillColor(hx(ctx.color))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.circle(x + 13, y - 20, 12, stroke=1, fill=1)
        text(c, str(i + 1), x + 13, y - 25, cfg.F_BOLD, 13, "#FFFFFF", "center")
        text(c, idn, x + 32, y - 17, cfg.F_BOLD, 9.5, cfg.NAVY)
        text(c, en, x + 32, y - 29, cfg.F_IT, 8.5, cfg.GREY)


TRACE_GAP = 0.45      # space between letters, in x-height units
TRACE_MAX_U = 15.5   # largest x-height (pt) of the traced word


def _trace_strokes(ch: str):
    """Single-stroke path(s) of one character in line units, or None for a space."""
    if ch in strokes.SMALL:
        return strokes.SMALL[ch]
    if ch == "-":
        return [[(0.0, 0.5), (0.55, 0.5)]]
    return None


def trace_word_width(word: str, u: float) -> float:
    total = 0.0
    for ch in word.lower():
        st = _trace_strokes(ch)
        if st is None:
            total += 0.6 * u
        else:
            lo, hi = strokes._bounds(st)
            total += (hi - lo) * u + TRACE_GAP * u
    return max(total - TRACE_GAP * u, 0.0)


def _stroke_path(c, pts, color, lw, dash=None):
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


def draw_trace_word(c, word: str, x: float, base: float, u: float, band: bool = True) -> None:
    """The word as ONE dashed pen line per stroke (the letter's centre line), no outline.
    A soft pale band under it (cfg.TRACING_SET['trace_band']) helps small hands; the dashes are the only line to follow."""
    cx, first = x, True
    for ch in word.lower():
        st = _trace_strokes(ch)
        if st is None:
            cx += 0.6 * u
            continue
        lo, hi = strokes._bounds(st)
        cs = [[(cx + (px - lo) * u, base + py * u) for px, py in s_] for s_ in st]
        if band:
            for s_ in cs:
                _stroke_path(c, s_, "#E3E9F5", 0.34 * u)
        for s_ in cs:
            _stroke_path(c, s_, "#5B6475", 1.5, (3, 3))
        if first:   # green start dot on the first stroke of the word
            c.setFillColor(hx("#3FB984"))
            c.setStrokeColor(hx("#FFFFFF"))
            c.setLineWidth(1.2)
            c.circle(cs[0][0][0], cs[0][0][1], 4.2, stroke=1, fill=1)
            first = False
        cx += (hi - lo) * u + TRACE_GAP * u


def trace_line(c, ctx, word: str, x, area_top, w):
    """Guide lines (top / x-height / baseline / descender) + the single-stroke dashed word."""
    wu = trace_word_width(word, 1.0)
    u = min(TRACE_MAX_U, (w - 18) / wu) if wu else TRACE_MAX_U
    base = area_top - 34
    strokes_lines(c, x, x + w, base, u)
    draw_trace_word(c, word, x + 9, base, u, cfg.TRACING_SET.get("trace_band", True))


def strokes_lines(c, x0, x1, base, u):
    c.saveState()
    c.setLineWidth(1)
    c.setStrokeColor(hx("#D5DEEF"))
    c.line(x0, base + 2 * u, x1, base + 2 * u)
    c.line(x0, base - u, x1, base - u)
    c.setStrokeColor(hx("#8FA6CC"))
    c.setLineWidth(1.5)
    c.line(x0, base, x1, base)
    c.setDash(3, 3)
    c.setLineWidth(1)
    c.line(x0, base + u, x1, base + u)
    c.restoreState()


def word_card(c, ctx, x, y_top, w, h, wd: TraceWord):
    card_box(c, x, y_top - h, w, h, ctx.color)
    s = h - 20
    image_slot(c, x + 10, y_top - h + 10, s, wd)
    tx, colw = x + 10 + s + 14, 146
    text(c, wd.word_id, tx, y_top - 34, cfg.F_BOLD, 24, cfg.NAVY, max_width=colw)
    text(c, wd.word_en, tx, y_top - 52, cfg.F_MED, 13, ctx.color, max_width=colw)
    text(c, "Tepuk / Clap", tx, y_top - 66, cfg.F_MED, 7, cfg.GREY)
    syl = syllabify_id(wd.word_id, wd.syllables or None)
    size, pad, gap = 11, 7, 5
    widths = [stringWidth(t, cfg.F_BOLD, size) + 2 * pad for t in syl]
    while sum(widths) + gap * (len(syl) - 1) > colw and size > 6.5:
        size -= 0.5
        pad = max(4, pad - 0.3)
        widths = [stringWidth(t, cfg.F_BOLD, size) + 2 * pad for t in syl]
    bx = tx
    for t, bw in zip(syl, widths):
        c.setFillColor(hx("#FFFFFF"))
        c.setStrokeColor(hx(ctx.color))
        c.setLineWidth(1.8)
        c.roundRect(bx, y_top - 92, bw, 22, 7, stroke=1, fill=1)
        text(c, t, bx + bw / 2, y_top - 85, cfg.F_BOLD, size, cfg.NAVY, "center")
        bx += bw + gap
    text(c, wd.letters_en, tx, y_top - 110, cfg.F_REG, 9, cfg.GREY, max_width=colw)
    cx0 = tx + colw + 12
    cw = x + w - 12 - cx0
    trace_line(c, ctx, wd.word_id, cx0, y_top - 6, cw)
    trace_line(c, ctx, wd.word_en, cx0, y_top - 64, cw)


def page_tracing(c, ctx: TracingCtx):
    header(c, ctx)
    step_strip(c, ctx, TOP + 4)
    top, h, gap = TOP - 52, 124, 10
    for i, wd in enumerate(ctx.theme.words):
        word_card(c, ctx, X0, top - i * (h + gap), AVAIL_W, h, wd)
    footer(c, ctx)
