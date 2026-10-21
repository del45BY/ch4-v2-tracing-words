"""Pre-generation quality gate.

ERROR   -> row is skipped (or everything with --strict warnings-as-errors)
WARNING -> row is generated but listed in qa_report.csv for a human look
"""
import csv
import re
from dataclasses import dataclass
from pathlib import Path

from reportlab.pdfbase.pdfmetrics import stringWidth

from . import config as cfg
from . import icons
from .database import Row
from .linguistics import syllabify_id

UNSAFE_PROMPT_WORDS = {"scary", "blood", "angry", "dead", "weapon", "gun", "knife", "evil", "monster", "realistic", "photo"}
WORD_RE = re.compile(r"^[A-Za-z]+(?:[ \-][A-Za-z]+)?$")
ID_WORD_RE = re.compile(r"^[A-Za-z]+(?:[ \-][A-Za-z]+)?$")


@dataclass
class Issue:
    row_id: str
    level: str  # ERROR | WARNING
    check: str
    message: str


def check_row(row: Row, glossary: dict, all_rows: list[Row]) -> list[Issue]:
    out: list[Issue] = []

    def add(level, check, msg):
        out.append(Issue(row.id, level, check, msg))

    # ---- completeness
    for name in ("category", "object_en", "object_id", "relation_en", "relation_id", "image_prompt"):
        if not getattr(row, name):
            add("ERROR", "complete", f"Empty field: {name}")
    if not out:
        pairs = [("object", row.object_en, row.object_id), ("relation", row.relation_en, row.relation_id)]
        for kind, en, idn in pairs:
            # ---- spelling / characters
            if not WORD_RE.match(en):
                add("ERROR", "spelling", f"{kind} EN '{en}' has odd characters or more than 2 words")
            if not ID_WORD_RE.match(idn):
                add("ERROR", "spelling", f"{kind} ID '{idn}' has odd characters or more than 2 words")
            # ---- age suitability
            letters = len(en.replace(" ", ""))
            if letters > 12:
                add("ERROR", "age", f"'{en}' has {letters} letters - too long for ages 3-5")
            elif letters > 8:
                add("WARNING", "age", f"'{en}' has {letters} letters - check it is tracing-friendly")
            # ---- vocabulary + translation
            g = glossary.get(en.lower())
            if g is None:
                add("WARNING", "vocab", f"'{en}' is not in the approved glossary - verify spelling and translation, then add it")
            elif idn.lower() not in g["id"]:
                add("ERROR", "translation", f"'{en}' -> '{idn}' but glossary says {sorted(g['id'])}")
            # ---- printable layout (big text must fit the card)
            for word, font, size, limit in ((en, cfg.F_BOLD, 34, 300), (idn, cfg.F_MED, 24, 300)):
                if stringWidth(word, font, size) > limit * 1.6:
                    add("ERROR", "layout", f"'{word}' is too wide for the vocabulary card")
            if len(syllabify_id(idn, (g or {}).get("syllables"))) > 6:
                add("WARNING", "age", f"'{idn}' has more than 6 syllables")
            # ---- images
            if icons.art_source(re.sub(r"[^a-z0-9]+", "_", en.lower()).strip("_")) == "placeholder":
                add("WARNING", "image", f"No artwork for '{en}' - generate assets/images/{en.lower()}.png from Image_Prompt")
        if row.object_en.lower() == row.relation_en.lower():
            add("ERROR", "complete", "Object and Relation are the same word")
        bad = [w for w in UNSAFE_PROMPT_WORDS if re.search(rf"\b{w}\b", row.image_prompt.lower())]
        if bad:
            add("WARNING", "image", f"Image_Prompt contains non-child-friendly words: {bad}")
    return out


def run_qa(rows: list[Row], glossary: dict) -> list[Issue]:
    issues: list[Issue] = []
    seen = set()
    for r in rows:
        if r.id in seen:
            issues.append(Issue(r.id, "ERROR", "complete", "Duplicate ID"))
        seen.add(r.id)
        issues += check_row(r, glossary, rows)
    return issues


def write_report(issues: list[Issue], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Level", "Check", "Message"])
        for i in issues:
            w.writerow([i.row_id, i.level, i.check, i.message])


def run_letter_qa(items, glossary: dict) -> list[Issue]:
    """Checks for the Capital Letters series (sheet 'Letters')."""
    out: list[Issue] = []
    seen = {}
    for it in items:
        def add(level, check, msg):
            out.append(Issue(it.id, level, check, msg))
        if len(it.letter) != 1 or not it.letter.isalpha():
            add("ERROR", "complete", f"Letter '{it.letter}' must be one A-Z character")
            continue
        if it.letter in seen:
            add("ERROR", "complete", f"Letter {it.letter} appears twice (also row {seen[it.letter]})")
        seen[it.letter] = it.id
        if not it.word_en or not it.word_id:
            add("ERROR", "complete", f"Empty word for letter {it.letter}")
            continue
        if not it.word_en.upper().startswith(it.letter):
            add("ERROR", "age", f"'{it.word_en}' does not start with {it.letter}")
        if not WORD_RE.match(it.word_en) or not ID_WORD_RE.match(it.word_id):
            add("ERROR", "spelling", f"'{it.word_en}' / '{it.word_id}' has odd characters or more than 2 words")
        if len(it.word_en.replace(" ", "")) > 10:
            add("WARNING", "age", f"'{it.word_en}' is long for a letter page")
        g = glossary.get(it.word_en.lower())
        if g is None:
            add("WARNING", "vocab", f"'{it.word_en}' is not in the approved glossary")
        elif it.word_id.lower() not in g["id"]:
            add("ERROR", "translation", f"'{it.word_en}' -> '{it.word_id}' but glossary says {sorted(g['id'])}")
        if icons.art_source(it.slug) == "placeholder":
            add("WARNING", "image", f"No artwork for '{it.word_en}' - generate assets/images/{it.slug}.png")
    missing = [ch for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if ch not in seen]
    if missing:
        out.append(Issue("-", "ERROR", "complete", f"Missing letters: {''.join(missing)}"))
    return out


def run_words_qa(words: dict, glossary: dict) -> list[Issue]:
    """Checks for the phonics series (sheet 'Words' + config.PHONICS_CONTENT)."""
    out: list[Issue] = []

    def add(rid, level, check, msg):
        out.append(Issue(rid, level, check, msg))

    # ---- every word used on a page must exist and be valid
    used: dict[str, set] = {}
    for t, content in cfg.PHONICS_CONTENT.items():
        keys = (list(content.values()) if isinstance(content, dict)
                else [w for item in content for w in (item if isinstance(item, tuple) else (item,))][:])
        if t == "J":
            keys = [k for pair in content for k in pair[:2]]
        for k in keys:
            used.setdefault(k.lower(), set()).add(t)
    for k, templates in sorted(used.items()):
        wd = words.get(k)
        rid = "/".join(sorted(templates))
        if wd is None:
            add(rid, "ERROR", "complete", f"Word '{k}' is used on template {rid} but missing from sheet 'Words'")
            continue
        if not ID_WORD_RE.match(wd.word_id) or not WORD_RE.match(wd.word_en):
            add(rid, "ERROR", "spelling", f"'{wd.word_id}' / '{wd.word_en}' has odd characters or more than 2 words")
        g = glossary.get(wd.word_en.lower())
        if g is None:
            add(rid, "WARNING", "vocab", f"'{wd.word_en}' is not in the approved glossary")
        elif wd.word_id.lower() not in g["id"]:
            add(rid, "ERROR", "translation", f"'{wd.word_en}' -> '{wd.word_id}' but glossary says {sorted(g['id'])}")
        if icons.art_source(wd.slug) == "placeholder":
            add(rid, "WARNING", "image", f"No artwork for '{wd.word_en}' - save assets/images/{wd.slug}.png")
        if len(wd.word_id.replace(" ", "")) > 10:
            add(rid, "WARNING", "age", f"'{wd.word_id}' is long for ages 3-5")
        if wd.uses_english_sound:
            add(rid, "WARNING", "sound", f"'{wd.word_id}' does not start with '{wd.initial_letter}': the page shows the English word '{wd.word_en}' for this sound")

    # ---- page rules
    A = [words[k].initial_letter for k in cfg.PHONICS_CONTENT["A"] if k in words]
    if sorted(A) != sorted("aiueo"):
        add("A", "ERROR", "sound", f"Template A needs one word per vowel a-i-u-e-o, found initials {A}")
    for t, rng_ in cfg.PHONICS_LETTER_RANGES.items():
        if t == "A":
            continue
        for k in cfg.PHONICS_CONTENT[t]:
            wd = words.get(k)
            if wd and wd.initial_letter not in rng_:
                add(t, "ERROR", "sound", f"'{k}' starts with '{wd.initial_letter}', which is outside template {t} ({rng_[0]}-{rng_[-1]})")
        got = {words[k].initial_letter for k in cfg.PHONICS_CONTENT[t] if k in words}
        miss = sorted(set(rng_) - got) if t != "E" else sorted(set("stuvwxyz") - got)
        if miss:
            add(t, "WARNING", "sound", f"Template {t} has no picture for letter(s): {''.join(miss)}")
    for t in ("F", "G"):
        for syl, k in cfg.PHONICS_CONTENT[t].items():
            wd = words.get(k)
            if wd and not wd.word_id.lower().startswith(syl):
                add(t, "ERROR", "sound", f"'{k}' does not start with the syllable '{syl}'")
    for a, b, ending in cfg.PHONICS_CONTENT["J"]:
        for k in (a, b):
            if not k.lower().endswith(ending):
                add("J", "ERROR", "rhyme", f"'{k}' does not end with '-{ending}'")
    for k in cfg.PHONICS_CONTENT["H"]:
        wd = words.get(k)
        if wd and len(syllabify_id(wd.word_id, wd.syllables or None)) != 2:
            add("H", "ERROR", "sound", f"'{k}' must have exactly 2 syllables for template H")
    for k in cfg.PHONICS_CONTENT["G"].values():
        wd = words.get(k)
        if wd and len(syllabify_id(wd.word_id, wd.syllables or None)) != 2:
            add("G", "ERROR", "sound", f"'{k}' must have exactly 2 syllables for the joining exercise")
    return out


def run_prewrite_qa(words: dict, glossary: dict) -> list[Issue]:
    """Pre-writing series: every picture used as a start/goal must exist, have artwork and a correct translation."""
    out: list[Issue] = []
    seen: set[str] = set()
    for t, pairs in cfg.PREWRITE_CONTENT.items():
        for pair in pairs:
            for k in pair:
                if k in seen:
                    continue
                seen.add(k)
                wd = words.get(k.lower())
                if wd is None:
                    out.append(Issue(t, "ERROR", "complete", f"'{k}' (template {t}) is missing from sheet 'Words'"))
                    continue
                g = glossary.get(wd.word_en.lower())
                if g is not None and wd.word_id.lower() not in g["id"]:
                    out.append(Issue(t, "ERROR", "translation", f"'{wd.word_en}' -> '{wd.word_id}' but glossary says {sorted(g['id'])}"))
                if icons.art_source(wd.slug) == "placeholder":
                    out.append(Issue(t, "WARNING", "image", f"No artwork for '{wd.word_en}' - save assets/images/{wd.slug}.png"))
    need = {"B": 4, "D": 3, "E": 1, "F": 3, "I": 4}
    for t, n in need.items():
        if len(cfg.PREWRITE_CONTENT.get(t, [])) < n:
            out.append(Issue(t, "ERROR", "complete", f"Template {t} needs at least {n} picture pairs in PREWRITE_CONTENT"))
    return out


def run_tracing_qa(themes: dict, glossary: dict) -> list[Issue]:
    """Tracing Words series: structure, spelling, translation, syllable overrides and picture files."""
    from .tracing import find_image
    out: list[Issue] = []

    def add(rid, level, check, msg):
        out.append(Issue(rid, level, check, msg))

    missing_pages = [t for t in cfg.TRACING_SET["all_order"] if t not in themes]
    if missing_pages:
        add("-", "WARNING", "complete", f"Sheet 'Themes' has no row for template(s): {''.join(missing_pages)}")
    seen_words: set = set()
    for t, th in themes.items():
        if len(th.words) != 4:
            add(t, "ERROR", "complete", f"Template {t} ({th.theme_id}) has {len(th.words)} words in 'TraceWords'; it needs exactly 4")
        if not th.theme_id or not th.theme_en:
            add(t, "ERROR", "complete", f"Template {t} has an empty Theme_ID / Theme_EN")
        for wd in th.words:
            rid = f"{t}"
            if not WORD_RE.match(wd.word_en) or not ID_WORD_RE.match(wd.word_id):
                add(rid, "ERROR", "spelling", f"'{wd.word_id}' / '{wd.word_en}' has odd characters or more than 2 words")
                continue
            key = (wd.word_id.lower(), wd.word_en.lower())
            if key in seen_words:
                add(rid, "WARNING", "complete", f"'{wd.word_id}' / '{wd.word_en}' appears on more than one page")
            seen_words.add(key)
            g = glossary.get(wd.word_en.lower())
            if g is None:
                add(rid, "WARNING", "vocab", f"'{wd.word_en}' is not in the approved glossary")
            elif wd.word_id.lower() not in g["id"]:
                add(rid, "ERROR", "translation", f"'{wd.word_en}' -> '{wd.word_id}' but glossary says {sorted(g['id'])}")
            if wd.syllables:
                joined = re.sub(r"[^a-z]", "", wd.syllables.lower())
                plain = re.sub(r"[^a-z]", "", wd.word_id.lower())
                if joined != plain:
                    add(rid, "ERROR", "spelling", f"Syllables '{wd.syllables}' do not spell '{wd.word_id}'")
            n = len(re.sub(r"[^A-Za-z]", "", wd.word_id))
            if n > 10:
                add(rid, "WARNING", "age", f"'{wd.word_id}' has {n} letters - long for ages 3-5 (the text will shrink)")
            if find_image(wd) is None:
                add(rid, "WARNING", "image", f"No picture yet: put assets/images/{wd.expected_file}")
    return out


def write_image_list(themes: dict, path: Path) -> None:
    from .tracing import find_image
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Template", "Word_ID", "Word_EN", "Put_File_Here", "Exists", "Image_Prompt"])
        for t, th in themes.items():
            for wd in th.words:
                w.writerow([t, wd.word_id, wd.word_en, f"assets/images/{wd.expected_file}", "yes" if find_image(wd) else "NO", wd.image_prompt])
