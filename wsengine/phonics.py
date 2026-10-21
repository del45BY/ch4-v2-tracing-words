"""Indonesian-first early-reading series, templates A-J (default product).

A vowel sounds | B-E beginning sounds A-Z | F-G syllables | H building words |
I bilingual picture-word match | J rhyming words.
Words come from Excel sheet 'Words'; which words each page uses is set in config.PHONICS_CONTENT.
"""
from __future__ import annotations

import random

from . import config as cfg
from . import icons, strokes
from .database import Word
from .letters import AVAIL_W, SMALL_START, SMALL_START_X, X0, _small_lines, _strip
from .linguistics import syllabify_id
from .modules import (M, W, card_box, dashed_rrect, dashed_text, fit_size, footer, header, hx, instruction,
                      scissors, text)

TOP = cfg.CONTENT_TOP
GAP = 0.3  # gap between letters of a word, in x-height units


class PhonicsCtx:
    def __init__(self, template: str, page_no: int, page_total: int, words: dict[str, Word]):
        self.template, self.page_no, self.page_total, self.words = template, page_no, page_total, words
        self.spec = cfg.PHONICS_TEMPLATES[template]
        self.content = cfg.PHONICS_CONTENT[template]
        self.rng = random.Random(f"phonics-{template}")

    @property
    def color(self):
        return cfg.TEMPLATE_COLORS[self.template]

    def fill(self, t):
        return t

    def w(self, key: str) -> Word:
        return self.words[key.lower()]


# ------------------------------------------------------------------ helpers
def derange(items, rng):
    """Shuffle so that no item stays at its original index (items must be unique)."""
    items = list(items)
    if len(items) < 2:
        return items
    for _ in range(200):
        s = items[:]
        rng.shuffle(s)
        if all(a != b for a, b in zip(s, items)):
            return s
    return items[1:] + items[:1]


def syl_of(wd: Word) -> list[str]:
    return syllabify_id(wd.word_id, wd.syllables or None)


def word_width(word: str, u: float) -> float:
    total, n = 0.0, 0
    for ch in word.lower():
        if ch in " -":
            total += 0.5 * u
        elif ch in strokes.SMALL:
            total += strokes.small_width(ch, u) + GAP * u
            n += 1
    return max(total - GAP * u, 0)


def draw_word(c, word, x, base, u, mode="solid", color=cfg.NAVY, numbers=True):
    cx, n = x, 0
    for ch in word.lower():
        if ch in " -":
            cx += 0.5 * u
        elif ch in strokes.SMALL:
            w = strokes.draw_small(c, ch, cx, base, u, mode, color, numbers=(numbers and n == 0))
            cx += w + GAP * u
            n += 1
    return word_width(word, u)


def start_dot(c, word, cell_x, cell_w, base, u, color):
    ch = next((k for k in word.lower() if k in strokes.SMALL), None)
    if not ch:
        return
    left = cell_x + (cell_w - word_width(word, u)) / 2
    c.setFillColor(hx(color))
    c.circle(left + SMALL_START_X[ch] * u, base + SMALL_START[ch] * u, 4.2, stroke=0, fill=1)


def lines3(c, x0, x1, base, u):
    """Ascender (light) / x-height (dashed) / baseline - for rows that have no descenders."""
    c.saveState()
    c.setLineWidth(1)
    c.setStrokeColor(hx("#D5DEEF"))
    c.line(x0, base + 2 * u, x1, base + 2 * u)
    c.setStrokeColor(hx("#8FA6CC"))
    c.setLineWidth(1.5)
    c.line(x0, base, x1, base)
    c.setDash(3, 3)
    c.setLineWidth(1)
    c.line(x0, base + u, x1, base + u)
    c.restoreState()


def dot(c, ctx, x, y):
    c.setFillColor(hx(ctx.color))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(2)
    c.circle(x, y, 7, stroke=1, fill=1)


def pic_v(c, ctx, x, y_top, w, h, wd: Word, show_en=True, main_text=None):
    """Picture card: icon on top, word(s) underneath."""
    card_box(c, x, y_top - h, w, h, ctx.color)
    tb = 34 if show_en else 24
    size = min(w - 14, h - tb - 6)
    icons.draw_object(c, wd.slug, x + (w - size) / 2, y_top - h + tb, size)
    text(c, main_text or wd.main, x + w / 2, y_top - h + (21 if show_en else 8), cfg.F_BOLD, 12, cfg.NAVY, "center", max_width=w - 10)
    if show_en:
        text(c, wd.sub, x + w / 2, y_top - h + 8, cfg.F_IT, 8.3, cfg.GREY, "center", max_width=w - 10)


def pic_h(c, ctx, x, y_top, w, h, wd: Word):
    """Picture card: icon left, word(s) right."""
    card_box(c, x, y_top - h, w, h, ctx.color)
    size = h - 12
    icons.draw_object(c, wd.slug, x + 6, y_top - h + 6, size)
    tx = x + size + 14
    text(c, wd.main, tx, y_top - h / 2 + 2, cfg.F_BOLD, 14, cfg.NAVY, max_width=w - (tx - x) - 8)
    text(c, wd.sub, tx, y_top - h / 2 - 11, cfg.F_IT, 8.8, cfg.GREY, max_width=w - (tx - x) - 8)


def blank_card(c, ctx, x, y_top, w, h, wd: Word, dashed=False):
    """Picture + the word with its FIRST letter missing (a box to write it in)."""
    if dashed:
        c.setFillColor(hx("#FFFFFF"))
        dashed_rrect(c, x, y_top - h, w, h, 12, cfg.NAVY, 1.6)
    else:
        card_box(c, x, y_top - h, w, h, ctx.color)
    size = min(h - 14, 60)
    icons.draw_object(c, wd.slug, x + 7, y_top - h / 2 - size / 2, size)
    bx, bw, bh = x + size + 14, 30, 38
    c.setFillColor(hx("#FFFFFF"))
    dashed_rrect(c, bx, y_top - h / 2 - bh / 2, bw, bh, 8, ctx.color, 1.8)
    rest = wd.main[1:]
    text(c, rest, bx + bw + 6, y_top - h / 2 - 7, cfg.F_BOLD, 20, cfg.NAVY, max_width=x + w - (bx + bw + 6) - 6)


def model_trace_row(c, ctx, label: str, y_top: float, h: float = 96, u_model: float = 30, u_strip: float = 26):
    """Model (solid, on 4 lines) + strip with 2 trace cells and 1 write cell. Returns (strip_right_x, mid_y)."""
    mw = 100
    card_box(c, X0, y_top - h, mw, h, ctx.color)
    base = y_top - h + 33
    _small_lines(c, X0 + 6, X0 + mw - 6, base, u_model)
    ww = word_width(label, u_model)
    draw_word(c, label, X0 + (mw - ww) / 2, base, u_model, "solid", ctx.color)
    sx, sw = X0 + mw + 8, 178
    _strip(c, sx, y_top - h, sw, h)
    sb = y_top - h + 36
    _small_lines(c, sx + 6, sx + sw - 6, sb, u_strip)
    cell = sw / 3
    for k in range(3):
        cx = sx + k * cell
        if k < 2:
            ww = word_width(label, u_strip)
            draw_word(c, label, cx + (cell - ww) / 2, sb, u_strip, "trace", numbers=(k == 0))
        else:
            start_dot(c, label, cx, cell, sb, u_strip, ctx.color)
    return sx + sw, y_top - h / 2


# ====================================================================== A: vowels
def page_a(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Ucapkan bunyi vokal, tebalkan huruf, lalu cocokkan dengan gambarnya.",
                "Say each vowel sound, trace the letter, then match it to its picture.")
    by_v = {ctx.w(k).initial_letter: ctx.w(k) for k in ctx.content}
    vowels = "aiueo"
    order = derange(list(vowels), ctx.rng)
    top, h, step = TOP - 40, 96, 104
    for i, v in enumerate(vowels):
        y = top - i * step
        ex, my = model_trace_row(c, ctx, v, y, h)
        dot(c, ctx, ex, my)
        px, pw = X0 + AVAIL_W - 140, 140
        pic_v(c, ctx, px, y, pw, h, by_v[order[i]])
        dot(c, ctx, px, my)
    footer(c, ctx)


# ====================================================================== B: beginning sounds A-F (circle)
def page_b(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Sebutkan nama gambar, lalu lingkari huruf bunyi awalnya.",
                "Say each picture name, then circle the letter of its beginning sound.")
    pool = list(cfg.PHONICS_LETTER_RANGES["B"])
    top, h = TOP - 40, 80
    for i, k in enumerate(ctx.content):
        wd = ctx.w(k)
        y = top - i * 88
        pic_h(c, ctx, X0, y, 170, h, wd)
        text(c, "Bunyi awal?", X0 + 182, y - 34, cfg.F_BOLD, 9, cfg.NAVY)
        text(c, "First sound?", X0 + 182, y - 46, cfg.F_IT, 8, cfg.GREY)
        ch = [wd.initial_letter] + ctx.rng.sample([l for l in pool if l != wd.initial_letter], 2)
        ctx.rng.shuffle(ch)
        for j, l in enumerate(ch):
            bx = X0 + 262 + j * 80
            card_box(c, bx, y - h + 8, 70, 64, ctx.color, fill="#FFFFFF", lw=2, r=12)
            text(c, l, bx + 35, y - h + 26, cfg.F_BOLD, 30, cfg.NAVY, "center")
    footer(c, ctx)


# ====================================================================== C: G-L (match + write first letter)
def page_c(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Cocokkan gambar dengan huruf awalnya.", "Match each picture to its first letter.")
    words = [ctx.w(k) for k in ctx.content]
    letters = derange([w.initial_letter for w in words], ctx.rng)
    top, h, step = TOP - 40, 46, 52
    for i, wd in enumerate(words):
        y = top - i * step
        pic_h(c, ctx, X0, y, 170, h, wd)
        bx = X0 + AVAIL_W - 80
        card_box(c, bx, y - h, 80, h, ctx.color, fill="#FFFFFF", lw=2, r=12)
        text(c, letters[i], bx + 40, y - h + 12, cfg.F_BOLD, 26, cfg.NAVY, "center")
        dot(c, ctx, X0 + 170, y - h / 2)
        dot(c, ctx, bx, y - h / 2)
    y2 = top - 6 * step - 6
    instruction(c, ctx, "Tulis huruf awal katanya.", "Write the first letter of each word.", y=y2)
    cw = (AVAIL_W - 16) / 3
    for i, wd in enumerate(words):
        r, k = divmod(i, 3)
        blank_card(c, ctx, X0 + k * (cw + 8), y2 - 34 - r * 86, cw, 78, wd)
    footer(c, ctx)


# ====================================================================== D: M-R (sort + complete)
def page_d(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tulis huruf awal, gunting, lalu tempel di kotak huruf.",
                "Write the first letter, cut, then paste in the matching box.")
    words = [ctx.w(k) for k in ctx.content]
    shuffled = words[:]
    ctx.rng.shuffle(shuffled)
    cw = (AVAIL_W - 16) / 3
    top = TOP - 40
    scissors(c, X0 + AVAIL_W - 40, TOP - 12, 1.0)
    for i, wd in enumerate(shuffled):
        r, k = divmod(i, 3)
        blank_card(c, ctx, X0 + k * (cw + 8), top - r * 108, cw, 100, wd, dashed=True)
    y2 = top - 2 * 108 - 4
    instruction(c, ctx, "Tempel gambar di kotak yang huruf awalnya sama.", "Paste each picture in the box with the same first letter.", y=y2)
    for i, wd in enumerate(words):
        r, k = divmod(i, 3)
        x, y = X0 + k * (cw + 8), y2 - 34 - r * 120
        col = cfg.SWATCHES[(i + 4) % len(cfg.SWATCHES)]
        card_box(c, x, y - 112, cw, 112, col)
        text(c, wd.initial_letter, x + 34, y - 62, cfg.F_BOLD, 44, cfg.NAVY, "center")
        dashed_rrect(c, x + 66, y - 102, cw - 76, 92, 10, cfg.GREY)
    footer(c, ctx)


# ====================================================================== E: S-Z (match + complete)
def page_e(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tarik garis dari gambar ke huruf awalnya.", "Draw a line from each picture to its first letter.")
    words = [ctx.w(k) for k in ctx.content]
    top = TOP - 40
    cw = (AVAIL_W - 30) / 4
    for b in range(2):
        grp = words[b * 4:(b + 1) * 4]
        lets = derange([w.initial_letter for w in grp], ctx.rng)
        y = top - b * 156
        for k, wd in enumerate(grp):
            x = X0 + k * (cw + 10)
            pic_v(c, ctx, x, y, cw, 70, wd, show_en=False)
            dot(c, ctx, x + cw / 2, y - 70)
            ly = y - 70 - 46
            card_box(c, x, ly - 40, cw, 40, ctx.color, fill="#FFFFFF", lw=2, r=12)
            text(c, lets[k], x + cw / 2, ly - 40 + 10, cfg.F_BOLD, 26, cfg.NAVY, "center")
            dot(c, ctx, x + cw / 2, ly)
    y2 = top - 2 * 156 - 6
    instruction(c, ctx, "Lengkapi katanya dengan huruf awal.", "Complete each word with its first letter.", y=y2)
    cw3 = (AVAIL_W - 16) / 3
    for i, wd in enumerate(words):
        r, k = divmod(i, 3)
        blank_card(c, ctx, X0 + k * (cw3 + 8), y2 - 34 - r * 58, cw3, 52, wd)
    x, y = X0 + 2 * (cw3 + 8), y2 - 34 - 2 * 58
    card_box(c, x, y - 52, cw3, 52, ctx.color, fill="#FFFFFF", lw=2, r=12)
    text(c, "Hebat!  Great!", x + cw3 / 2, y - 30, cfg.F_BOLD, 13, ctx.color, "center")
    footer(c, ctx)


# ====================================================================== F: basic syllables
def page_f(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan suku kata, bunyikan, lalu cocokkan dengan gambarnya.",
                "Trace each syllable, sound it out, then match it to its picture.")
    sylls = list(ctx.content.keys())
    order = derange(sylls, ctx.rng)
    top, h, step = TOP - 40, 96, 104
    for i, sy in enumerate(sylls):
        y = top - i * step
        ex, my = model_trace_row(c, ctx, sy, y, h, u_model=30, u_strip=22)
        dot(c, ctx, ex, my)
        wd = ctx.w(ctx.content[order[i]])
        px, pw = X0 + AVAIL_W - 140, 140
        pic_v(c, ctx, px, y, pw, h, wd, main_text=" - ".join(syl_of(wd)))
        dot(c, ctx, px, my)
    footer(c, ctx)


# ====================================================================== G: more syllables + join
def compose_row(c, ctx, wd: Word, y_top: float, h: float = 50):
    card_box(c, X0, y_top - h, 70, h, ctx.color)
    icons.draw_object(c, wd.slug, X0 + 15, y_top - h + 5, h - 10)
    syl = syl_of(wd)
    chips = syl[:]
    ctx.rng.shuffle(chips)
    if chips == syl:
        chips.reverse()
    x = X0 + 84
    for s in chips:
        c.setFillColor(hx(cfg.LIGHT))
        c.setStrokeColor(hx(ctx.color))
        c.setLineWidth(2)
        c.roundRect(x, y_top - h / 2 - 17, 54, 34, 9, stroke=1, fill=1)
        text(c, s, x + 27, y_top - h / 2 - 6, cfg.F_BOLD, 15, cfg.NAVY, "center")
        x += 60
    c.setFillColor(hx(ctx.color))
    p = c.beginPath()
    p.moveTo(x + 4, y_top - h / 2 - 8)
    p.lineTo(x + 20, y_top - h / 2)
    p.lineTo(x + 4, y_top - h / 2 + 8)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    x += 32
    for _ in syl:
        c.setFillColor(hx("#FFFFFF"))
        dashed_rrect(c, x, y_top - h / 2 - 20, 66, 40, 9, ctx.color, 1.8)
        x += 72


def page_g(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tebalkan suku kata, lalu susun menjadi kata.", "Trace each syllable, then join the syllables into a word.")
    sylls = ["ka", "la", "ma", "na", "sa"]
    top, h, step, u = TOP - 40, 52, 57, 20
    for i, sy in enumerate(sylls):
        y = top - i * step
        base = y - h + 9
        card_box(c, X0, y - h, 90, h, ctx.color)
        lines3(c, X0 + 6, X0 + 84, base, u)
        draw_word(c, sy, X0 + (90 - word_width(sy, u)) / 2, base, u, "solid", ctx.color)
        sx = X0 + 96
        sw = AVAIL_W - 96
        _strip(c, sx, y - h, sw, h)
        lines3(c, sx + 6, sx + sw - 6, base, u)
        cell = sw / 4
        for k in range(4):
            cx = sx + k * cell
            if k < 2:
                draw_word(c, sy, cx + (cell - word_width(sy, u)) / 2, base, u, "trace", numbers=(k == 0))
            elif k == 2:
                start_dot(c, sy, cx, cell, base, u, ctx.color)
        c.setStrokeColor(hx(ctx.color))
        c.setLineWidth(1.4)
        c.setDash(3, 3)
        c.line(sx + 2 * cell, y - h + 5, sx + 2 * cell, y - 5)
        c.setDash([], 0)
    y2 = top - 5 * step - 4
    instruction(c, ctx, "Susun suku kata menjadi kata. Tulis di kotak.", "Join the syllables to make a word. Write them in the boxes.", y=y2)
    for i, k in enumerate(ctx.content.values()):
        compose_row(c, ctx, ctx.w(k), y2 - 34 - i * 54, 50)
    footer(c, ctx)


# ====================================================================== H: build two-syllable words (cut + paste)
def page_h(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Gunting kartu suku kata.", "Cut out the syllable cards.")
    scissors(c, X0 + AVAIL_W - 40, TOP - 12, 1.0)
    words = [ctx.w(k) for k in ctx.content]
    cards = [s for wd in words for s in syl_of(wd)]
    ctx.rng.shuffle(cards)
    top = TOP - 40
    cw = (AVAIL_W - 30) / 4
    for i, s in enumerate(cards):
        r, k = divmod(i, 4)
        x, y = X0 + k * (cw + 10), top - r * 60
        c.setFillColor(hx("#FFFFFF"))
        dashed_rrect(c, x, y - 52, cw, 52, 10, cfg.NAVY, 1.6)
        text(c, s, x + cw / 2, y - 36, cfg.F_BOLD, 26, cfg.NAVY, "center")
    y2 = top - 2 * 60 - 6
    instruction(c, ctx, "Tempel dua suku kata untuk menyusun nama gambar, lalu tulis katanya.",
                "Paste two syllables to build each picture name, then write the word.", y=y2)
    h, step = 68, 74
    for i, wd in enumerate(words):
        y = y2 - 34 - i * step
        card_box(c, X0, y - h, 80, h, ctx.color)
        icons.draw_object(c, wd.slug, X0 + 10, y - h + 8, 60)
        x1 = X0 + 92
        for j in range(2):
            c.setFillColor(hx("#FFFFFF"))
            dashed_rrect(c, x1 + j * 114, y - h + 6, 92, h - 12, 10, ctx.color, 1.8)
        text(c, "+", x1 + 92 + 11, y - h / 2 - 8, cfg.F_BOLD, 20, cfg.NAVY, "center")
        text(c, "=", x1 + 2 * 114 - 8, y - h / 2 - 8, cfg.F_BOLD, 20, cfg.NAVY, "center")
        sx = X0 + 322
        sw = AVAIL_W - 322
        _strip(c, sx, y - h, sw, h)
        _small_lines(c, sx + 6, sx + sw - 6, y - h + 28, 20)
    footer(c, ctx)


# ====================================================================== I: bilingual picture-word match
def page_i(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tarik garis dari gambar ke kata Indonesia dan Inggrisnya, lalu tebalkan kata-katanya.",
                "Draw a line from each picture to its Indonesian and English words, then trace the words.")
    words = [ctx.w(k) for k in ctx.content]
    order = derange(list(range(len(words))), ctx.rng)
    top, h, step = TOP - 40, 92, 104
    rx, rw = X0 + AVAIL_W - 280, 280
    for i, wd in enumerate(words):
        y = top - i * step
        pic_v(c, ctx, X0, y, 110, h, wd, show_en=False)
        dot(c, ctx, X0 + 110, y - h / 2)
        tw = words[order[i]]
        card_box(c, rx, y - h, rw, h, ctx.color)
        dot(c, ctx, rx, y - h / 2)
        for j, (tag, word, tcol) in enumerate((("ID", tw.word_id.lower(), ctx.color), ("EN", tw.word_en.lower(), cfg.SWATCHES[1]))):
            by = y - 36 - j * 40
            c.setFillColor(hx(tcol))
            c.roundRect(rx + 12, by - 4, 26, 18, 6, stroke=0, fill=1)
            text(c, tag, rx + 25, by + 2, cfg.F_BOLD, 8.5, "#FFFFFF", "center")
            size = fit_size(word, cfg.F_MED, 28, rw - 62)
            dashed_text(c, word, rx + 46, by, cfg.F_MED, size)
    footer(c, ctx)


# ====================================================================== J: rhyming words
def page_j(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Tarik garis antara dua gambar yang bunyi akhirnya sama.",
                "Draw a line between the two pictures whose words end with the same sound.")
    pairs = ctx.content
    left = [ctx.w(a) for a, _, _ in pairs]
    right = [ctx.w(b) for _, b, _ in pairs]
    order = derange(list(range(len(pairs))), ctx.rng)
    top, h, step = TOP - 40, 90, 100
    cw = 150
    for i in range(len(pairs)):
        y = top - i * step
        pic_v(c, ctx, X0 + 20, y, cw, h, left[i], show_en=False)
        dot(c, ctx, X0 + 20 + cw, y - h / 2)
        rx = X0 + AVAIL_W - 20 - cw
        pic_v(c, ctx, rx, y, cw, h, right[order[i]], show_en=False)
        dot(c, ctx, rx, y - h / 2)
    y2 = top - len(pairs) * step - 2
    instruction(c, ctx, "Tebalkan dan tulis akhiran katanya.", "Trace and write the ending of the rhyming words.", y=y2)
    u, rh = 18, 62
    for i, (a, b, ending) in enumerate(pairs):
        y = y2 - 34 - i * 66
        text(c, f"{a}  \u2022  {b}", X0 + 4, y - 36, cfg.F_BOLD, 13, cfg.NAVY, max_width=160)
        sx = X0 + 170
        sw = AVAIL_W - 170
        _strip(c, sx, y - rh, sw, rh)
        base = y - rh + 22
        _small_lines(c, sx + 6, sx + sw - 6, base, u)
        cell = sw / 4
        for k in range(4):
            cx = sx + k * cell
            ww = word_width(ending, u)
            if k < 3:
                draw_word(c, ending, cx + (cell - ww) / 2, base, u, "trace", numbers=(k == 0))
            else:
                start_dot(c, ending, cx, cell, base, u, ctx.color)
    footer(c, ctx)


PHONICS_FUNCS = {"A": page_a, "B": page_b, "C": page_c, "D": page_d, "E": page_e,
                 "F": page_f, "G": page_g, "H": page_h, "I": page_i, "J": page_j}
