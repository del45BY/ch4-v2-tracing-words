"""Build the PDF, then derive Preview.png, Cover.png and Thumbnail.png from it."""
from __future__ import annotations

import random
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from . import config as cfg
from . import icons
from .database import Row, fill_placeholders
from .modules import Ctx, fit_size, text
from .templates import TEMPLATE_FUNCS

hx = colors.HexColor
PDF_NAME = "English_Indonesian_Worksheet.pdf"


def build_pdf(row: Row, all_rows: list[Row], glossary: dict, out_pdf: Path, templates=None) -> None:
    templates = templates or cfg.TEMPLATE_ORDER
    c = canvas.Canvas(str(out_pdf), pagesize=(cfg.PAGE_W, cfg.PAGE_H))
    c.setTitle(f"{row.object_en} & {row.relation_en} / {row.object_id} & {row.relation_id} - Bilingual Worksheet")
    c.setAuthor(cfg.BRAND["name"])
    c.setSubject("Preschool bilingual worksheet, ages 3-5")
    for n, t in enumerate(templates, 1):
        ctx = Ctx(row, all_rows, glossary, t, n, len(templates), random.Random(f"{row.id}-{t}"))
        c.setLineJoin(1)
        c.setLineCap(1)
        TEMPLATE_FUNCS[t](c, ctx)
        c.showPage()
    c.save()


def rasterise(pdf_path: Path, dpi: int = 110) -> list[Image.Image]:
    pdf = pdfium.PdfDocument(str(pdf_path))
    imgs = [pdf[i].render(scale=dpi / 72).to_pil().convert("RGB") for i in range(len(pdf))]
    pdf.close()
    return imgs


def save_page_pngs(pages: list[Image.Image], folder: Path, templates, names: dict | None = None) -> None:
    names = names or {t: cfg.TEMPLATES[t]["name"] for t in templates}
    pages_dir = folder / "pages"
    pages_dir.mkdir(exist_ok=True)
    for im, t in zip(pages, templates):
        im.save(pages_dir / f"Page_{t}_{names[t].replace(' ', '_')}.png")


def make_preview(pages: list[Image.Image], templates, out: Path, names: dict | None = None, per_row: int = 5) -> None:
    """Contact sheet of every page, with labels (wraps after `per_row` pages)."""
    names = names or {t: cfg.TEMPLATES[t]["name"] for t in templates}
    pw = 380
    thumbs = [p.resize((pw, int(p.height * pw / p.width)), Image.LANCZOS) for p in pages]
    gap, pad, label_h = 28, 40, 44
    n_rows = -(-len(thumbs) // per_row)
    cols = min(per_row, len(thumbs))
    width = pad * 2 + cols * pw + (cols - 1) * gap
    cell_h = thumbs[0].height + label_h + gap
    height = pad * 2 + n_rows * cell_h - gap
    sheet = Image.new("RGB", (width, height), "#F4F9FF")
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(cfg.FONT_FILE_BOLD, 22) if cfg.FONT_FILE_BOLD else ImageFont.load_default()
    for i, (t, im) in enumerate(zip(templates, thumbs)):
        r, k = divmod(i, per_row)
        x, y = pad + k * (pw + gap), pad + r * cell_h
        d.rectangle([x + 6, y + 6, x + pw + 6, y + im.height + 6], fill="#D5E0F0")  # shadow
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x + pw, y + im.height], outline=cfg.TEMPLATE_COLORS[t], width=3)
        d.text((x, y + im.height + 12), f"{t}  {names[t]}", fill=cfg.NAVY, font=font)
    sheet.save(out)


def make_cover(row: Row, glossary: dict, pages: list[Image.Image], out: Path) -> None:
    """2000x2000 product cover drawn at 1000x1000 pt, then thumbnail derived from it."""
    S = 1000
    tmp = out.with_suffix(".pdf")
    c = canvas.Canvas(str(tmp), pagesize=(S, S))
    c.setFillColor(hx(cfg.LIGHT))
    c.rect(0, 0, S, S, stroke=0, fill=1)
    for (x, y, r, col) in [(80, 900, 120, "#FFE9B8"), (940, 760, 150, "#D8EEFF"), (60, 430, 90, "#FFD9E6"), (960, 380, 80, "#DDF5E7")]:
        c.setFillColor(hx(col))
        c.circle(x, y, r, stroke=0, fill=1)
    # banner pill
    c.setFillColor(hx(cfg.TEMPLATE_COLORS["A"]))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(5)
    c.roundRect(150, 910, 700, 56, 28, stroke=1, fill=1)
    text(c, "BILINGUAL WORKSHEET PACK  \u2022  ENGLISH + BAHASA INDONESIA", 500, 929, cfg.F_BOLD, 21, "#FFFFFF", "center", max_width=660)
    # titles
    en = f"{row.object_en} & {row.relation_en}"
    idn = f"{row.object_id} & {row.relation_id}"
    text(c, en, 500, 830, cfg.F_BOLD, 88, cfg.NAVY, "center", max_width=900)
    text(c, idn, 500, 760, cfg.F_BOLD, 56, cfg.TEMPLATE_COLORS["D"], "center", max_width=900)
    # artwork
    icons.draw_object(c, row.object_slug, 110, 440, 340)
    icons.draw_object(c, row.relation_slug, 550, 440, 340)
    c.setFillColor(hx("#FFFFFF"))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(5)
    c.circle(500, 610, 36, stroke=1, fill=1)
    text(c, "+", 500, 593, cfg.F_BOLD, 52, cfg.NAVY, "center")
    # page thumbnails
    tw, tgap = 172, 14
    x0 = (S - (5 * tw + 4 * tgap)) / 2
    for i, p in enumerate(pages[:5]):
        th = tw * p.height / p.width
        x = x0 + i * (tw + tgap)
        c.setFillColor(hx("#D5E0F0"))
        c.roundRect(x + 5, 148 - 5, tw, th, 6, stroke=0, fill=1)
        c.drawImage(ImageReader(p), x, 148, tw, th)
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.rect(x, 148, tw, th, stroke=1, fill=0)
    # badges + brand
    c.setFillColor(hx(cfg.NAVY))
    c.roundRect(170, 70, 660, 52, 26, stroke=0, fill=1)
    text(c, "5 Worksheets  \u2022  Ages 3\u20135  \u2022  Printable A4 PDF", 500, 87, cfg.F_BOLD, 24, "#FFFFFF", "center", max_width=620)
    text(c, cfg.BRAND["name"] + " \u2022 " + cfg.BRAND["tagline"], 500, 36, cfg.F_MED, 18, cfg.GREY, "center")
    c.save()
    pdf = pdfium.PdfDocument(str(tmp))
    pdf[0].render(scale=2).to_pil().convert("RGB").save(out)
    pdf.close()
    tmp.unlink()


def make_thumbnail(cover: Path, out: Path) -> None:
    Image.open(cover).resize((600, 600), Image.LANCZOS).save(out)


def generate_row(row: Row, all_rows: list[Row], glossary: dict, out_root: Path, templates=None) -> Path:
    templates = templates or cfg.TEMPLATE_ORDER
    folder = out_root / row.folder
    folder.mkdir(parents=True, exist_ok=True)
    pdf_path = folder / PDF_NAME
    build_pdf(row, all_rows, glossary, pdf_path, templates)
    pages = rasterise(pdf_path)
    save_page_pngs(pages, folder, templates)
    make_preview(pages, templates, folder / "Preview.png")
    make_cover(row, glossary, pages, folder / "Cover.png")
    make_thumbnail(folder / "Cover.png", folder / "Thumbnail.png")
    return folder


# ====================================================================== ALPHABET SERIES (templates A-T)
def build_letters_pdf(items, out_pdf: Path, order: list[str], title: str) -> None:
    from .letters import LETTER_FUNCS, LetterCtx
    by_letter = {i.letter: i for i in items}
    c = canvas.Canvas(str(out_pdf), pagesize=(cfg.PAGE_W, cfg.PAGE_H))
    c.setTitle(f"{title} - Bilingual Worksheets")
    c.setAuthor(cfg.BRAND["name"])
    c.setSubject("Preschool alphabet worksheets, ages 3-5")
    for n, t in enumerate(order, 1):
        c.setLineJoin(1)
        c.setLineCap(1)
        LETTER_FUNCS[t](c, LetterCtx(t, n, len(order), by_letter))
        c.showPage()
    c.save()


def make_letters_cover(items, pages: list[Image.Image], out: Path, meta: dict) -> None:
    from . import strokes
    by_letter = {i.letter: i for i in items}
    S = 1000
    tmp = out.with_suffix(".pdf")
    c = canvas.Canvas(str(tmp), pagesize=(S, S))
    c.setFillColor(hx(cfg.LIGHT))
    c.rect(0, 0, S, S, stroke=0, fill=1)
    for (x, y, r, col) in [(70, 880, 130, "#FFE9B8"), (950, 700, 150, "#D8EEFF"), (50, 400, 90, "#FFD9E6"), (960, 360, 80, "#DDF5E7")]:
        c.setFillColor(hx(col))
        c.circle(x, y, r, stroke=0, fill=1)
    c.setFillColor(hx(cfg.TEMPLATE_COLORS["A"]))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(5)
    c.roundRect(130, 910, 740, 56, 28, stroke=1, fill=1)
    text(c, meta["banner"], 500, 929, cfg.F_BOLD, 21, "#FFFFFF", "center", max_width=700)
    text(c, meta["title_en"], 500, 826, cfg.F_BOLD, 86, cfg.NAVY, "center", max_width=900)
    text(c, meta["title_id"], 500, 756, cfg.F_BOLD, 56, cfg.TEMPLATE_COLORS["D"], "center", max_width=900)
    tile, gap = 270, 40
    x0 = (S - (3 * tile + 2 * gap)) / 2
    cols = [cfg.TEMPLATE_COLORS["A"], cfg.TEMPLATE_COLORS["D"], cfg.TEMPLATE_COLORS["C"]]
    for i, ch in enumerate(meta["tiles"]):
        x, y = x0 + i * (tile + gap), 430
        c.setFillColor(hx("#FFFFFF"))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(6)
        c.roundRect(x, y, tile, 270, 28, stroke=1, fill=1)
        it = by_letter[ch.upper()]
        if ch.islower():
            u = 56
            lw = strokes.small_width(ch, u)
            strokes.draw_small(c, ch, x + 22 + (104 - lw) / 2, y + 108, u, "solid", cols[i], numbers=False)
        else:
            lh = 128
            lw = strokes.letter_width(ch, lh)
            strokes.draw_letter(c, ch, x + 22 + (104 - lw) / 2, y + 76, lh, "solid", cols[i], numbers=False)
        icons.draw_object(c, it.slug, x + 142, y + 76, 114)
        text(c, f"{ch} for {it.word_en}", x + tile / 2, y + 26, cfg.F_BOLD, 22, cfg.NAVY, "center", max_width=tile - 20)
    n = len(pages)
    pick = sorted({round(i * (n - 1) / 4) for i in range(5)})
    tw, tgap = 172, 14
    xs = (S - (len(pick) * tw + (len(pick) - 1) * tgap)) / 2
    for i, idx in enumerate(pick):
        p = pages[idx]
        th = tw * p.height / p.width
        x = xs + i * (tw + tgap)
        c.setFillColor(hx("#D5E0F0"))
        c.roundRect(x + 5, 148 - 5, tw, th, 6, stroke=0, fill=1)
        c.drawImage(ImageReader(p), x, 148, tw, th)
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.rect(x, 148, tw, th, stroke=1, fill=0)
    c.setFillColor(hx(cfg.NAVY))
    c.roundRect(150, 70, 700, 52, 26, stroke=0, fill=1)
    text(c, f"{n} Worksheets  \u2022  Ages 3\u20135  \u2022  Printable A4 PDF", 500, 87, cfg.F_BOLD, 24, "#FFFFFF", "center", max_width=660)
    text(c, cfg.BRAND["name"] + " \u2022 " + cfg.BRAND["tagline"], 500, 36, cfg.F_MED, 18, cfg.GREY, "center")
    c.save()
    pdf = pdfium.PdfDocument(str(tmp))
    pdf[0].render(scale=2).to_pil().convert("RGB").save(out)
    pdf.close()
    tmp.unlink()


def generate_letters(items, out_root: Path, set_key: str = "full") -> Path:
    meta = cfg.LETTER_SETS[set_key]
    order = meta["order"]
    folder = out_root / meta["category"] / meta["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    pdf_path = folder / PDF_NAME
    build_letters_pdf(items, pdf_path, order, f"{meta['title_id']} / {meta['title_en']}")
    pages = rasterise(pdf_path)
    names = {t: cfg.LETTER_TEMPLATES[t]["name"] for t in order}
    save_page_pngs(pages, folder, order, names)
    make_preview(pages, order, folder / "Preview.png", names, per_row=5)
    make_letters_cover(items, pages, folder / "Cover.png", meta)
    make_thumbnail(folder / "Cover.png", folder / "Thumbnail.png")
    return folder


# ====================================================================== PHONICS SERIES (templates A-J)
def build_phonics_pdf(words, out_pdf: Path) -> None:
    from .phonics import PHONICS_FUNCS, PhonicsCtx
    meta = cfg.PHONICS_SET
    order = meta["order"]
    c = canvas.Canvas(str(out_pdf), pagesize=(cfg.PAGE_W, cfg.PAGE_H))
    c.setTitle(f"{meta['title_id']} / {meta['title_en']} - Bilingual Worksheets")
    c.setAuthor(cfg.BRAND["name"])
    c.setSubject("Indonesian early reading worksheets (sounds, syllables, words), ages 3-5")
    for n, t in enumerate(order, 1):
        c.setLineJoin(1)
        c.setLineCap(1)
        PHONICS_FUNCS[t](c, PhonicsCtx(t, n, len(order), words))
        c.showPage()
    c.save()


def make_phonics_cover(words, pages: list[Image.Image], out: Path) -> None:
    from .phonics import draw_word, word_width
    meta = cfg.PHONICS_SET
    S = 1000
    tmp = out.with_suffix(".pdf")
    c = canvas.Canvas(str(tmp), pagesize=(S, S))
    c.setFillColor(hx(cfg.LIGHT))
    c.rect(0, 0, S, S, stroke=0, fill=1)
    for (x, y, r, col) in [(70, 880, 130, "#FFE9B8"), (950, 700, 150, "#D8EEFF"), (50, 400, 90, "#FFD9E6"), (960, 360, 80, "#DDF5E7")]:
        c.setFillColor(hx(col))
        c.circle(x, y, r, stroke=0, fill=1)
    c.setFillColor(hx(cfg.TEMPLATE_COLORS["A"]))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(5)
    c.roundRect(110, 910, 780, 56, 28, stroke=1, fill=1)
    text(c, meta["banner"], 500, 929, cfg.F_BOLD, 20, "#FFFFFF", "center", max_width=740)
    text(c, meta["title_id"], 500, 826, cfg.F_BOLD, 80, cfg.NAVY, "center", max_width=920)
    text(c, meta["title_en"], 500, 756, cfg.F_BOLD, 52, cfg.TEMPLATE_COLORS["D"], "center", max_width=920)
    tile, gap = 270, 40
    x0 = (S - (3 * tile + 2 * gap)) / 2
    cols = [cfg.TEMPLATE_COLORS["A"], cfg.TEMPLATE_COLORS["D"], cfg.TEMPLATE_COLORS["C"]]
    for i, (label, key) in enumerate([("a", "apel"), ("ba", "babi"), ("topi", "topi")]):
        x, y = x0 + i * (tile + gap), 430
        c.setFillColor(hx("#FFFFFF"))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(6)
        c.roundRect(x, y, tile, 270, 28, stroke=1, fill=1)
        wd = words[key]
        u = 44 if len(label) < 3 else 32
        ww = word_width(label, u)
        draw_word(c, label, x + 20 + (110 - ww) / 2 if ww < 110 else x + 14, y + 96, u, "solid", cols[i], numbers=False)
        icons.draw_object(c, wd.slug, x + 140, y + 84, 112)
        text(c, f"{wd.main} = {wd.sub.lower()}", x + tile / 2, y + 28, cfg.F_BOLD, 21, cfg.NAVY, "center", max_width=tile - 20)
    n = len(pages)
    pick = sorted({round(i * (n - 1) / 4) for i in range(5)})
    tw, tgap = 172, 14
    xs = (S - (len(pick) * tw + (len(pick) - 1) * tgap)) / 2
    for i, idx in enumerate(pick):
        p = pages[idx]
        th = tw * p.height / p.width
        x = xs + i * (tw + tgap)
        c.setFillColor(hx("#D5E0F0"))
        c.roundRect(x + 5, 148 - 5, tw, th, 6, stroke=0, fill=1)
        c.drawImage(ImageReader(p), x, 148, tw, th)
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.rect(x, 148, tw, th, stroke=1, fill=0)
    c.setFillColor(hx(cfg.NAVY))
    c.roundRect(150, 70, 700, 52, 26, stroke=0, fill=1)
    text(c, f"{n} Lembar Kerja  \u2022  Usia 3\u20135  \u2022  PDF A4 Siap Cetak", 500, 87, cfg.F_BOLD, 24, "#FFFFFF", "center", max_width=660)
    text(c, cfg.BRAND["name"] + " \u2022 " + cfg.BRAND["tagline"], 500, 36, cfg.F_MED, 18, cfg.GREY, "center")
    c.save()
    pdf = pdfium.PdfDocument(str(tmp))
    pdf[0].render(scale=2).to_pil().convert("RGB").save(out)
    pdf.close()
    tmp.unlink()


def generate_phonics(words, out_root: Path) -> Path:
    meta = cfg.PHONICS_SET
    order = meta["order"]
    folder = out_root / meta["category"] / meta["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    pdf_path = folder / PDF_NAME
    build_phonics_pdf(words, pdf_path)
    pages = rasterise(pdf_path)
    names = {t: cfg.PHONICS_TEMPLATES[t]["name"] for t in order}
    save_page_pngs(pages, folder, order, names)
    make_preview(pages, order, folder / "Preview.png", names, per_row=5)
    make_phonics_cover(words, pages, folder / "Cover.png")
    make_thumbnail(folder / "Cover.png", folder / "Thumbnail.png")
    return folder


# ====================================================================== PRE-WRITING SERIES (templates A-J)
def build_prewrite_pdf(words, out_pdf: Path) -> None:
    from .prewriting import PREWRITE_FUNCS, PrewriteCtx
    meta = cfg.PREWRITE_SET
    order = meta["order"]
    c = canvas.Canvas(str(out_pdf), pagesize=(cfg.PAGE_W, cfg.PAGE_H))
    c.setTitle(f"{meta['title_id']} / {meta['title_en']} - Bilingual Worksheets")
    c.setAuthor(cfg.BRAND["name"])
    c.setSubject("Pre-writing and fine motor worksheets, ages 3-5")
    for n, t in enumerate(order, 1):
        c.setLineJoin(1)
        c.setLineCap(1)
        PREWRITE_FUNCS[t](c, PrewriteCtx(t, n, len(order), words))
        c.showPage()
    c.save()


def make_prewrite_cover(words, pages: list[Image.Image], out: Path) -> None:
    from . import prewriting as pw
    meta = cfg.PREWRITE_SET
    S = 1000
    tmp = out.with_suffix(".pdf")
    c = canvas.Canvas(str(tmp), pagesize=(S, S))
    c.setFillColor(hx(cfg.LIGHT))
    c.rect(0, 0, S, S, stroke=0, fill=1)
    for (x, y, r, col) in [(70, 880, 130, "#FFE9B8"), (950, 700, 150, "#D8EEFF"), (50, 400, 90, "#FFD9E6"), (960, 360, 80, "#DDF5E7")]:
        c.setFillColor(hx(col))
        c.circle(x, y, r, stroke=0, fill=1)
    c.setFillColor(hx(cfg.TEMPLATE_COLORS["A"]))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(5)
    c.roundRect(110, 910, 780, 56, 28, stroke=1, fill=1)
    text(c, meta["banner"], 500, 929, cfg.F_BOLD, 20, "#FFFFFF", "center", max_width=740)
    text(c, meta["title_id"], 500, 826, cfg.F_BOLD, 76, cfg.NAVY, "center", max_width=920)
    text(c, meta["title_en"], 500, 756, cfg.F_BOLD, 48, cfg.TEMPLATE_COLORS["D"], "center", max_width=920)
    tile, gap = 270, 40
    x0 = (S - (3 * tile + 2 * gap)) / 2
    for i in range(3):
        x, y = x0 + i * (tile + gap), 430
        c.setFillColor(hx("#FFFFFF"))
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(6)
        c.roundRect(x, y, tile, 270, 28, stroke=1, fill=1)
        cx, cy = x + tile / 2, y + 140
        if i == 0:      # bee -> honey along a wave
            icons.draw_object(c, words["lebah"].slug, x + 14, cy - 30, 60)
            icons.draw_object(c, words["madu"].slug, x + tile - 74, cy - 30, 60)
            pts = pw.sine(x + 86, x + tile - 88, cy, 22, 2.5)
        elif i == 1:    # spiral
            pts = pw.spiral(cx, cy, 82, 3)
        else:           # zigzag mountains
            pts = pw.zig(x + 24, x + tile - 40, cy - 34, cy + 34, 5)
        pw.guide(c, pts, 16)
        pw.stroke(c, pts, pw.DASH, 2.4, (5, 5))
        pw.start_marker(c, pts[0])
    labels = ["Gelombang", "Spiral", "Zigzag"]
    for i, lab in enumerate(labels):
        text(c, lab, x0 + i * (tile + gap) + tile / 2, 450, cfg.F_BOLD, 24, cfg.NAVY, "center")
    n = len(pages)
    pick = sorted({round(i * (n - 1) / 4) for i in range(5)})
    tw, tgap = 172, 14
    xs = (S - (len(pick) * tw + (len(pick) - 1) * tgap)) / 2
    for i, idx in enumerate(pick):
        p = pages[idx]
        th = tw * p.height / p.width
        x = xs + i * (tw + tgap)
        c.setFillColor(hx("#D5E0F0"))
        c.roundRect(x + 5, 148 - 5, tw, th, 6, stroke=0, fill=1)
        c.drawImage(ImageReader(p), x, 148, tw, th)
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.rect(x, 148, tw, th, stroke=1, fill=0)
    c.setFillColor(hx(cfg.NAVY))
    c.roundRect(150, 70, 700, 52, 26, stroke=0, fill=1)
    text(c, f"{n} Lembar Kerja  \u2022  Usia 3\u20135  \u2022  PDF A4 Siap Cetak", 500, 87, cfg.F_BOLD, 24, "#FFFFFF", "center", max_width=660)
    text(c, cfg.BRAND["name"] + " \u2022 " + cfg.BRAND["tagline"], 500, 36, cfg.F_MED, 18, cfg.GREY, "center")
    c.save()
    pdf = pdfium.PdfDocument(str(tmp))
    pdf[0].render(scale=2).to_pil().convert("RGB").save(out)
    pdf.close()
    tmp.unlink()


def generate_prewrite(words, out_root: Path) -> Path:
    meta = cfg.PREWRITE_SET
    order = meta["order"]
    folder = out_root / meta["category"] / meta["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    pdf_path = folder / PDF_NAME
    build_prewrite_pdf(words, pdf_path)
    pages = rasterise(pdf_path)
    names = {t: cfg.PREWRITE_TEMPLATES[t]["name"] for t in order}
    save_page_pngs(pages, folder, order, names)
    make_preview(pages, order, folder / "Preview.png", names, per_row=5)
    make_prewrite_cover(words, pages, folder / "Cover.png")
    make_thumbnail(folder / "Cover.png", folder / "Thumbnail.png")
    return folder


# ====================================================================== TRACING WORDS SERIES (templates A-T)
def build_tracing_pdf(themes, order, out_pdf: Path) -> None:
    from .tracing import TracingCtx, page_tracing
    meta = cfg.TRACING_SET
    c = canvas.Canvas(str(out_pdf), pagesize=(cfg.PAGE_W, cfg.PAGE_H))
    c.setTitle(f"{meta['title_id']} / {meta['title_en']} - Bilingual Worksheets")
    c.setAuthor(cfg.BRAND["name"])
    c.setSubject("Themed tracing-words worksheets, ages 3-5")
    for n, t in enumerate(order, 1):
        c.setLineJoin(1)
        c.setLineCap(1)
        page_tracing(c, TracingCtx(t, n, len(order), themes[t]))
        c.showPage()
    c.save()


def make_tracing_cover(themes, order, pages: list[Image.Image], out: Path) -> None:
    """Text-only cover (no artwork is drawn by code)."""
    meta = cfg.TRACING_SET
    S = 1000
    tmp = out.with_suffix(".pdf")
    c = canvas.Canvas(str(tmp), pagesize=(S, S))
    c.setFillColor(hx(cfg.LIGHT))
    c.rect(0, 0, S, S, stroke=0, fill=1)
    c.setFillColor(hx(cfg.TEMPLATE_COLORS["A"]))
    c.setStrokeColor(hx(cfg.NAVY))
    c.setLineWidth(5)
    c.roundRect(110, 910, 780, 56, 28, stroke=1, fill=1)
    text(c, meta["banner"], 500, 929, cfg.F_BOLD, 20, "#FFFFFF", "center", max_width=740)
    text(c, meta["title_id"], 500, 826, cfg.F_BOLD, 84, cfg.NAVY, "center", max_width=920)
    text(c, meta["title_en"], 500, 756, cfg.F_BOLD, 54, cfg.TEMPLATE_COLORS["D"], "center", max_width=920)
    cols, gap = 5, 10
    tw_ = (S - 100 - gap * (cols - 1)) / cols
    th_ = 62
    for i, t in enumerate(order):
        r, k = divmod(i, cols)
        x, y = 50 + k * (tw_ + gap), 700 - th_ - r * (th_ + gap)
        th = themes[t]
        c.setFillColor(hx(cfg.TEMPLATE_COLORS[t]))
        c.roundRect(x, y, tw_, th_, 12, stroke=0, fill=1)
        text(c, th.no, x + 12, y + th_ - 22, cfg.F_BOLD, 15, "#FFFFFF")
        text(c, th.theme_id, x + 40, y + th_ - 22, cfg.F_BOLD, 13, "#FFFFFF", max_width=tw_ - 48)
        text(c, th.theme_en, x + 12, y + 12, cfg.F_IT, 10, "#FFFFFF", max_width=tw_ - 22)
    n = len(pages)
    pick = sorted({round(i * (n - 1) / 4) for i in range(5)})
    tw, tgap = 172, 14
    xs = (S - (len(pick) * tw + (len(pick) - 1) * tgap)) / 2
    for i, idx in enumerate(pick):
        p = pages[idx]
        thh = tw * p.height / p.width
        x = xs + i * (tw + tgap)
        c.setFillColor(hx("#D5E0F0"))
        c.roundRect(x + 5, 148 - 5, tw, thh, 6, stroke=0, fill=1)
        c.drawImage(ImageReader(p), x, 148, tw, thh)
        c.setStrokeColor(hx(cfg.NAVY))
        c.setLineWidth(2)
        c.rect(x, 148, tw, thh, stroke=1, fill=0)
    c.setFillColor(hx(cfg.NAVY))
    c.roundRect(150, 70, 700, 52, 26, stroke=0, fill=1)
    text(c, f"{n} Lembar Kerja  \u2022  {n * 4} Kata  \u2022  PDF A4 Siap Cetak", 500, 87, cfg.F_BOLD, 24, "#FFFFFF", "center", max_width=660)
    text(c, cfg.BRAND["name"] + " \u2022 " + cfg.BRAND["tagline"], 500, 36, cfg.F_MED, 18, cfg.GREY, "center")
    c.save()
    pdf = pdfium.PdfDocument(str(tmp))
    pdf[0].render(scale=2).to_pil().convert("RGB").save(out)
    pdf.close()
    tmp.unlink()


def generate_tracing(themes, out_root: Path, order=None) -> Path:
    meta = cfg.TRACING_SET
    order = [t for t in (order or meta["all_order"]) if t in themes]
    full = order == meta["all_order"]
    folder = out_root / meta["category"] / (f"Menebalkan Kata {order[0]}-{order[-1]}" if len(order) > 1 else f"Menebalkan Kata {order[0]}")
    folder.mkdir(parents=True, exist_ok=True)
    pdf_path = folder / PDF_NAME
    build_tracing_pdf(themes, order, pdf_path)
    pages = rasterise(pdf_path)
    names = {t: f"{themes[t].no} {themes[t].theme_en}" for t in order}
    save_page_pngs(pages, folder, order, names)
    make_preview(pages, order, folder / "Preview.png", names, per_row=5)
    make_tracing_cover(themes, order, pages, folder / "Cover.png")
    make_thumbnail(folder / "Cover.png", folder / "Thumbnail.png")
    return folder
