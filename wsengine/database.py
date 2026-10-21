"""Excel -> Row objects, glossary loading and the {PLACEHOLDER} engine."""
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import config as cfg
from .linguistics import article_phrase, capitalise

REQUIRED_COLUMNS = ["ID", "Category", "Object_EN", "Object_ID", "Relation_EN", "Relation_ID", "Image_Prompt"]


def slugify(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")


def safe_name(text: str) -> str:
    """Folder-safe version of a category / object name ('&' -> 'and')."""
    t = text.replace("&", "and")
    t = re.sub(r'[<>:"/\\|?*]+', "", t)
    return re.sub(r"\s+", " ", t).strip()


@dataclass(frozen=True)
class Row:
    id: str
    category: str
    object_en: str
    object_id: str
    relation_en: str
    relation_id: str
    image_prompt: str

    @property
    def object_slug(self) -> str:
        return slugify(self.object_en)

    @property
    def relation_slug(self) -> str:
        return slugify(self.relation_en)

    @property
    def wording(self) -> dict:
        return cfg.CATEGORY_WORDING.get(self.category, cfg.DEFAULT_WORDING)

    @property
    def folder(self) -> Path:
        return Path(safe_name(self.category)) / safe_name(self.object_en)


@dataclass(frozen=True)
class Item:
    """One drawable thing: used for the row's own pair and for distractors."""
    slug: str
    en: str
    id: str


# ------------------------------------------------------------------ loading
def load_database(path: str | Path) -> list[Row]:
    df = pd.read_excel(path, sheet_name="Worksheets", dtype=str, keep_default_na=False)
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    lookup = {c.lower(): c for c in df.columns}
    missing = [c for c in REQUIRED_COLUMNS if c.lower() not in lookup]
    if missing:
        raise ValueError(f"Database is missing columns: {missing}")
    rows = []
    for _, r in df.iterrows():
        vals = {c: str(r[lookup[c.lower()]]).strip() for c in REQUIRED_COLUMNS}
        if not any(vals.values()):
            continue  # fully blank line
        if vals["ID"].isdigit():
            vals["ID"] = vals["ID"].zfill(3)
        rows.append(Row(*[vals[c] for c in REQUIRED_COLUMNS]))
    return rows


def load_glossary(path: str | Path | None = None) -> dict[str, dict]:
    """EN word (lowercase) -> {id: set of accepted Indonesian words, countable: bool, syllables: str}."""
    path = Path(path or cfg.DATA_DIR / "vocabulary_glossary.csv")
    gl: dict[str, dict] = {}
    if not path.exists():
        return gl
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            en = r["EN"].strip().lower()
            gl[en] = dict(
                id={x.strip().lower() for x in r["ID"].split("|") if x.strip()},
                countable=r.get("Countable", "Y").strip().upper() != "N",
                syllables=(r.get("Syllables_ID") or "").strip() or None,
            )
    return gl


# ------------------------------------------------------------------ placeholders
_TOKEN = re.compile(r"\{(A_)?(OBJECT|RELATION)_(EN|ID)\}|\{(OBJ|REL)_NOUN_(EN|ID)\}", re.I)


def fill_placeholders(text: str, row: Row, glossary: dict | None = None) -> str:
    """Replace {OBJECT_EN} {OBJECT_ID} {RELATION_EN} {RELATION_ID} (and helpers).

    UPPERCASE token -> Capitalised value, lowercase token -> lowercase value,
    {a_object_en} -> 'a chicken' / 'an egg' / 'milk'.
    """
    glossary = glossary or {}
    values = {
        ("OBJECT", "EN"): row.object_en, ("OBJECT", "ID"): row.object_id,
        ("RELATION", "EN"): row.relation_en, ("RELATION", "ID"): row.relation_id,
    }

    def repl(m: re.Match) -> str:
        raw = m.group(0)
        if m.group(4):  # {OBJ_NOUN_EN} style: category wording
            key = f"{m.group(4).lower()}_noun_{m.group(5).lower()}"
            val = row.wording[key]
        else:
            kind, lang = m.group(2).upper(), m.group(3).upper()
            val = values[(kind, lang)]
            if m.group(1) and lang == "EN":
                g = glossary.get(val.lower(), {})
                return article_phrase(val, g.get("countable", True))
        return capitalise(val) if raw.strip("{}")[:1].isupper() else val.lower()

    return _TOKEN.sub(repl, text)


# ------------------------------------------------------------------ alphabet (Capital Letters series)
@dataclass(frozen=True)
class LetterItem:
    id: str
    letter: str
    word_en: str
    word_id: str
    image_prompt: str

    @property
    def slug(self) -> str:
        return slugify(self.word_en)


def load_letters(path: str | Path) -> list[LetterItem]:
    """Reads sheet 'Letters': ID | Letter | Word_EN | Word_ID | Image_Prompt (one row per letter)."""
    df = pd.read_excel(path, sheet_name="Letters", dtype=str, keep_default_na=False)
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    need = ["ID", "Letter", "Word_EN", "Word_ID", "Image_Prompt"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"Sheet 'Letters' is missing columns: {missing}")
    items = []
    for _, r in df.iterrows():
        v = {c: str(r[c]).strip() for c in need}
        if not any(v.values()):
            continue
        items.append(LetterItem(v["ID"].zfill(3) if v["ID"].isdigit() else v["ID"], v["Letter"].upper(),
                                v["Word_EN"], v["Word_ID"], v["Image_Prompt"]))
    return items


# ------------------------------------------------------------------ phonics series (Indonesian-first)
@dataclass(frozen=True)
class Word:
    id: str
    word_id: str
    word_en: str
    initial: str          # explicit sound letter ('' = first letter of word_id)
    syllables: str        # optional override, e.g. 'a-pel'
    image_prompt: str

    @property
    def slug(self) -> str:
        return slugify(self.word_en)

    @property
    def initial_letter(self) -> str:
        return (self.initial or self.word_id[:1]).lower()

    @property
    def uses_english_sound(self) -> bool:
        """True when the sound letter is not the first letter of the Indonesian word (e.g. Q = Queen)."""
        return self.initial_letter != self.word_id[:1].lower()

    @property
    def main(self) -> str:
        """The word shown first: the one that really starts with the sound letter."""
        return (self.word_en if self.uses_english_sound else self.word_id).lower()

    @property
    def sub(self) -> str:
        return capitalise(self.word_id if self.uses_english_sound else self.word_en)


def load_words(path: str | Path) -> dict[str, Word]:
    """Sheet 'Words' -> {word_id.lower(): Word}."""
    from .linguistics import capitalise as _c  # noqa: F401
    df = pd.read_excel(path, sheet_name="Words", dtype=str, keep_default_na=False)
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    need = ["ID", "Word_ID", "Word_EN", "Initial", "Syllables_ID", "Image_Prompt"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"Sheet 'Words' is missing columns: {missing}")
    out: dict[str, Word] = {}
    for _, r in df.iterrows():
        v = {c: str(r[c]).strip() for c in need}
        if not v["Word_ID"]:
            continue
        out[v["Word_ID"].lower()] = Word(v["ID"], v["Word_ID"], v["Word_EN"], v["Initial"].lower(), v["Syllables_ID"], v["Image_Prompt"])
    return out


# ------------------------------------------------------------------ tracing-words series (templates A-T)
@dataclass(frozen=True)
class TraceWord:
    template: str
    word_id: str
    word_en: str
    syllables: str     # optional override, e.g. 'ti-reks'
    image_file: str    # optional override file name inside assets/images/
    image_prompt: str

    @property
    def slug_en(self) -> str:
        return slugify(self.word_en)

    @property
    def slug_id(self) -> str:
        return slugify(self.word_id)

    @property
    def expected_file(self) -> str:
        return self.image_file or f"{self.slug_en}.png"

    @property
    def letters_en(self) -> str:
        return " - ".join(ch for ch in self.word_en.lower() if ch.isalpha())


@dataclass(frozen=True)
class TraceTheme:
    template: str
    no: str
    theme_id: str
    theme_en: str
    tip_id: str
    tip_en: str
    words: tuple

    @property
    def spec(self) -> dict:
        """Header/footer text for this page (same keys as the other series)."""
        return dict(
            name=f"{self.no} {self.theme_en}", primary="id", series="Menebalkan Kata / Tracing Words",
            title_id=f"{self.no} {self.theme_id}", title_en=f"{self.theme_en} \u2022 Tracing Words",
            goal_id=f"Mengenal, menepuk suku kata, dan menebalkan kata bertema {self.theme_id.lower()}.",
            goal_en=f"Learn, clap the syllables and trace words about {self.theme_en.lower()}.",
            tip_id=self.tip_id, tip_en=self.tip_en,
        )


def load_tracing(path: str | Path) -> dict[str, TraceTheme]:
    """Sheets 'Themes' + 'TraceWords' -> {template letter: TraceTheme}, in sheet order."""
    th = pd.read_excel(path, sheet_name="Themes", dtype=str, keep_default_na=False)
    tw = pd.read_excel(path, sheet_name="TraceWords", dtype=str, keep_default_na=False)
    for df, need in ((th, ["Template", "No", "Theme_ID", "Theme_EN", "Tip_ID", "Tip_EN"]),
                     (tw, ["Template", "Word_ID", "Word_EN", "Syllables_ID", "Image_File", "Image_Prompt"])):
        df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
        missing = [c for c in need if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns {missing}")
    words: dict[str, list] = {}
    for _, r in tw.iterrows():
        t = str(r["Template"]).strip().upper()
        if t and str(r["Word_ID"]).strip():
            words.setdefault(t, []).append(TraceWord(t, r["Word_ID"].strip(), r["Word_EN"].strip(), r["Syllables_ID"].strip(),
                                                    r["Image_File"].strip(), r["Image_Prompt"].strip()))
    out: dict[str, TraceTheme] = {}
    for _, r in th.iterrows():
        t = str(r["Template"]).strip().upper()
        if t:
            out[t] = TraceTheme(t, r["No"].strip(), r["Theme_ID"].strip(), r["Theme_EN"].strip(), r["Tip_ID"].strip(),
                                r["Tip_EN"].strip(), tuple(words.get(t, [])))
    return out
