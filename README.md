# Preschool Worksheet Engine (Excel -> bilingual printable PDFs)

## DEFAULT: Tracing Words series, templates A-T ("Menebalkan Kata / Tracing Words")

`python main.py` -> one 20-page A4 PDF (20 themes x 4 words) + Preview/Cover/Thumbnail/pages.
**No picture is drawn by code in this series.** Put one picture per word in `assets/images/` (see `assets/images/README.txt`);
only `cow.png` is shipped as a demo. Missing pictures print as an empty dashed box naming the expected file.
`PRODUCTS/image_list.csv` lists every file name (and whether it exists) each run.

Data: Excel sheets **Themes** (20 rows: Template, No, Theme_ID, Theme_EN, Tip_ID, Tip_EN) and **TraceWords** (exactly 4 rows per Template:
Word_ID, Word_EN, Syllables_ID, Image_File, Image_Prompt). Layout: `wsengine/tracing.py`. `--pages ABCDEFGHIJ` builds a subset.

Page: header (number + theme) | steps 1 Lihat & sebutkan, 2 Tepuk suku katanya, 3 Tebalkan hurufnya | 4 cards
(picture, ID word, EN word, ID syllable boxes, spelled letters, ID + EN words as ONE dashed centre-line stroke per letter to trace, config TRACING_SET['trace_band']) | parent tip | footer.

Other series still exist (`--mode prewriting | phonics | letters | objects`) but they DO draw their pictures in code.

---

## Pre-writing series (--mode prewriting)


`python main.py` builds ONE 10-page product (PDF + Preview/Cover/Thumbnail + pages/). Series label appears in every footer.
Titles/goals/tips: `config.PREWRITE_TEMPLATES` | picture pairs (start -> goal): `config.PREWRITE_CONTENT` (words from sheet Words)
| layouts + line geometry: `wsengine/prewriting.py`.

| Tmpl | Title | Exercises |
|---|---|---|
| A | Garis Tegak (Vertical Lines) | rain, fence, balloons, connect dots top->bottom |
| B | Garis Datar (Horizontal Lines) | animal -> goal rows, straight road, connect dots left->right |
| C | Garis Miring (Diagonal Lines) | slides, roofs, crosses (1 then 2), connect diagonal dots |
| D | Garis Zigzag | mountains, zigzag to goal, lightning, join dots |
| E | Garis Lengkung (Curved Lines) | rainbow, bouncing ball, smiles/hills, dotted arches |
| F | Garis Gelombang (Wavy Lines) | big/medium/small waves, wiggle to goal, flowing water, dotted wave |
| G | Lingkaran & Spiral | circles big->small, spirals, loops, dotted circles |
| H | Pola Campuran (Mixed Patterns) | 6 repeating patterns - first two periods drawn, child continues |
| I | Mengikuti Jalur (Path Tracing) | 4 bordered roads (wave, right angles, zigzag, loop-the-loop) |
| J | Menebalkan Bentuk Dasar (Shape Tracing) | 8 named shapes + a house made of shapes |

Every guide: pale thick line + dashed centre, GREEN start dot, direction arrows, RED flag at the end.
Goals, parent tips and exercise ideas were written by the generator from the page titles - please review.
Other series: `--mode phonics` (sounds/syllables/words A-J), `--mode letters --set full|capital|small`, `--mode objects`.

---

## Phonics series (--mode phonics)

`python main.py` builds ONE 10-page product "Bunyi, Suku Kata & Kata" (PDF + Preview/Cover/Thumbnail + pages/).
Words come from Excel sheet **Words**; which words each page uses is set in `config.PHONICS_CONTENT`;
titles / objectives / tips in `config.PHONICS_TEMPLATES`; layouts in `wsengine/phonics.py`.

| Tmpl | Title | Activity |
|---|---|---|
| A | Bunyi Huruf Vokal (a, i, u, e, o) | Mengucapkan bunyi vokal, menebalkan huruf, dan mencocokkan gambar dengan vokal awalnya. |
| B | Bunyi Awal Kata A-F | Menyebutkan nama gambar dan melingkari huruf bunyi awalnya. |
| C | Bunyi Awal Kata G-L | Mencocokkan gambar dengan huruf awal dan menulis huruf awal kata. |
| D | Bunyi Awal Kata M-R | Mengelompokkan gambar berdasarkan bunyi awal dan melengkapi huruf awal. |
| E | Bunyi Awal Kata S-Z | Mengelompokkan gambar, mencocokkan huruf, dan melengkapi kata. |
| F | Suku Kata Dasar (ba, bi, bu, be, bo) | Menebalkan suku kata, membunyikan, dan mencocokkan dengan gambar. |
| G | Suku Kata Lanjutan (ka, la, ma, na, sa) | Menebalkan suku kata dan menyusun suku kata menjadi kata sederhana. |
| H | Menyusun Kata Dua Suku Kata | Menyusun kata seperti bola, sapi, topi, dan bebek dari kartu suku kata. |
| I | Pasangan Gambar & Kata Bilingual | Mencocokkan gambar dengan kata Indonesia dan Inggris, lalu menebalkan kata. |
| J | Kata Berima (Rhyming Words) | Mencocokkan gambar yang bunyi akhirnya sama, misalnya topi-kopi, sapi-api. |

Notes: the "Tujuan" shown in each header is the *activity* column of the brief. Q has no common Indonesian word, so page D uses "Queen"
(sheet column `Initial` = Q). "bola-gola" was replaced by valid rhymes (topi-kopi, sapi-api, payung-burung).
QA: `python main.py --qa-only` (qa_report_phonics.csv).

Older series are still available: `--mode letters --set full|capital|small` (alphabet A-T) and `--mode objects`.

---

## Alphabet series - templates A-T (default mode)

```
python main.py                 # --set full    : A-T, one 20-page PDF "Alphabet Workbook Aa-Zz"
python main.py --set capital   # A-J, 10 pages "Capital Letters A-Z"
python main.py --set small     # K-T, 10 pages "Small Letters a-z" (page numbers restart at 1)
```

| Tmpl | Title | Objective (Tujuan) |
|---|---|---|
| A-I | Huruf Besar A-C, D-F, G-I, J-L, M-O, P-R, S-U, V-X, Y-Z (Capital Letters) | Mengenal bentuk dan cara menulis huruf besar ... |
| J | Review Huruf Besar A-Z & Urutan Abjad | Mengulang huruf besar dan melatih urutan abjad. |
| K | Huruf Kecil a-c (Small Letters) | Menulis huruf kecil a-c dengan posisi yang tepat pada garis. |
| L | Huruf Kecil d-f | ... d-f ... |
| M | Huruf Kecil g-i | ... g-i ... |
| N | Huruf Kecil j-l | ... j-l ... |
| O | Huruf Kecil m-o | ... m-o ... |
| P | Huruf Kecil p-r | ... p-r ... |
| Q | Huruf Kecil s-u | ... s-u ... |
| R | Huruf Kecil v-z | ... v-z ... (5 letters, compact rows) |
| S | Membedakan Huruf Mirip (b-d, p-q, m-n) | Membedakan huruf yang bentuknya mirip. |
| T | Pasangan Huruf Besar-Kecil (Aa-Zz) | Mengaitkan huruf besar dengan pasangan huruf kecilnya. |

* **A-I (capitals):** model letter with numbered stroke order | 2 trace boxes + 2 write boxes | picture card.
* **K-R (small letters):** same bands, but every guide box has 4 lines: ascender (light), x-height (dashed), baseline (strong),
  descender (light) - so tall letters (b d f h k l t), round letters and tails (g j p q y) land in the right place.
* **S:** three pairs; each letter card has a picture, a shape hint (ID + EN) and a "circle the letter" row.
* **T:** Aa-Zz chart + draw-a-line matching (A D G N Q T to shuffled small letters).

Data: Excel sheet **Letters** (`ID | Letter | Word_EN | Word_ID | Image_Prompt`, one row per letter; used by both capital and small pages).
Stroke order: `wsengine/strokes.py` (`LETTERS` = capitals, `SMALL` = small letters, in "line space" units).
Page text: `config.LETTER_TEMPLATES` | layouts: `wsengine/letters.py` | product sets: `config.LETTER_SETS`.

`python main.py --mode objects` still runs the previous object/relation worksheets (templates A-E, described below).

---


One Excel row in → one product folder out: a 5-page A4 worksheet PDF, page PNGs, a preview sheet, a 2000×2000 cover and a 600×600 thumbnail.

```
python main.py                  # whole database
python main.py --only 001 003   # selected IDs
python main.py --qa-only        # quality checks only
python main.py --strict         # QA warnings also block a row
python main.py --templates ABE  # only some templates
```

Requirements: `pip install reportlab pillow pandas openpyxl pypdfium2`

---

## 1. Worksheet template design

Every page is built from the same four modules, so all products share one identity.

| Module | Content |
|---|---|
| **Header** | Nama / Date lines · template badge (A–E) · bilingual title · age pill (Ages 3–5 / Usia 3–5 tahun) · learning objective |
| **Image** | Main object + related object (vector art, thick navy outline, flat colours, smiling faces) |
| **Activity** | Matching · Tracing (+ clap syllables) · Circle the answer · Cut & paste · Coloring |
| **Vocabulary** | English word (large) + Indonesian word + "This is a chicken. / Ini adalah ayam." |
| **Footer** | Parent tip (ID + EN) · brand · "Halaman / Page n dari / of N" · copyright |

| Template | Colour | Activity | What the child does |
|---|---|---|---|
| A Animal Matching | blue | Matching | Draws lines between 3 object→relation pairs (row's pair + 2 distractor pairs) |
| B Vocabulary Learning | green | Tracing | ① look & say ② clap Indonesian syllables ③ trace dashed lowercase word |
| C Find and Circle | orange | Circle the answer | Circles the relation among 3, then the object among 3 |
| D Cut and Paste | pink | Cut & paste | Cuts 2 pictures, pastes them into labelled frames (frames are in the opposite order) |
| E Coloring | purple | Coloring | Colors a huge outline of the object, then the relation |

Print rules baked in: A4 portrait, 34 pt margins, ≥ 108 pt artwork, titles 25 pt, vocabulary 34 pt, 3.4 pt outlines, white background, no photos, no small details.
Add shadow matching / connect-the-dots later by adding a function to `templates.py` and a line in `config.TEMPLATES`.

## 2. Database mapping rules

| Excel column | Used for |
|---|---|
| `ID` | Output ordering, duplicate check, **seed** for repeatable shuffling (same row → same worksheet every run) |
| `Category` | Folder name (`&` → `and`) **and** wording group (`config.CATEGORY_WORDING`: animal/product, plant/fruit …) |
| `Object_EN` / `Object_ID` | Main word. Slug = lowercase, underscores → artwork file `assets/images/{slug}.png` |
| `Relation_EN` / `Relation_ID` | Paired word, same rules |
| `Image_Prompt` | Prompt for AI artwork; listed in `image_todo.csv` when no artwork exists; scanned for non-child-friendly words |

Placeholders (usable in every title / sentence in `config.py`):

| Token | Result for Chicken/Egg |
|---|---|
| `{OBJECT_EN}` `{OBJECT_ID}` `{RELATION_EN}` `{RELATION_ID}` | Chicken · Ayam · Egg · Telur (Capitalised) |
| `{object_en}` (lowercase token) | chicken |
| `{a_object_en}` / `{a_relation_en}` | a chicken / an egg (uncountables like *milk* → "milk", set in glossary) |
| `{OBJ_NOUN_EN}` `{REL_NOUN_ID}` … | animal · product · hewan · hasilnya (from Category) |

Derived automatically: Indonesian syllables for the clap boxes (rule-based, `ng/ny/sy/kh` kept together; override in glossary `Syllables_ID`), articles, trace word (lowercase).
Distractors for A and C come from **other rows** (same category first), so there is no extra data entry. Needs ≥ 3 rows per category for fully on-topic distractors.

## 3. Automation workflow

```
Excel ─► load + normalise ─► QA gate ─┬─► image_todo.csv ─► generate art ─► assets/images/{slug}.png
                                      │                                      (re-run; PNG overrides vector)
                                      └─► per row: build 5 pages ─► PDF ─► rasterise ─► Preview / Cover / Thumbnail
                                                                     └► manifest.csv
```

Output tree:

```
PRODUCTS/
  qa_report.csv  image_todo.csv  manifest.csv
  Animals and Their Products/
    Chicken/
      English_Indonesian_Worksheet.pdf
      Preview.png   Cover.png   Thumbnail.png
      pages/Page_A_….png … Page_E_….png
```

Quality gate (`wsengine/qa.py`)

| Check | Rule | Level |
|---|---|---|
| Complete | no empty field, unique ID, object ≠ relation | ERROR |
| Spelling | letters only, ≤ 2 words | ERROR |
| Translation | must match `data/vocabulary_glossary.csv` (`wol\|bulu domba` = alternatives) | ERROR on mismatch |
| Vocabulary | word must be in glossary (approved list) | WARNING (→ human check) |
| Age | ≤ 8 letters ideal, > 12 error, ≤ 6 syllables | WARNING / ERROR |
| Layout | word must fit the card at full size | ERROR |
| Images | artwork exists; prompt has no scary/realistic words | WARNING |

Automatic checks cannot confirm that a picture *looks like* its word: review `Preview.png` for each new batch (10 seconds per row), and keep the glossary as the single source of truth for translations.

## 4. Python structure

```
main.py                    CLI: load → QA → generate → reports
make_sample_db.py          builds the 5-row demo Excel
data/worksheet_database.xlsx, vocabulary_glossary.csv
assets/images/             optional {slug}.png (and {slug}_outline.png for coloring)
wsengine/
  config.py                brand, palette, fonts, TEMPLATES text, CATEGORY_WORDING
  database.py              Excel → Row, glossary, {PLACEHOLDER} engine, folder names
  linguistics.py           Indonesian syllables, a/an articles
  qa.py                    quality gate
  icons.py                 vector art kit + PNG override + outline mode
  modules.py               Header / Footer / cards / text helpers / Ctx (distractors)
  templates.py             object/relation templates A-E (--mode objects)
  letters.py               Capital Letters templates A-J (default)
  strokes.py               stroke-order data for A-Z
  renderer.py              PDF, rasterise, Preview, Cover, Thumbnail
```

## Scaling to thousands

* Replace the vector icons with AI artwork: run `main.py --qa-only`, feed `image_todo.csv` to your image generator, save as `assets/images/{slug}.png` (transparent PNG, square), re-run. Nothing else changes.
* Rows are independent, so batches can be parallelised with `multiprocessing` over `generate_row`.
* To rebrand, edit only `config.BRAND`, `TEMPLATE_COLORS` and fonts.
