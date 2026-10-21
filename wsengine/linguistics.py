"""Small language helpers used for clap-the-syllables boxes and sentences."""
import re

_VOWELS = set("aiueo")
_DIGRAPHS = ("ng", "ny", "sy", "kh")


def _units(word: str) -> list[str]:
    """Split a word into letters, keeping ng / ny / sy / kh together as one consonant."""
    units, i = [], 0
    while i < len(word):
        if word[i : i + 2] in _DIGRAPHS:
            units.append(word[i : i + 2])
            i += 2
        else:
            units.append(word[i])
            i += 1
    return units


def _syllabify_word(word: str) -> list[str]:
    units = _units(word)
    vowels = [k for k, u in enumerate(units) if u in _VOWELS]
    if len(vowels) < 2:
        return [word]
    cuts = []
    for a, b in zip(vowels, vowels[1:]):
        between = b - a - 1
        if between == 0:      # V-V  -> pa-us, hi-u
            cuts.append(b)
        elif between == 1:    # V-CV -> le-bah
            cuts.append(b - 1)
        else:                 # VC-CV -> dom-ba
            cuts.append(a + 2)
    bounds = [0] + cuts + [len(units)]
    return ["".join(units[s:e]) for s, e in zip(bounds, bounds[1:])]


def syllabify_id(text: str, override: str | None = None) -> list[str]:
    """Indonesian syllables. `override` (e.g. 'ba-bi') comes from the glossary and wins."""
    if override:
        return [s for s in re.split(r"[\s\-]+", override.lower()) if s]
    out: list[str] = []
    for w in re.split(r"[\s\-]+", text.lower().strip()):
        if w:
            out += _syllabify_word(w)
    return out


_AN_EXCEPTIONS = {"hour", "honest"}
_A_EXCEPTIONS = ("uni", "use", "one")


def article_phrase(word: str, countable: bool = True) -> str:
    """'chicken' -> 'a chicken', 'egg' -> 'an egg', 'milk' -> 'milk' (uncountable)."""
    w = word.strip().lower()
    if not countable:
        return w
    first = w.split()[0] if w else w
    if first in _AN_EXCEPTIONS or (first[:1] in _VOWELS and not first.startswith(_A_EXCEPTIONS)):
        return f"an {w}"
    return f"a {w}"


def capitalise(text: str) -> str:
    t = text.strip()
    return t[:1].upper() + t[1:]
