"""Capital Letters series (templates A-J). Reuses Header / Footer / card modules.

Pages A-I: three letters per page (I has two). Each letter gets one band:
   [ model letter with numbered strokes ] [ 2 trace boxes + 2 write-it-yourself boxes ] [ picture card ]
Page J: alphabet order tiles + missing-letter practice.
"""
from __future__ import annotations

from . import config as cfg
from . import icons, strokes
from .database import LetterItem
from .modules import H, M, W, card_box, dashed_rrect, footer, header, hx, instruction, text

X0 = M + 8
AVAIL_W = W - 2 * M - 16  # 511 pt
TOP = cfg.CONTENT_TOP


class LetterCtx:
    """Minimal context so header()/footer() work for the letters series."""

    def __init__(self, template: str, page_no: int, page_total: int, items: dict[str, LetterItem]):
        self.template, self.page_no, self.page_total, self.items = template, page_no, page_total, items
        self.spec = cfg.LETTER_TEMPLATES[template]

    @property
    def color(self):
        return cfg.TEMPLATE_COLORS[self.template]

    def fill(self, t):  # no row placeholders in this series
        return t


# ------------------------------------------------------------------ pieces
def _guide_box(c, x, y, w, h):
    c.setFillColor(hx("#FFFFFF"))
    c.setStrokeColor(hx(cfg.LINE))
    c.setLineWidth(1.6)
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)
    base, top = y + h * 0.12, y + h * 0.88
    c.setStrokeColor(hx("#BFD0EA"))
    c.setLineWidth(1)
    c.line(x + 6, base, x + w - 6, base)
    c.line(x + 6, top, x + w - 6, top)
    c.setDash(3, 3)
    c.line(x + 6, (base + top) / 2, x + w - 6, (base + top) / 2)
    c.setDash([], 0)
    return base, top - base


def _letter_row(c, ctx: LetterCtx, it: LetterItem, y_top: float, h: float = 170):
    col = ctx.color
    # ---- model letter
    mw = 130
    card_box(c, X0, y_top - h, mw, h, col)
    mh = 100
    lw = strokes.letter_width(it.letter, mh)
    strokes.draw_letter(c, it.letter, X0 + (mw - lw) / 2, y_top - h + 38, mh, "solid", col)
    text(c, f"Huruf Besar {it.letter}", X0 + mw / 2, y_top - h + 20, cfg.F_BOLD, 9.5, cfg.NAVY, "center")
    text(c, f"Capital {it.letter}", X0 + mw / 2, y_top - h + 8, cfg.F_IT, 8, cfg.GREY, "center")
    # ---- trace (top row) + write (bottom row)
    gx, bw, bh, gap = X0 + mw + 8, 108, 76, 6
    for r in range(2):
        for k in range(2):
            bx = gx + k * (bw + gap)
            by = y_top - 6 - bh - r * (bh + gap)
            base, ch = _guide_box(c, bx, by, bw, bh)
            lw = strokes.letter_width(it.letter, ch)
            if r == 0:
                strokes.draw_letter(c, it.letter, bx + (bw - lw) / 2, base, ch, "trace", numbers=(k == 0))
            elif k == 0:  # tiny start hint in the first blank box
                sx = bx + (bw - lw) / 2 + strokes.LETTERS[it.letter][0][0][0] * lw
                sy = base + strokes.LETTERS[it.letter][0][0][1] * ch
                c.setFillColor(hx(col))
                c.circle(sx, sy, 4.2, stroke=0, fill=1)
    # ---- picture card
    px = gx + 2 * bw + gap + 8
    pw = X0 + AVAIL_W - px
    card_box(c, px, y_top - h, pw, h, col)
    icons.draw_object(c, it.slug, px + (pw - 88) / 2, y_top - 14 - 88, 88)
    text(c, f"{it.letter} for {it.word_en}", px + pw / 2, y_top - 124, cfg.F_BOLD, 13, cfg.NAVY, "center", max_width=pw - 14)
    text(c, f"{it.word_en} = {it.word_id}", px + pw / 2, y_top - 142, cfg.F_MED, 10.5, col, "center", max_width=pw - 14)


def _name_row(c, ctx: LetterCtx, y_top: float, h: float = 170):
    """Closing row on page I: celebration + write your name."""
    card_box(c, X0, y_top - h, AVAIL_W, h, ctx.color, fill="#FFFFFF")
    text(c, "Z adalah huruf terakhir!  Hebat!", X0 + AVAIL_W / 2, y_top - 34, cfg.F_BOLD, 17, cfg.NAVY, "center")
    text(c, "Z is the last letter!  Great job!", X0 + AVAIL_W / 2, y_top - 54, cfg.F_IT, 11, cfg.GREY, "center")
    text(c, "Tulis namamu / Write your name:", X0 + 20, y_top - 82, cfg.F_BOLD, 10, ctx.color)
    base, top = y_top - h + 30, y_top - h + 30 + 46
    c.setStrokeColor(hx("#BFD0EA"))
    c.setLineWidth(1)
    c.line(X0 + 20, base, X0 + AVAIL_W - 20, base)
    c.line(X0 + 20, top, X0 + AVAIL_W - 20, top)
    c.setDash(3, 3)
    c.line(X0 + 20, (base + top) / 2, X0 + AVAIL_W - 20, (base + top) / 2)
    c.setDash([], 0)


# ------------------------------------------------------------------ pages A-I
def letters_page(c, ctx: LetterCtx):
    header(c, ctx)
    instruction(c, ctx, "Look, say, trace and write each letter.", "Lihat, ucapkan, tebalkan, dan tulis setiap huruf.")
    top = TOP - 40
    for i, ch in enumerate(ctx.spec["letters"]):
        _letter_row(c, ctx, ctx.items[ch], top - i * 180)
    if len(ctx.spec["letters"]) == 2:
        _name_row(c, ctx, top - 2 * 180)
    footer(c, ctx)


# ------------------------------------------------------------------ page J: review + order
def review_page(c, ctx: LetterCtx):
    header(c, ctx)
    instruction(c, ctx, "Follow the alphabet from A to Z.", "Ikuti urutan abjad dari A sampai Z.")
    cols, gap, th = 7, 7, 58
    tw = (AVAIL_W - gap * (cols - 1)) / cols
    top = TOP - 40
    for i in range(26):
        r, k = divmod(i, cols)
        x, y = X0 + k * (tw + gap), top - th - r * (th + 8)
        col = cfg.SWATCHES[i % len(cfg.SWATCHES)]
        card_box(c, x, y, tw, th, col, lw=2.2, r=12)
        text(c, chr(65 + i), x + tw / 2, y + th / 2 - 11, cfg.F_BOLD, 30, cfg.NAVY, "center")
        text(c, str(i + 1), x + 6, y + th - 11, cfg.F_MED, 7.5, cfg.GREY)
    # celebration tile fills the 2 empty cells after Z
    x, y = X0 + 5 * (tw + gap), top - th - 3 * (th + 8)
    card_box(c, x, y, 2 * tw + gap, th, ctx.color, fill="#FFFFFF", lw=2.2, r=12)
    text(c, "Hebat!", x + tw + gap / 2, y + th / 2 + 2, cfg.F_BOLD, 15, ctx.color, "center")
    text(c, "Great!", x + tw + gap / 2, y + th / 2 - 13, cfg.F_IT, 10, cfg.GREY, "center")
    # missing letters
    y2 = top - 4 * (th + 8) - 8
    instruction(c, ctx, "Write the missing letters.", "Tulis huruf yang hilang.", y=y2)
    seqs = ["AB_D_F", "J_LM_O", "ST_VW_"]
    bw, bh, bg = 76, 60, 11
    for r, seq in enumerate(seqs):
        for k, ch in enumerate(seq):
            x, y = X0 + k * (bw + bg), y2 - 40 - bh - r * (bh + 10)
            if ch == "_":
                c.setFillColor(hx("#FFFFFF"))
                dashed_rrect(c, x, y, bw, bh, 12, ctx.color, 2)
            else:
                card_box(c, x, y, bw, bh, hx_str(cfg.SWATCHES[(ord(ch) - 65) % len(cfg.SWATCHES)]), lw=2.2, r=12)
                text(c, ch, x + bw / 2, y + bh / 2 - 12, cfg.F_BOLD, 32, cfg.NAVY, "center")
    footer(c, ctx)


def hx_str(col):  # card_box expects a hex string
    return col




# ====================================================================== K-R: small letters on 4 lines
def _small_lines(c, x0, x1, base, u):
    """Ascender (light) / x-height (dashed) / baseline (strong) / descender (light)."""
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


def _strip(c, x, y, w, h):
    c.setFillColor(hx("#FFFFFF"))
    c.setStrokeColor(hx(cfg.LINE))
    c.setLineWidth(1.6)
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)


def _small_row(c, ctx: LetterCtx, ch: str, y_top: float, compact: bool = False):
    it = ctx.items[ch.upper()]
    col = ctx.color
    h = 100 if compact else 170
    mw = 100 if compact else 130
    # ---- model letter on 4 lines
    card_box(c, X0, y_top - h, mw, h, col)
    u = 27 if compact else 40
    base = y_top - h + (37 if compact else 76)
    _small_lines(c, X0 + 8, X0 + mw - 8, base, u)
    w = strokes.small_width(ch, u)
    strokes.draw_small(c, ch, X0 + (mw - w) / 2, base, u, "solid", col)
    if not compact:
        text(c, f"Huruf Kecil {ch}", X0 + mw / 2, y_top - h + 20, cfg.F_BOLD, 9.5, cfg.NAVY, "center")
        text(c, f"Small {ch}", X0 + mw / 2, y_top - h + 8, cfg.F_IT, 8, cfg.GREY, "center")
    # ---- practice strips
    gx = X0 + mw + 8
    pw = 100 if compact else 143
    sw = AVAIL_W - mw - pw - 16
    if compact:  # one strip: 2 trace cells + 2 write cells
        cell, uu = sw / 4, 26
        _strip(c, gx, y_top - h, sw, h)
        b = y_top - h + 36
        _small_lines(c, gx + 6, gx + sw - 6, b, uu)
        for k in range(4):
            cx = gx + k * cell
            lw = strokes.small_width(ch, uu)
            if k < 2:
                strokes.draw_small(c, ch, cx + (cell - lw) / 2, b, uu, "trace", numbers=(k == 0))
            elif k == 2:
                sx = cx + (cell - lw) / 2
                sy = b + SMALL_START[ch] * uu
                c.setFillColor(hx(col))
                c.circle(sx + SMALL_START_X[ch] * uu, sy, 4.2, stroke=0, fill=1)
        c.setStrokeColor(hx(col))
        c.setLineWidth(1.6)
        c.setDash(3, 3)
        c.line(gx + 2 * cell, y_top - h + 6, gx + 2 * cell, y_top - 6)
        c.setDash([], 0)
    else:  # two strips of 3 cells: trace, then write
        cell, uu, sh = sw / 3, 22, 78
        for r in range(2):
            y0 = y_top - 6 - sh - r * (sh + 6)
            _strip(c, gx, y0, sw, sh)
            b = y0 + 5 + uu
            _small_lines(c, gx + 6, gx + sw - 6, b, uu)
            lw = strokes.small_width(ch, uu)
            for k in range(3):
                cx = gx + k * cell
                if r == 0:
                    strokes.draw_small(c, ch, cx + (cell - lw) / 2, b, uu, "trace", numbers=(k == 0))
                elif k == 0:
                    c.setFillColor(hx(col))
                    c.circle(cx + (cell - lw) / 2 + SMALL_START_X[ch] * uu, b + SMALL_START[ch] * uu, 4.2, stroke=0, fill=1)
    # ---- picture card
    px = gx + sw + 8
    card_box(c, px, y_top - h, pw, h, col)
    if compact:
        icons.draw_object(c, it.slug, px + (pw - 54) / 2, y_top - 8 - 54, 54)
        text(c, f"{ch} for {it.word_en}", px + pw / 2, y_top - 76, cfg.F_BOLD, 9.5, cfg.NAVY, "center", max_width=pw - 10)
        text(c, f"{it.word_en} = {it.word_id}", px + pw / 2, y_top - 90, cfg.F_MED, 8, col, "center", max_width=pw - 10)
    else:
        icons.draw_object(c, it.slug, px + (pw - 88) / 2, y_top - 14 - 88, 88)
        text(c, f"{ch} for {it.word_en}", px + pw / 2, y_top - 124, cfg.F_BOLD, 13, cfg.NAVY, "center", max_width=pw - 14)
        text(c, f"{it.word_en} = {it.word_id}", px + pw / 2, y_top - 142, cfg.F_MED, 10.5, col, "center", max_width=pw - 14)


# where each small letter starts (x offset inside its box in line-units, y in line-units)
SMALL_START = {ch: strokes.SMALL[ch][0][0][1] for ch in strokes.SMALL}
SMALL_START_X = {ch: strokes.SMALL[ch][0][0][0] - strokes._bounds(strokes.SMALL[ch])[0] for ch in strokes.SMALL}


def small_page(c, ctx: LetterCtx):
    header(c, ctx)
    instruction(c, ctx, "Look, say, trace and write each small letter on the lines.",
                "Lihat, ucapkan, tebalkan, dan tulis setiap huruf kecil pada garis.")
    top = TOP - 40
    letters = ctx.spec["letters"]
    compact = len(letters) > 3
    step = 109 if compact else 180
    for i, ch in enumerate(letters):
        _small_row(c, ctx, ch, top - i * step, compact)
    footer(c, ctx)


# ====================================================================== S: look-alike letters
PAIRS = [("b", "d", "dbdbbd", "b"), ("p", "q", "pqqpqp", "q"), ("m", "n", "nmnmmn", "m")]
HINTS = {
    "b": ("Batang kiri, bulat kanan", "Stick left, ball right"),
    "d": ("Bulat kiri, batang kanan", "Ball left, stick right"),
    "p": ("Batang turun, bulat kanan", "Stick down, ball right"),
    "q": ("Bulat kiri, batang turun", "Ball left, stick down"),
    "m": ("Dua bukit", "Two humps"),
    "n": ("Satu bukit", "One hump"),
}


def similar_page(c, ctx: LetterCtx):
    header(c, ctx)
    instruction(c, ctx, "Look carefully, then circle the correct letter.",
                "Perhatikan baik-baik, lalu lingkari huruf yang benar.")
    top = TOP - 40
    cw = (AVAIL_W - 10) / 2
    for i, (a, b, seq, target) in enumerate(PAIRS):
        y = top - i * 162
        for k, ch in enumerate((a, b)):
            x = X0 + k * (cw + 10)
            colr = cfg.SWATCHES[4] if k == 0 else cfg.SWATCHES[1]
            card_box(c, x, y - 90, cw, 90, ctx.color)
            u = 24
            w = strokes.small_width(ch, u)
            strokes.draw_small(c, ch, x + 16 + (36 - w) / 2, y - 90 + 9 + u, u, "solid", colr, numbers=False)
            it = ctx.items[ch.upper()]
            icons.draw_object(c, it.slug, x + 52, y - 90 + 14, 62)
            tx = x + 122
            text(c, f"{ch} for {it.word_en}", tx, y - 34, cfg.F_BOLD, 10.5, cfg.NAVY, max_width=cw - 130)
            text(c, HINTS[ch][0], tx, y - 52, cfg.F_MED, 8.3, cfg.NAVY, max_width=cw - 130)
            text(c, HINTS[ch][1], tx, y - 65, cfg.F_IT, 8, cfg.GREY, max_width=cw - 130)
        # circle row
        ry = y - 98
        tcol = cfg.SWATCHES[4] if target == a else cfg.SWATCHES[1]
        text(c, "Lingkari huruf", X0 + 4, ry - 18, cfg.F_BOLD, 9.5, cfg.NAVY)
        text(c, "Circle the letter", X0 + 4, ry - 31, cfg.F_IT, 8, cfg.GREY)
        text(c, target, X0 + 104, ry - 34, cfg.F_BOLD, 32, tcol)
        for k, ch in enumerate(seq):
            bx = X0 + 158 + k * 58
            card_box(c, bx, ry - 46, 52, 44, ctx.color, fill="#FFFFFF", lw=2, r=10)
            text(c, ch, bx + 26, ry - 46 + 12, cfg.F_BOLD, 30, cfg.NAVY, "center")
        if i < 2:
            c.setStrokeColor(hx(cfg.LINE))
            c.setDash(4, 4)
            c.line(X0, y - 152, X0 + AVAIL_W, y - 152)
            c.setDash([], 0)
    footer(c, ctx)


# ====================================================================== T: capital-small pairs
def pairs_page(c, ctx: LetterCtx):
    header(c, ctx)
    instruction(c, ctx, "Aa to Zz: every capital letter has a small partner.",
                "Aa sampai Zz: setiap huruf besar punya pasangan huruf kecil.")
    cols, gap, th = 7, 6, 44
    tw = (AVAIL_W - gap * (cols - 1)) / cols
    top = TOP - 40
    for i in range(26):
        r, k = divmod(i, cols)
        x, y = X0 + k * (tw + gap), top - th - r * (th + 6)
        card_box(c, x, y, tw, th, cfg.SWATCHES[i % len(cfg.SWATCHES)], lw=2, r=10)
        text(c, chr(65 + i) + chr(97 + i), x + tw / 2, y + th / 2 - 8, cfg.F_BOLD, 22, cfg.NAVY, "center")
    x, y = X0 + 5 * (tw + gap), top - th - 3 * (th + 6)
    card_box(c, x, y, 2 * tw + gap, th, ctx.color, fill="#FFFFFF", lw=2, r=10)
    text(c, "Hebat!  Great!", x + tw + gap / 2, y + th / 2 - 5, cfg.F_BOLD, 13, ctx.color, "center")
    # matching exercise
    y2 = top - 4 * (th + 6) - 6
    instruction(c, ctx, "Draw a line from each capital letter to its small letter.",
                "Tarik garis dari huruf besar ke pasangan huruf kecilnya.", y=y2)
    caps, smalls = "ADGNQT", "gtaqdn"
    bw, bh = 110, 40
    lx, rx = X0 + 60, X0 + AVAIL_W - 60 - bw
    for i in range(6):
        yy = y2 - 34 - bh - i * (bh + 6)
        for xx, ch, colr in ((lx, caps[i], ctx.color), (rx, smalls[i], cfg.SWATCHES[(i + 2) % len(cfg.SWATCHES)])):
            card_box(c, xx, yy, bw, bh, colr, fill="#FFFFFF", lw=2.2, r=10)
            text(c, ch, xx + bw / 2, yy + bh / 2 - 9, cfg.F_BOLD, 28, cfg.NAVY, "center")
        for xx in (lx + bw, rx):
            c.setFillColor(hx(ctx.color))
            c.setStrokeColor(hx(cfg.NAVY))
            c.setLineWidth(2)
            c.circle(xx, yy + bh / 2, 7, stroke=1, fill=1)
    footer(c, ctx)


LETTER_FUNCS = {t: letters_page for t in "ABCDEFGHI"}
LETTER_FUNCS["J"] = review_page
LETTER_FUNCS.update({t: small_page for t in "KLMNOPQR"})
LETTER_FUNCS["S"] = similar_page
LETTER_FUNCS["T"] = pairs_page
