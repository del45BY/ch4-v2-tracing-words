"""Templates A-E. Each takes (canvas, Ctx) and draws ONE A4 page.

All wording comes from config.TEMPLATES + {PLACEHOLDERS}; all artwork from icons.py.
"""
from reportlab.lib import colors

from . import config as cfg
from .database import Item
from .linguistics import article_phrase, syllabify_id
from .modules import (H, M, W, card_box, dashed_rrect, dashed_text, fit_size, footer, header,
                      hx, instruction, item_card, scissors, text)
from . import icons
from reportlab.pdfbase.pdfmetrics import stringWidth

TOP = cfg.CONTENT_TOP


# ====================================================================== A: matching
def template_a(c, ctx):
    header(c, ctx)
    wd = ctx.row.wording
    instruction(c, ctx,
                f"Draw a line from the {wd['obj_noun_en']} to its {wd['rel_noun_en']}.",
                f"Tarik garis dari {wd['obj_noun_id']} ke {wd['rel_noun_id']}.")
    pairs = [(ctx.obj, ctx.rel)] + ctx.pick_pairs(2)
    n = len(pairs)
    left = list(pairs)
    ctx.rng.shuffle(left)
    k = ctx.rng.randint(1, n - 1)  # rotate so no pair lines up straight across
    right = left[k:] + left[:k]
    card_w, card_h, row_h = 150, 168, 186
    lx, rx = M + 24, W - M - 24 - card_w
    for i in range(n):
        y_top = TOP - 40 - i * row_h
        item_card(c, ctx, lx, y_top, card_w, card_h, left[i][0])
        item_card(c, ctx, rx, y_top, card_w, card_h, right[i][1])
        for xx in (lx + card_w, rx):
            c.setFillColor(hx(ctx.color))
            c.setStrokeColor(hx(cfg.NAVY))
            c.setLineWidth(2.2)
            c.circle(xx, y_top - card_h / 2, 8, stroke=1, fill=1)
    footer(c, ctx)


# ====================================================================== B: vocabulary + clap + trace
def _step_strip(c, ctx, y):
    steps = [("Lihat & sebutkan", "Look and say"), ("Tepuk suku katanya", "Clap the syllables"), ("Tebalkan hurufnya", "Trace the letters")]
    w = (W - 2 * M - 16) / 3
    for i, (idn, en) in enumerate(steps):
        x = M + 8 + i * w
        c.setFillColor(hx(ctx.color))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.circle(x + 13, y - 20, 12, stroke=1, fill=1)
        text(c, str(i + 1), x + 13, y - 25, cfg.F_BOLD, 13, "#FFFFFF", "center")
        text(c, idn, x + 32, y - 17, cfg.F_BOLD, 9.5, cfg.NAVY)
        text(c, en, x + 32, y - 29, cfg.F_IT, 8.5, cfg.GREY)


def _vocab_card(c, ctx, y_top, item: Item, en_raw, id_raw):
    x, w, h = M + 4, W - 2 * M - 8, 250
    card_box(c, x, y_top - h, w, h, ctx.color)
    icons.draw_object(c, item.slug, x + 16, y_top - h / 2 - 78, 156)
    tx = x + 196
    avail = w - 196 - 16
    g = ctx.glossary.get(id_raw.lower() if False else en_raw.lower(), {})
    sentence_en = f"This is {article_phrase(en_raw, g.get('countable', True))}."
    sentence_id = f"Ini adalah {id_raw.lower()}."
    text(c, item.en, tx, y_top - 48, cfg.F_BOLD, 34, cfg.NAVY, max_width=avail)
    text(c, item.id, tx, y_top - 80, cfg.F_MED, 24, ctx.color, max_width=avail)
    text(c, sentence_en + "  \u2022  " + sentence_id, tx, y_top - 100, cfg.F_IT, 9, cfg.GREY, max_width=avail)
    # clap boxes
    syl = syllabify_id(id_raw, g.get("syllables"))
    text(c, "Tepuk / Clap", tx, y_top - 122, cfg.F_MED, 8, cfg.GREY)
    size, pad, gap = 13, 9, 6
    widths = [stringWidth(s, cfg.F_BOLD, size) + 2 * pad for s in syl]
    while sum(widths) + gap * (len(syl) - 1) > avail and size > 8:
        size -= 1
        widths = [stringWidth(s, cfg.F_BOLD, size) + 2 * pad for s in syl]
    bx = tx
    for s, bw in zip(syl, widths):
        c.setFillColor(hx("#FFFFFF"))
        c.setStrokeColor(hx(ctx.color))
        c.setLineWidth(2)
        c.roundRect(bx, y_top - 156, bw, 26, 8, stroke=1, fill=1)
        text(c, s, bx + bw / 2, y_top - 147, cfg.F_BOLD, size, cfg.NAVY, "center")
        bx += bw + gap
    # trace line
    word = en_raw.lower()
    tsize = fit_size(word, cfg.F_MED, 46, avail)
    base = y_top - 216
    c.setStrokeColor(hx(cfg.LINE))
    c.setLineWidth(1)
    c.line(tx, base, tx + avail, base)
    c.setDash(2, 3)
    c.line(tx, base + tsize * 0.55, tx + avail, base + tsize * 0.55)
    c.setDash([], 0)
    dashed_text(c, word, tx + 4, base, cfg.F_MED, tsize, cfg.GREY)


def template_b(c, ctx):
    header(c, ctx)
    _step_strip(c, ctx, TOP + 4)
    top = TOP - 52
    _vocab_card(c, ctx, top, ctx.obj, ctx.row.object_en, ctx.row.object_id)
    _vocab_card(c, ctx, top - 264, ctx.rel, ctx.row.relation_en, ctx.row.relation_id)
    footer(c, ctx)


# ====================================================================== C: find and circle
def _circle_section(c, ctx, y_top, target: Item, choices, verb_en, verb_id):
    instruction(c, ctx, f"Circle the {target.en.lower()}.", f"Lingkari {target.id.lower()}.", y=y_top)
    # "look for" preview, top-right
    px, pw = W - M - 8 - 150, 150
    text(c, "Cari ini / Look for:", px, y_top - 8, cfg.F_MED, 8, cfg.GREY)
    card_box(c, W - M - 8 - 52, y_top - 52, 52, 52, ctx.color, r=10, lw=2)
    icons.draw_object(c, target.slug, W - M - 8 - 46, y_top - 46, 40)
    # three big answer cards
    cw, gap = 150, 28
    x0 = (W - (3 * cw + 2 * gap)) / 2
    for i, it in enumerate(choices):
        item_card(c, ctx, x0 + i * (cw + gap), y_top - 62, cw, 160, it, show_words=False, icon_size=130)


def template_c(c, ctx):
    header(c, ctx)
    rel_choices = [ctx.rel] + ctx.pick_items("relation", 2)
    obj_choices = [ctx.obj] + ctx.pick_items("object", 2, avoid={i.slug for i in rel_choices})
    ctx.rng.shuffle(rel_choices)
    ctx.rng.shuffle(obj_choices)
    _circle_section(c, ctx, TOP, ctx.rel, rel_choices, "", "")
    c.setStrokeColor(hx(cfg.LINE))
    c.setDash(4, 4)
    c.line(M + 8, TOP - 250, W - M - 8, TOP - 250)
    c.setDash([], 0)
    _circle_section(c, ctx, TOP - 276, ctx.obj, obj_choices, "", "")
    footer(c, ctx)


# ====================================================================== D: cut and paste
def template_d(c, ctx):
    header(c, ctx)
    instruction(c, ctx, "Cut the pictures and paste them in the correct place.",
                "Gunting gambarnya, lalu tempel di tempat yang benar.")
    # cut zone
    zx, zw, zh = M + 8, W - 2 * M - 16, 220
    zy = TOP - 40 - zh
    dashed_rrect(c, zx, zy, zw, zh, 16, cfg.NAVY, 1.8)
    scissors(c, zx + 22, zy + zh - 22, 1.2)
    text(c, "Gunting / Cut", zx + 52, zy + zh - 25, cfg.F_BOLD, 10, cfg.NAVY)
    sz = 150
    for x, it in ((zx + zw / 4 - sz / 2, ctx.rel), (zx + 3 * zw / 4 - sz / 2, ctx.obj)):
        icons.draw_object(c, it.slug, x, zy + 14, sz)
    # paste zone: frames are in the OPPOSITE order to the cut pictures
    fw, fh, gap = 240, 276, 20
    fy = zy - 26 - fh
    fx0 = (W - (2 * fw + gap)) / 2
    for i, it in enumerate((ctx.obj, ctx.rel)):
        x = fx0 + i * (fw + gap)
        card_box(c, x, fy, fw, fh, ctx.color)
        text(c, it.en, x + fw / 2, fy + fh - 34, cfg.F_BOLD, 22, cfg.NAVY, "center", max_width=fw - 20)
        text(c, it.id, x + fw / 2, fy + fh - 56, cfg.F_MED, 14, ctx.color, "center", max_width=fw - 20)
        dashed_rrect(c, x + 28, fy + 22, fw - 56, fw - 56 - 4, 14, cfg.GREY)
        text(c, "Tempel di sini / Paste here", x + fw / 2, fy + 8, cfg.F_IT, 7.5, cfg.GREY, "center")
    footer(c, ctx)


# ====================================================================== E: coloring
def template_e(c, ctx):
    header(c, ctx)
    instruction(c, ctx, f"Color the {ctx.row.object_en.lower()}.", f"Warnai {ctx.row.object_id.lower()}.")
    big = 330
    icons.draw_object(c, ctx.obj.slug, (W - big) / 2, TOP - 40 - big, big, outline=True)
    y = TOP - 40 - big - 24
    text(c, f"{ctx.obj.en}  \u2022  {ctx.obj.id}", W / 2, y, cfg.F_BOLD, 18, cfg.NAVY, "center", max_width=W - 2 * M)
    # small second picture + palette hint
    small = 150
    sy = y - 24 - small
    card_box(c, M + 8, sy - 8, 200, small + 16, ctx.color, fill="#FFFFFF")
    icons.draw_object(c, ctx.rel.slug, M + 8 + 25, sy, small, outline=True)
    text(c, f"Warnai {ctx.rel.id.lower()} juga!", M + 24 + 200 + 8, sy + small - 20, cfg.F_BOLD, 11, cfg.NAVY)
    text(c, f"Color the {ctx.rel.en.lower()} too!", M + 24 + 200 + 8, sy + small - 35, cfg.F_IT, 9.5, cfg.GREY)
    for i, col in enumerate(cfg.SWATCHES):
        c.setFillColor(hx(col))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.circle(M + 24 + 200 + 20 + (i % 4) * 36, sy + 62 - (i // 4) * 36, 13, stroke=1, fill=1)
    text(c, "Warna / Colors", M + 24 + 200 + 8, sy + small - 56, cfg.F_MED, 8, cfg.GREY)
    footer(c, ctx)


TEMPLATE_FUNCS = {"A": template_a, "B": template_b, "C": template_c, "D": template_d, "E": template_e}
