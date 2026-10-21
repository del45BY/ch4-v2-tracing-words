"""Brand, palette, fonts, template definitions and category wording.

Everything visual or textual that is NOT row data lives here, so a re-brand
or a new template never touches the rendering code.
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
IMAGE_DIR = ROOT / "assets" / "images"  # optional PNG artwork named {slug}.png
OUTPUT_DIR = ROOT / "PRODUCTS"

# ------------------------------------------------------------------ brand
BRAND = {
    "name": "Preschool Digital Education Series",
    "tagline": "Indonesia & English",
    "copyright": "\u00a9 2026 Preschool Digital Education Series. For personal and classroom use only. Do not resell or redistribute.",
    "age_en": "Ages 3\u20135",
    "age_id": "Usia 3\u20135 tahun",
}

# ------------------------------------------------------------------ page
PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pt, portrait
MARGIN = 34
CONTENT_TOP = PAGE_H - 152  # just below the header module
CONTENT_BOTTOM = 100  # just above parent tip + footer

# ------------------------------------------------------------------ palette
NAVY, GREY, LIGHT, LINE = "#2B2D42", "#6B7280", "#F4F9FF", "#C9D6EA"
TEMPLATE_COLORS = {
    "A": "#4D9DE0",
    "B": "#3FB984",
    "C": "#F59E0B",
    "D": "#EC6A9B",
    "E": "#8B7CF6",
    "F": "#14B8A6",
    "G": "#EF4444",
    "H": "#6366F1",
    "I": "#84CC16",
    "J": "#F97316",
    "K": "#0EA5E9",
    "L": "#D946EF",
    "M": "#10B981",
    "N": "#E11D48",
    "O": "#7C3AED",
    "P": "#EAB308",
    "Q": "#06B6D4",
    "R": "#F43F5E",
    "S": "#22C55E",
    "T": "#2563EB",
}
SWATCHES = ["#FF595E", "#FFB703", "#FFD23F", "#6BCB77", "#4D9DE0", "#8B7CF6", "#C68642"]

# ------------------------------------------------------------------ fonts
_FONT_DIRS = [
    ROOT / "assets" / "fonts",
    Path("/usr/share/fonts/truetype/google-fonts"),
]


def _register(name: str, filename: str, fallback: str) -> str:
    for d in _FONT_DIRS:
        p = d / filename
        if p.exists():
            pdfmetrics.registerFont(TTFont(name, str(p)))
            return name
    return fallback


F_BOLD = _register("Brand-Bold", "Poppins-Bold.ttf", "Helvetica-Bold")
F_MED = _register("Brand-Medium", "Poppins-Medium.ttf", "Helvetica")
F_REG = _register("Brand-Regular", "Poppins-Regular.ttf", "Helvetica")
F_IT = _register("Brand-Italic", "Poppins-Italic.ttf", "Helvetica-Oblique")
FONT_FILE_BOLD = next(
    (str(d / "Poppins-Bold.ttf") for d in _FONT_DIRS if (d / "Poppins-Bold.ttf").exists()),
    None,
)
FONT_FILE_MED = next(
    (str(d / "Poppins-Medium.ttf") for d in _FONT_DIRS if (d / "Poppins-Medium.ttf").exists()),
    None,
)

# ------------------------------------------------------------------ category wording
# One template can say "animal / product" for farm rows and "plant / fruit" for plant rows.
CATEGORY_WORDING = {
    "Animals & Their Products": dict(
        obj_noun_en="animal", obj_noun_id="hewan", rel_noun_en="product", rel_noun_id="hasilnya"
    ),
    "Plants & Fruits": dict(
        obj_noun_en="plant", obj_noun_id="tumbuhan", rel_noun_en="fruit", rel_noun_id="buahnya"
    ),
}
DEFAULT_WORDING = dict(
    obj_noun_en="picture", obj_noun_id="gambar", rel_noun_en="picture", rel_noun_id="pasangannya"
)

# ------------------------------------------------------------------ template registry
# Placeholders: {OBJECT_EN} Capitalised | {object_en} lowercase | {a_object_en} "a chicken" / "an egg" / "milk"
TEMPLATES = {
    "A": dict(
        name="Animal Matching",
        title_en="Let's Match!",
        title_id="Ayo Cocokkan!",
        activity="Matching",
        goal_en="I can match things that belong together.",
        goal_id="Aku bisa mencocokkan benda yang berpasangan.",
        tip_en="Ask your child to say each word out loud before drawing the line.",
        tip_id="Minta anak menyebutkan setiap kata sebelum menarik garis.",
    ),
    "B": dict(
        name="Vocabulary Learning",
        title_en="Learn {OBJECT_EN} & {RELATION_EN}",
        title_id="Belajar {OBJECT_ID} & {RELATION_ID}",
        activity="Tracing",
        goal_en="I can say, clap and trace new words.",
        goal_id="Aku bisa menyebut, menepuk, dan menebalkan kata baru.",
        tip_en="Ask your child to act out the animal first, then say its name.",
        tip_id="Minta anak menirukan gerakan hewannya, lalu ucapkan namanya.",
    ),
    "C": dict(
        name="Find and Circle",
        title_en="Find and Circle",
        title_id="Cari dan Lingkari",
        activity="Circle the correct answer",
        goal_en="I can find the right picture.",
        goal_id="Aku bisa menemukan gambar yang tepat.",
        tip_en="Use a chunky crayon. Say the word together before circling.",
        tip_id="Gunakan krayon besar. Ucapkan katanya bersama sebelum melingkari.",
    ),
    "D": dict(
        name="Cut and Paste",
        title_en="Cut and Paste",
        title_id="Gunting dan Tempel",
        activity="Cutting and pasting",
        goal_en="I can cut and paste each picture in its place.",
        goal_id="Aku bisa menggunting dan menempel gambar di tempatnya.",
        tip_en="Use safety scissors and a glue stick. Help with cutting for younger children.",
        tip_id="Gunakan gunting aman dan lem stik. Bantu menggunting untuk anak yang lebih kecil.",
    ),
    "E": dict(
        name="Coloring Worksheet",
        title_en="Color the {OBJECT_EN}",
        title_id="Warnai {OBJECT_ID}",
        activity="Coloring",
        goal_en="I can color inside the lines.",
        goal_id="Aku bisa mewarnai di dalam garis.",
        tip_en="Let your child pick the colors. There is no wrong color!",
        tip_id="Biarkan anak memilih warnanya sendiri. Tidak ada warna yang salah!",
    ),
}
TEMPLATE_ORDER = ["A", "B", "C", "D", "E"]


# ------------------------------------------------------------------ CAPITAL LETTERS SERIES (templates A-J)
# One product = 10 pages. Titles/objectives are the series spec; edit text here only.
_LETTER_TIP_EN = "Say the letter name and sound together. Follow the numbered dots to write each letter."
_LETTER_TIP_ID = "Ucapkan nama dan bunyi huruf bersama. Ikuti titik bernomor saat menulis setiap huruf."


def _letter_spec(letters: str):
    rng = f"{letters[0]}\u2013{letters[-1]}"
    return dict(
        name=f"Capital Letters {letters[0]}-{letters[-1]}",
        title_en=f"Capital Letters {rng}",
        title_id=f"Huruf Besar {rng}",
        activity="Tracing + writing",
        letters=letters,
        goal_en=f"I can recognise and write capital letters {rng}.",
        goal_id=f"Mengenal bentuk dan cara menulis huruf besar {rng}.",
        tip_en=_LETTER_TIP_EN,
        tip_id=_LETTER_TIP_ID,
    )


LETTER_TEMPLATES = {
    "A": _letter_spec("ABC"),
    "B": _letter_spec("DEF"),
    "C": _letter_spec("GHI"),
    "D": _letter_spec("JKL"),
    "E": _letter_spec("MNO"),
    "F": _letter_spec("PQR"),
    "G": _letter_spec("STU"),
    "H": _letter_spec("VWX"),
    "I": _letter_spec("YZ"),
    "J": dict(
        name="Review A-Z and Alphabet Order",
        title_en="Review A\u2013Z & Alphabet Order",
        title_id="Review Huruf Besar A\u2013Z & Urutan Abjad",
        activity="Review + ordering",
        letters="",
        goal_en="I can review capital letters and put the alphabet in order.",
        goal_id="Mengulang huruf besar dan melatih urutan abjad.",
        tip_en="Sing the alphabet song while pointing at each letter in order.",
        tip_id="Nyanyikan lagu abjad sambil menunjuk setiap huruf secara berurutan.",
    ),
}
LETTER_ORDER = list("ABCDEFGHIJ")


# ------------------------------------------------------------------ SMALL LETTERS + REVIEW (templates K-T)
_SMALL_TIP_EN = "Start at the numbered dot. Tall letters touch the top line; round letters sit on the dashed middle line."
_SMALL_TIP_ID = "Mulai dari titik bernomor. Huruf tinggi menyentuh garis atas; huruf bulat berada di garis putus-putus."


def _small_spec(letters: str):
    rng = f"{letters[0]}\u2013{letters[-1]}"
    return dict(
        name=f"Small Letters {letters[0]}-{letters[-1]}",
        title_en=f"Small Letters {rng}",
        title_id=f"Huruf Kecil {rng}",
        activity="Tracing on 4 lines",
        letters=letters,
        goal_en=f"I can write small letters {rng} in the right place on the lines.",
        goal_id=f"Menulis huruf kecil {rng} dengan posisi yang tepat pada garis.",
        tip_en=_SMALL_TIP_EN,
        tip_id=_SMALL_TIP_ID,
    )


LETTER_TEMPLATES.update({
    "K": _small_spec("abc"),
    "L": _small_spec("def"),
    "M": _small_spec("ghi"),
    "N": _small_spec("jkl"),
    "O": _small_spec("mno"),
    "P": _small_spec("pqr"),
    "Q": _small_spec("stu"),
    "R": _small_spec("vwxyz"),
    "S": dict(
        name="Look-Alike Letters",
        title_en="Look-Alike Letters",
        title_id="Membedakan Huruf Mirip (b\u2013d, p\u2013q, m\u2013n)",
        activity="Discrimination + circling",
        letters="",
        goal_en="I can tell letters that look alike apart.",
        goal_id="Membedakan huruf yang bentuknya mirip.",
        tip_en="Say the picture word first: b for bee, d for duck. Use the hint to remember each shape.",
        tip_id="Ucapkan nama gambarnya dulu, misalnya b for Bee. Gunakan petunjuk untuk mengingat bentuk setiap huruf.",
    ),
    "T": dict(
        name="Capital-Small Pairs",
        title_en="Capital\u2013Small Pairs (Aa\u2013Zz)",
        title_id="Pasangan Huruf Besar\u2013Kecil (Aa\u2013Zz)",
        activity="Matching",
        letters="",
        goal_en="I can match each capital letter with its small letter.",
        goal_id="Mengaitkan huruf besar dengan pasangan huruf kecilnya.",
        tip_en="Point to a capital letter and ask: where is its small partner?",
        tip_id="Tunjuk huruf besar dan tanyakan: di mana pasangan huruf kecilnya?",
    ),
})

# Which pages go into which product (--set on the command line)
LETTER_SETS = {
    "capital": dict(order=list("ABCDEFGHIJ"), category="Alphabet", folder="Capital Letters A-Z",
                    title_en="Capital Letters A\u2013Z", title_id="Huruf Besar A\u2013Z",
                    banner="BILINGUAL ALPHABET WORKBOOK  \u2022  ENGLISH + BAHASA INDONESIA", tiles="ABC"),
    "small": dict(order=list("KLMNOPQRST"), category="Alphabet", folder="Small Letters a-z",
                  title_en="Small Letters a\u2013z", title_id="Huruf Kecil a\u2013z",
                  banner="BILINGUAL ALPHABET WORKBOOK  \u2022  ENGLISH + BAHASA INDONESIA", tiles="abc"),
    "full": dict(order=list("ABCDEFGHIJKLMNOPQRST"), category="Alphabet", folder="Alphabet Workbook Aa-Zz",
                 title_en="Alphabet Aa\u2013Zz", title_id="Huruf Besar & Huruf Kecil",
                 banner="BILINGUAL ALPHABET WORKBOOK  \u2022  ENGLISH + BAHASA INDONESIA", tiles="ABC"),
}


# ====================================================================== PHONICS SERIES (templates A-J) - DEFAULT
# Indonesian-first early-reading series. Page text lives here; the words come from sheet 'Words'.
PHONICS_TEMPLATES = {
    "A": dict(name="Bunyi Huruf Vokal", primary="id", title_id="Bunyi Huruf Vokal (a, i, u, e, o)",
              title_en="Vowel Sounds (a, i, u, e, o)", activity="Vowel sounds + tracing + matching",
              goal_id="Mengucapkan bunyi vokal, menebalkan huruf, dan mencocokkan gambar dengan vokal awalnya.",
              goal_en="Say the vowel sounds, trace the letters and match each picture to its first vowel.",
              tip_id="Ucapkan bunyi vokal keras-keras bersama anak, lalu sebutkan nama gambarnya.",
              tip_en="Say each vowel sound out loud together, then say the picture name."),
    "B": dict(name="Bunyi Awal Kata A-F", primary="id", title_id="Bunyi Awal Kata A\u2013F",
              title_en="Beginning Sounds A\u2013F", activity="First-sound circling",
              goal_id="Menyebutkan nama gambar dan melingkari huruf bunyi awalnya.",
              goal_en="Say each picture name and circle the letter of its beginning sound.",
              tip_id="Tekankan bunyi pertama: a-a-apel. Biarkan anak mendengar dulu sebelum memilih huruf.",
              tip_en="Stretch the first sound: a-a-apel. Let your child listen before choosing a letter."),
    "C": dict(name="Bunyi Awal Kata G-L", primary="id", title_id="Bunyi Awal Kata G\u2013L",
              title_en="Beginning Sounds G\u2013L", activity="Matching + writing the first letter",
              goal_id="Mencocokkan gambar dengan huruf awal dan menulis huruf awal kata.",
              goal_en="Match pictures to their first letter and write the first letter of each word.",
              tip_id="Mulai menulis dari titik atas. Pujilah usaha anak, bukan hanya hasil yang rapi.",
              tip_en="Start writing from the top. Praise effort, not only neat results."),
    "D": dict(name="Bunyi Awal Kata M-R", primary="id", title_id="Bunyi Awal Kata M\u2013R",
              title_en="Beginning Sounds M\u2013R", activity="Sorting by sound + completing letters",
              goal_id="Mengelompokkan gambar berdasarkan bunyi awal dan melengkapi huruf awal.",
              goal_en="Sort pictures by beginning sound and complete the first letter.",
              tip_id="Gunakan gunting aman dan lem stik. Bantu menggunting untuk anak yang lebih kecil.",
              tip_en="Use safety scissors and a glue stick. Help with cutting for younger children."),
    "E": dict(name="Bunyi Awal Kata S-Z", primary="id", title_id="Bunyi Awal Kata S\u2013Z",
              title_en="Beginning Sounds S\u2013Z", activity="Matching + completing words",
              goal_id="Mengelompokkan gambar, mencocokkan huruf, dan melengkapi kata.",
              goal_en="Group pictures, match letters and complete the words.",
              tip_id="Kerjakan satu kelompok gambar dulu, lalu istirahat sebentar sebelum kelompok berikutnya.",
              tip_en="Finish one group of pictures first, then take a short break before the next."),
    "F": dict(name="Suku Kata Dasar", primary="id", title_id="Suku Kata Dasar (ba, bi, bu, be, bo)",
              title_en="Basic Syllables (ba, bi, bu, be, bo)", activity="Syllable tracing + matching",
              goal_id="Menebalkan suku kata, membunyikan, dan mencocokkan dengan gambar.",
              goal_en="Trace syllables, sound them out and match them to pictures.",
              tip_id="Bunyikan b + a = ba sambil menepuk tangan satu kali untuk setiap suku kata.",
              tip_en="Sound it out: b + a = ba, clapping once for each syllable."),
    "G": dict(name="Suku Kata Lanjutan", primary="id", title_id="Suku Kata Lanjutan (ka, la, ma, na, sa)",
              title_en="More Syllables (ka, la, ma, na, sa)", activity="Syllable tracing + joining",
              goal_id="Menebalkan suku kata dan menyusun suku kata menjadi kata sederhana.",
              goal_en="Trace syllables and join them to make simple words.",
              tip_id="Baca suku kata satu per satu, lalu gabungkan: sa ... pi = sapi.",
              tip_en="Read the syllables one by one, then join them: sa ... pi = sapi."),
    "H": dict(name="Menyusun Kata Dua Suku Kata", primary="id", title_id="Menyusun Kata Dua Suku Kata",
              title_en="Building Two-Syllable Words", activity="Cut + paste word building",
              goal_id="Menyusun kata seperti bola, sapi, topi, dan bebek dari kartu suku kata.",
              goal_en="Build words such as bola, sapi, topi and bebek from syllable cards.",
              tip_id="Gunting kartu dulu, lalu coba susun dua suku kata dan bacakan hasilnya bersama.",
              tip_en="Cut the cards first, then try two syllables together and read the result aloud."),
    "I": dict(name="Gambar dan Kata Bilingual", primary="id", title_id="Pasangan Gambar & Kata Bilingual",
              title_en="Bilingual Picture\u2013Word Match", activity="Matching + word tracing",
              goal_id="Mencocokkan gambar dengan kata Indonesia dan Inggris, lalu menebalkan kata.",
              goal_en="Match pictures with Indonesian and English words, then trace the words.",
              tip_id="Ucapkan kata dalam dua bahasa: sapi ... cow. Ulangi sambil menunjuk gambar.",
              tip_en="Say each word in both languages: sapi ... cow. Repeat while pointing to the picture."),
    "J": dict(name="Kata Berima", primary="id", title_id="Kata Berima (Rhyming Words)",
              title_en="Rhyming Words", activity="Rhyme matching",
              goal_id="Mencocokkan gambar yang bunyi akhirnya sama, misalnya topi\u2013kopi, sapi\u2013api.",
              goal_en="Match pictures whose words end with the same sound, such as topi\u2013kopi.",
              tip_id="Ucapkan dua kata berima bersama-sama dan dengarkan bunyi akhirnya yang sama.",
              tip_en="Say the two rhyming words together and listen for the same ending sound."),
}

# Which words (keys = Word_ID from sheet 'Words') each page uses. Edit here to change page content.
PHONICS_CONTENT = {
    "A": ["apel", "ikan", "ular", "es krim", "ombak"],                      # vowels a i u e o
    "B": ["apel", "bebek", "cabai", "domba", "es krim", "foto"],            # A-F
    "C": ["gajah", "hati", "ikan", "jeruk", "kelinci", "lebah"],            # G-L
    "D": ["madu", "nanas", "ombak", "payung", "ratu", "rumah"],             # M-R (Q = Queen)
    "E": ["sapi", "topi", "ular", "vas", "wortel", "xilofon", "yoyo", "zebra"],  # S-Z
    "F": {"ba": "babi", "bi": "bintang", "bu": "buku", "be": "bebek", "bo": "bola"},
    "G": {"ka": "kapal", "ma": "mata", "na": "nanas", "sa": "sapi"},        # + 'la' is traced only
    "H": ["bola", "sapi", "topi", "bebek"],
    "I": ["sapi", "bebek", "ikan", "apel", "topi"],
    "J": [("topi", "kopi", "opi"), ("sapi", "api", "api"), ("payung", "burung", "ung")],  # (word, rhyme, ending)
}
PHONICS_LETTER_RANGES = {"A": "aiueo", "B": "abcdef", "C": "ghijkl", "D": "mnopqr", "E": "stuvwxyz"}
PHONICS_SET = dict(
    order=list("ABCDEFGHIJ"), category="Phonics", folder="Bunyi dan Suku Kata A-J",
    title_en="Sounds, Syllables & Words", title_id="Bunyi, Suku Kata & Kata",
    banner="BILINGUAL EARLY READING WORKBOOK  \u2022  BAHASA INDONESIA + ENGLISH",
)


# ====================================================================== PRE-WRITING & FINE MOTOR SERIES (templates A-J) - DEFAULT
SERIES_PREWRITE = "Pra-Menulis & Motorik Halus"
_PW_TIP_GRIP = "Pastikan anak duduk tegak dan memegang pensil dengan tiga jari (ibu jari, telunjuk, jari tengah)."
PREWRITE_TEMPLATES = {
    "A": dict(name="Garis Tegak", primary="id", series=SERIES_PREWRITE, title_id="Garis Tegak", title_en="Vertical Lines",
              activity="Vertical line tracing",
              goal_id="Melatih gerakan tangan menarik garis tegak dari atas ke bawah dengan lancar.",
              goal_en="Practise drawing straight vertical lines from top to bottom smoothly.",
              tip_id=_PW_TIP_GRIP, tip_en="Sit up straight and hold the pencil with three fingers (thumb, index and middle finger)."),
    "B": dict(name="Garis Datar", primary="id", series=SERIES_PREWRITE, title_id="Garis Datar", title_en="Horizontal Lines",
              activity="Horizontal line tracing",
              goal_id="Melatih gerakan menarik garis datar dari kiri ke kanan, arah yang sama dengan membaca.",
              goal_en="Practise drawing horizontal lines from left to right, the same direction as reading.",
              tip_id="Letakkan telunjuk tangan yang lain di titik awal sebagai pengingat arah.",
              tip_en="Place a finger of the other hand on the start dot as a reminder of the direction."),
    "C": dict(name="Garis Miring", primary="id", series=SERIES_PREWRITE, title_id="Garis Miring", title_en="Diagonal Lines",
              activity="Diagonal line tracing",
              goal_id="Melatih kontrol tangan untuk menarik garis miring ke kanan dan ke kiri.",
              goal_en="Practise controlled diagonal lines to the right and to the left.",
              tip_id="Putar kertas bila perlu agar tangan anak nyaman menarik garis.",
              tip_en="Turn the paper if needed so your child's hand moves comfortably."),
    "D": dict(name="Garis Zigzag", primary="id", series=SERIES_PREWRITE, title_id="Garis Zigzag", title_en="Zigzag Lines",
              activity="Zigzag line tracing",
              goal_id="Melatih gerakan tangan naik-turun yang cepat dan terkontrol.",
              goal_en="Practise quick, controlled up-and-down hand movements.",
              tip_id="Ajak anak mengucapkan \"naik-turun\" setiap kali menarik garis.",
              tip_en="Say \"up-down\" together each time a line is drawn."),
    "E": dict(name="Garis Lengkung", primary="id", series=SERIES_PREWRITE, title_id="Garis Lengkung", title_en="Curved Lines",
              activity="Curved line tracing",
              goal_id="Melatih gerakan lengkung sebagai dasar menulis huruf bundar seperti c, o, dan s.",
              goal_en="Practise curved movements, the base of round letters such as c, o and s.",
              tip_id="Biarkan anak bergerak pelan; kelancaran lebih penting daripada kecepatan.",
              tip_en="Let your child go slowly; smoothness matters more than speed."),
    "F": dict(name="Garis Gelombang", primary="id", series=SERIES_PREWRITE, title_id="Garis Gelombang", title_en="Wavy Lines",
              activity="Wavy line tracing",
              goal_id="Melatih gerakan gelombang yang halus dan berulang.",
              goal_en="Practise smooth, repeated wave movements.",
              tip_id="Gunakan krayon besar atau pensil warna agar mudah dipegang.",
              tip_en="Use chunky crayons or colored pencils for an easy grip."),
    "G": dict(name="Lingkaran dan Spiral", primary="id", series=SERIES_PREWRITE, title_id="Lingkaran & Spiral", title_en="Circles & Spirals",
              activity="Circle and spiral tracing",
              goal_id="Melatih gerakan memutar untuk membuat lingkaran, spiral, dan lilitan.",
              goal_en="Practise circular movements to make circles, spirals and loops.",
              tip_id="Gambar lingkaran berlawanan arah jarum jam, mulai dari atas.",
              tip_en="Draw circles counter-clockwise, starting from the top."),
    "H": dict(name="Pola Campuran", primary="id", series=SERIES_PREWRITE, title_id="Pola Campuran", title_en="Mixed Patterns",
              activity="Pattern continuing",
              goal_id="Menggabungkan beberapa jenis garis menjadi pola yang berulang.",
              goal_en="Combine different kinds of lines into repeating patterns.",
              tip_id="Minta anak menyebutkan polanya: naik, turun, naik, turun ...",
              tip_en="Ask your child to say the pattern aloud: up, down, up, down ..."),
    "I": dict(name="Mengikuti Jalur", primary="id", series=SERIES_PREWRITE, title_id="Mengikuti Jalur", title_en="Path Tracing",
              activity="Path tracing",
              goal_id="Melatih kontrol pensil agar tetap berada di dalam jalur dari awal sampai tujuan.",
              goal_en="Practise keeping the pencil inside the path from start to finish.",
              tip_id="Pujilah usaha anak, bukan hanya jalur yang rapi.",
              tip_en="Praise effort, not only neat paths."),
    "J": dict(name="Menebalkan Bentuk Dasar", primary="id", series=SERIES_PREWRITE, title_id="Menebalkan Bentuk Dasar", title_en="Shape Tracing",
              activity="Basic shape tracing",
              goal_id="Menebalkan bentuk dasar sebagai persiapan menulis huruf dan angka.",
              goal_en="Trace basic shapes to prepare for writing letters and numbers.",
              tip_id="Sebut nama setiap bentuk bersama-sama: lingkaran, persegi, segitiga ...",
              tip_en="Name each shape together: circle, square, triangle ..."),
}
# start -> goal picture pairs (keys = Word_ID from sheet 'Words'); edit freely
PREWRITE_CONTENT = {
    "B": [("lebah", "madu"), ("kelinci", "wortel"), ("ikan", "ombak"), ("burung", "rumah")],
    "D": [("gajah", "jeruk"), ("babi", "apel"), ("bebek", "kapal")],
    "E": [("bola", "bintang")],
    "F": [("bebek", "ombak"), ("ular", "hati"), ("ikan", "kapal")],
    "I": [("lebah", "madu"), ("kelinci", "wortel"), ("ikan", "ombak"), ("babi", "rumah")],
}
PREWRITE_SET = dict(
    order=list("ABCDEFGHIJ"), category="Pra-Menulis", folder="Pra-Menulis dan Motorik Halus A-J",
    title_id="Pra-Menulis & Motorik Halus", title_en="Pre-Writing & Fine Motor Skills",
    banner="BILINGUAL PRE-WRITING WORKBOOK  \u2022  BAHASA INDONESIA + ENGLISH",
)


# ====================================================================== TRACING WORDS SERIES (templates A-T) - DEFAULT
# Pure layout + text. NO artwork is drawn by code: put one picture per word in assets/images/ (see image_list.csv).
TRACING_SET = dict(
    category="Menebalkan Kata", all_order=list("ABCDEFGHIJKLMNOPQRST"),
    title_id="Menebalkan Kata", title_en="Tracing Words",
    banner="BILINGUAL TRACING WORDS WORKBOOK  \u2022  BAHASA INDONESIA + ENGLISH",
    image_exts=(".png", ".jpg", ".jpeg"),
    trace_band=True,   # soft pale band under the single dashed stroke (False = dashed line only)
)
