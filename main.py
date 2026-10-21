#!/usr/bin/env python3
"""Excel -> bilingual preschool worksheets.

    python main.py                              # whole database
    python main.py --only 001 003               # selected IDs
    python main.py --qa-only                    # just run quality checks
    python main.py --strict                     # warnings also block a row
    python main.py --db my.xlsx --out ./PRODUCTS
"""
import argparse
import csv
import sys
import traceback
from pathlib import Path

from wsengine import config as cfg
from wsengine import icons
from wsengine.database import load_database, load_glossary, load_letters, load_tracing, load_words
from wsengine.qa import run_letter_qa, run_prewrite_qa, run_qa, run_tracing_qa, run_words_qa, write_image_list, write_report
from wsengine.renderer import generate_letters, generate_phonics, generate_prewrite, generate_row, generate_tracing


def run_tracing(a, out_root: Path, glossary: dict) -> int:
    themes = load_tracing(a.db)
    print(f"Loaded {len(themes)} themes / {sum(len(t.words) for t in themes.values())} words from {a.db}")
    issues = run_tracing_qa(themes, glossary)
    write_report(issues, out_root / "qa_report_tracing.csv")
    write_image_list(themes, out_root / "image_list.csv")
    errors = [i for i in issues if i.level == "ERROR" or (a.strict and i.level == "WARNING")]
    for i in issues:
        if i.level == "ERROR" or i.check != "image":
            print(f"  [{i.level:7}] {i.row_id} {i.check}: {i.message}")
    n_img = sum(i.check == "image" for i in issues)
    print(f"QA: {sum(i.level == 'ERROR' for i in issues)} errors, {sum(i.level == 'WARNING' for i in issues)} warnings "
          f"({n_img} pictures still missing - see PRODUCTS/image_list.csv)")
    if errors or a.qa_only:
        return 1 if errors else 0
    order = list(a.pages.upper()) if a.pages else None
    folder = generate_tracing(themes, out_root, order)
    print(f"Done: Menebalkan Kata -> {folder.relative_to(out_root)}")
    return 0


def run_prewrite(a, out_root: Path, glossary: dict) -> int:
    words = load_words(a.db)
    print(f"Loaded {len(words)} words from {a.db}")
    issues = run_prewrite_qa(words, glossary)
    write_report(issues, out_root / "qa_report_prewriting.csv")
    for i in issues:
        print(f"  [{i.level:7}] {i.row_id} {i.check}: {i.message}")
    errors = [i for i in issues if i.level == "ERROR" or (a.strict and i.level == "WARNING")]
    print(f"QA: {sum(i.level == 'ERROR' for i in issues)} errors, {sum(i.level == 'WARNING' for i in issues)} warnings")
    if errors or a.qa_only:
        return 1 if errors else 0
    folder = generate_prewrite(words, out_root)
    print(f"Done: {cfg.PREWRITE_SET['title_id']} (10 pages) -> {folder.relative_to(out_root)}")
    return 0


def run_phonics(a, out_root: Path, glossary: dict) -> int:
    words = load_words(a.db)
    print(f"Loaded {len(words)} words from {a.db}")
    issues = run_words_qa(words, glossary)
    write_report(issues, out_root / "qa_report_phonics.csv")
    for i in issues:
        print(f"  [{i.level:7}] {i.row_id} {i.check}: {i.message}")
    errors = [i for i in issues if i.level == "ERROR" or (a.strict and i.level == "WARNING")]
    print(f"QA: {sum(i.level == 'ERROR' for i in issues)} errors, {sum(i.level == 'WARNING' for i in issues)} warnings")
    if errors or a.qa_only:
        return 1 if errors else 0
    folder = generate_phonics(words, out_root)
    print(f"Done: {cfg.PHONICS_SET['title_id']} (10 pages) -> {folder.relative_to(out_root)}")
    return 0


def run_letters(a, out_root: Path, glossary: dict) -> int:
    items = load_letters(a.db)
    print(f"Loaded {len(items)} letter rows from {a.db}")
    issues = run_letter_qa(items, glossary)
    write_report(issues, out_root / "qa_report_letters.csv")
    for i in issues:
        print(f"  [{i.level:7}] #{i.row_id} {i.check}: {i.message}")
    errors = [i for i in issues if i.level == "ERROR" or (a.strict and i.level == "WARNING")]
    print(f"QA: {sum(i.level == 'ERROR' for i in issues)} errors, {sum(i.level == 'WARNING' for i in issues)} warnings")
    if errors or a.qa_only:
        return 1 if errors else 0
    folder = generate_letters(items, out_root, a.set)
    print(f"Done: {cfg.LETTER_SETS[a.set]['title_en']} ({len(cfg.LETTER_SETS[a.set]['order'])} pages) -> {folder.relative_to(out_root)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["tracing", "prewriting", "phonics", "letters", "objects"], default="tracing",
                    help="tracing = Tracing Words A-T, pictures from assets/images (default) | prewriting | phonics | letters | objects "
                         "(the last four still draw their pictures in code)")
    ap.add_argument("--pages", default="", help="tracing mode: only these template letters, e.g. ABCDEFGHIJ")
    ap.add_argument("--set", choices=list(cfg.LETTER_SETS), default="full",
                    help="letters mode: full = A-T (20 pages) | capital = A-J | small = K-T")
    ap.add_argument("--db", default=str(cfg.DATA_DIR / "worksheet_database.xlsx"))
    ap.add_argument("--glossary", default=str(cfg.DATA_DIR / "vocabulary_glossary.csv"))
    ap.add_argument("--out", default=str(cfg.OUTPUT_DIR))
    ap.add_argument("--only", nargs="*", help="only these IDs")
    ap.add_argument("--templates", default="".join(cfg.TEMPLATE_ORDER), help="e.g. ABE")
    ap.add_argument("--strict", action="store_true", help="treat QA warnings as errors")
    ap.add_argument("--qa-only", action="store_true")
    a = ap.parse_args()

    out_root = Path(a.out)
    out_root.mkdir(parents=True, exist_ok=True)
    glossary = load_glossary(a.glossary)
    if a.mode == "tracing":
        return run_tracing(a, out_root, glossary)
    if a.mode == "prewriting":
        return run_prewrite(a, out_root, glossary)
    if a.mode == "phonics":
        return run_phonics(a, out_root, glossary)
    if a.mode == "letters":
        return run_letters(a, out_root, glossary)
    rows = load_database(a.db)
    print(f"Loaded {len(rows)} rows from {a.db}")

    # ---- 1. quality gate (runs on the FULL database so distractor pools stay intact)
    issues = run_qa(rows, glossary)
    write_report(issues, out_root / "qa_report.csv")
    blocked = {i.row_id for i in issues if i.level == "ERROR" or (a.strict and i.level == "WARNING")}
    for i in issues:
        print(f"  [{i.level:7}] #{i.row_id} {i.check}: {i.message}")
    print(f"QA: {sum(i.level == 'ERROR' for i in issues)} errors, {sum(i.level == 'WARNING' for i in issues)} warnings, "
          f"{len(blocked)} rows blocked")

    # ---- 2. image to-do list (rows that still need artwork)
    with open(out_root / "image_todo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Save_As", "Image_Prompt"])
        for r in rows:
            for slug, label in ((r.object_slug, r.object_en), (r.relation_slug, r.relation_en)):
                if icons.art_source(slug) == "placeholder":
                    w.writerow([r.id, f"assets/images/{slug}.png", f"{label}: {r.image_prompt}"])
    if a.qa_only:
        return 1 if blocked else 0

    # ---- 3. generate
    manifest, failed = [], 0
    for r in rows:
        if a.only and r.id not in a.only:
            continue
        if r.id in blocked:
            print(f"SKIP  #{r.id} {r.object_en} (QA)")
            continue
        try:
            folder = generate_row(r, rows, glossary, out_root, list(a.templates.upper()))
            manifest.append([r.id, r.category, r.object_en, r.relation_en, str(folder.relative_to(out_root))])
            print(f"OK    #{r.id} {r.object_en} & {r.relation_en} -> {folder.relative_to(out_root)}")
        except Exception:
            failed += 1
            print(f"FAIL  #{r.id} {r.object_en}")
            traceback.print_exc()
    with open(out_root / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Category", "Object_EN", "Relation_EN", "Folder"])
        w.writerows(manifest)
    print(f"Done: {len(manifest)} generated, {failed} failed -> {out_root}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
