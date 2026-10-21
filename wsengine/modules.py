"""Reusable worksheet modules: Header, Footer, Parent tip, Cards, text helpers."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from . import config as cfg
from . import icons
from .database import Item, Row, fill_placeholders
from .linguistics import capitalise

W, H, M = cfg.PAGE_W, cfg.PAGE_H, cfg.MARGIN
hx = colors.HexColor


# ------------------------------------------------------------------ context
@dataclass
class Ctx:
    row: Row
    all_rows: list[Row]
    glossary: dict
    template: str
    page_no: int
    page_total: int
    rng: random.Random = field(default=None)

    @property
    def color(self):
        return cfg.TEMPLATE_COLORS[self.template]

    @property
    def spec(self):
        return cfg.TEMPLATES[self.template]

    def fill(self, text):
        return fill_placeholders(text, self.row, self.glossary)

    # -- own items
    @property
    def obj(self) -> Item:
        return Item(self.row.object_slug, capitalise(self.row.object_en), capitalise(self.row.object_id))

    @property
    def rel(self) -> Item:
        return Item(self.row.relation_slug, capitalise(self.row.relation_en), capitalise(self.row.relation_id))

    # -- distractors come from OTHER rows (same category first), so no extra data is needed
    def _others(self):
        r = self.row
        same = [o for o in self.all_rows if o.id != r.id and o.category == r.category]
        diff = [o for o in self.all_rows if o.id != r.id and o.category != r.category]
        self.rng.shuffle(same)
        self.rng.shuffle(diff)
        return same + diff

    def pick_pairs(self, n):
        used = {self.row.object_slug, self.row.relation_slug}
        out = []
        for o in self._others():
            a = Item(o.object_slug, capitalise(o.object_en), capitalise(o.object_id))
            b = Item(o.relation_slug, capitalise(o.relation_en), capitalise(o.relation_id))
            if {a.slug, b.slug} & used or icons.art_source(a.slug) == "placeholder" or icons.art_source(b.slug) == "placeholder":
                continue
            used |= {a.slug, b.slug}
            out.append((a, b))
            if len(out) == n:
                break
        return out

    def pick_items(self, kind, n, avoid=()):
        """n distractor Items of kind 'object' or 'relation'."""
        used = {self.row.object_slug, self.row.relation_slug, *avoid}
        out = []
        for o in self._others():
            it = (Item(o.object_slug, capitalise(o.object_en), capitalise(o.object_id)) if kind == "object"
                  else Item(o.relation_slug, capitalise(o.relation_en), capitalise(o.relation_id)))
            if it.slug in used or icons.art_source(it.slug) == "placeholder":
                continue
            used.add(it.slug)
            out.append(it)
            if len(out) == n:
                break
        return out


# ------------------------------------------------------------------ text helpers
def fit_size(text, font, max_size, max_width, min_size=5.5):
    w = stringWidth(text, font, max_size)
    return max_size if w <= max_width else max(min_size, max_size * max_width / w)


def text(c, s, x, y, font, size, color=cfg.NAVY, align="left", max_width=None):
    if max_width:
        size = fit_size(s, font, size, max_width)
    c.setFillColor(hx(color))
    c.setFont(font, size)
    {"left": c.drawString, "center": c.drawCentredString, "right": c.drawRightString}[align](x, y, s)


def dashed_text(c, s, x, y, font, size, color=cfg.GREY):
    """Outline-only letters with a dashed stroke = 'trace the letters'."""
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setTextRenderMode(1)
    t.textOut(s)
    c.saveState()
    c.setStrokeColor(hx(color))
    c.setLineWidth(1.3)
    c.setDash(3, 3)
    c.drawText(t)
    c.restoreState()


def dashed_rrect(c, x, y, w, h, r=14, color=cfg.GREY, lw=1.6):
    c.saveState()
    c.setStrokeColor(hx(color))
    c.setLineWidth(lw)
    c.setDash(6, 4)
    c.roundRect(x, y, w, h, r, stroke=1, fill=0)
    c.restoreState()


def card_box(c, x, y, w, h, color, fill=cfg.LIGHT, lw=2.4, r=16):
    c.setFillColor(hx(fill))
    c.setStrokeColor(hx(color))
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)


# ------------------------------------------------------------------ Header module
def header(c, ctx: Ctx):
    col = ctx.color
    # page frame
    c.setStrokeColor(hx(col))
    c.setLineWidth(3)
    c.roundRect(14, 14, W - 28, H - 28, 18, stroke=1, fill=0)
    # Name / Date
    y = H - 50
    text(c, "Nama / Name", M + 8, y, cfg.F_MED, 9, cfg.GREY)
    c.setStrokeColor(hx(cfg.LINE))
    c.setLineWidth(1.2)
    c.line(M + 78, y - 2, 330, y - 2)
    text(c, "Tanggal / Date", 350, y, cfg.F_MED, 9, cfg.GREY)
    c.line(430, y - 2, W - M - 8, y - 2)
    # template badge + title
    cx, cy = M + 30, H - 92
    c.setFillColor(hx(col))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(2.4)
    c.circle(cx, cy, 21, stroke=1, fill=1)
    text(c, ctx.template, cx, cy - 8, cfg.F_BOLD, 22, "#FFFFFF", "center")
    title_en, title_id = ctx.fill(ctx.spec["title_en"]), ctx.fill(ctx.spec["title_id"])
    id_first = ctx.spec.get("primary") == "id"
    if id_first:  # Indonesian-first series: Indonesian title large, English below
        title_en, title_id = title_id, title_en
    tx, avail = cx + 32, W - M - 140 - (cx + 32)
    text(c, title_en, tx, cy - 2, cfg.F_BOLD, 25, cfg.NAVY, max_width=avail)
    text(c, title_id, tx, cy - 22, cfg.F_MED, 13, col, max_width=avail)
    # age pill
    pw = 112
    c.setFillColor(hx(col))
    c.roundRect(W - M - 8 - pw, cy - 4, pw, 34, 12, stroke=0, fill=1)
    text(c, cfg.BRAND["age_en"], W - M - 8 - pw / 2, cy + 14, cfg.F_BOLD, 10, "#FFFFFF", "center")
    text(c, cfg.BRAND["age_id"], W - M - 8 - pw / 2, cy + 3, cfg.F_MED, 8, "#FFFFFF", "center")
    # learning objective
    first, second = ("Tujuan:  " + ctx.spec["goal_id"], "Goal:  " + ctx.spec["goal_en"]) if id_first else \
                    ("Goal:  " + ctx.spec["goal_en"], "Tujuan:  " + ctx.spec["goal_id"])
    one_line = first + "  \u2022  " + second
    avail_w = W - 2 * M - 16
    if fit_size(one_line, cfg.F_IT, 8.5, avail_w) >= 7.2:      # fits comfortably on one line
        text(c, one_line, M + 8, H - 132, cfg.F_IT, 8.5, cfg.GREY, max_width=avail_w)
        div_y = H - 140
    else:                                                      # long objective: two lines
        text(c, first, M + 8, H - 126, cfg.F_IT, 8.3, cfg.GREY, max_width=avail_w)
        text(c, second, M + 8, H - 136, cfg.F_IT, 8.3, cfg.GREY, max_width=avail_w)
        div_y = H - 143
    c.setStrokeColor(hx(cfg.LINE))
    c.setLineWidth(1)
    c.setDash(4, 4)
    c.line(M + 8, div_y, W - M - 8, div_y)
    c.setDash([], 0)


def instruction(c, ctx, en, idn, y=None, x=M + 8):
    y = y if y is not None else cfg.CONTENT_TOP
    text(c, en, x, y - 6, cfg.F_BOLD, 13, cfg.NAVY, max_width=W - 2 * M - 16)
    text(c, idn, x, y - 22, cfg.F_MED, 10.5, ctx.color, max_width=W - 2 * M - 16)


# ------------------------------------------------------------------ Footer + parent tip
def footer(c, ctx: Ctx):
    tip_en, tip_id = ctx.spec["tip_en"], ctx.spec["tip_id"]
    c.setFillColor(hx("#FFF8E6"))
    c.setStrokeColor(hx("#F5C86B"))
    c.setLineWidth(1)
    c.roundRect(M + 8, 66, W - 2 * M - 16, 28, 8, stroke=1, fill=1)
    text(c, "Tips orang tua / Parent tip:  " + tip_id, M + 16, 83, cfg.F_MED, 7.8, cfg.NAVY, max_width=W - 2 * M - 32)
    text(c, tip_en, M + 16, 72, cfg.F_IT, 7.8, cfg.GREY, max_width=W - 2 * M - 32)
    c.setStrokeColor(hx(cfg.LINE))
    c.setLineWidth(1)
    c.line(M + 8, 58, W - M - 8, 58)
    text(c, cfg.BRAND["name"] + " \u2022 " + (ctx.spec.get("series") or cfg.BRAND["tagline"]), M + 8, 46, cfg.F_BOLD, 8, cfg.NAVY)
    text(c, f"Halaman / Page {ctx.page_no} dari / of {ctx.page_total}", W - M - 8, 46, cfg.F_MED, 8, cfg.GREY, "right")
    text(c, cfg.BRAND["copyright"], M + 8, 33, cfg.F_REG, 6.5, cfg.GREY, max_width=W - 2 * M - 16)


# ------------------------------------------------------------------ cards
def item_card(c, ctx, x, y_top, w, h, item: Item, show_words=True, icon_size=108, outline=False):
    """Card with artwork on top and EN / ID words underneath."""
    card_box(c, x, y_top - h, w, h, ctx.color)
    words_h = 46 if show_words else 0
    size = min(icon_size, h - words_h - 16)
    icons.draw_object(c, item.slug, x + (w - size) / 2, y_top - h + words_h + 8, size, outline)
    if show_words:
        text(c, item.en, x + w / 2, y_top - h + 28, cfg.F_BOLD, 16, cfg.NAVY, "center", max_width=w - 16)
        text(c, item.id, x + w / 2, y_top - h + 11, cfg.F_MED, 11, ctx.color, "center", max_width=w - 16)


def scissors(c, x, y, s=1.0, color=cfg.NAVY):
    c.saveState()
    c.translate(x, y)
    c.scale(s, s)
    c.setStrokeColor(hx(color))
    c.setLineWidth(2)
    c.line(0, 0, 18, 10)
    c.line(0, 10, 18, 0)
    c.circle(-2, -1, 3.2, stroke=1, fill=0)
    c.circle(-2, 11, 3.2, stroke=1, fill=0)
    c.restoreState()
