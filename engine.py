"""
engine.py
---------
Pure-logic study engine (stateless functions).
All state is stored in the Flask session so it survives page refreshes.
No HTML/JS lives here - see exporter.py for the export template.
"""

import random
import json


# ─────────────────────────────────────────────────────────────────────────────
# Text parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_notes(raw: str):
    """
    Parse tab-separated (or double-space-separated) notes.
    Returns (items, errors) where items = [{"term":str, "def":str}].
    """
    import re
    items, errors = [], []
    for i, line in enumerate(raw.strip().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if "\t" in line:
            parts = line.split("\t", 1)
        else:
            parts = re.split(r"  +", line, maxsplit=1)

        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            items.append({"term": parts[0].strip(), "def": parts[1].strip()})
        else:
            errors.append(f"Line {i} skipped (no separator found)")
    return items, errors


# ─────────────────────────────────────────────────────────────────────────────
# Flashcard – Spaced Repetition (SM-2 inspired)
# ─────────────────────────────────────────────────────────────────────────────

def build_fc_session(items, progress):
    """
    Build an ordered deck using saved progress ratings.
    Cards with lower ratings bubble to the front (unseen = 0 → front).
    Returns list of {"term", "def", "rating"}.
    """
    def sort_key(item):
        p = progress.get(item["term"], {})
        return p.get("rating", 0)

    deck = sorted(items, key=sort_key)
    return [
        {
            "term":   it["term"],
            "def":    it["def"],
            "rating": progress.get(it["term"], {}).get("rating", 0),
        }
        for it in deck
    ]


def fc_insert_after_rating(deck, index, rating):
    """
    Remove card at index, re-insert based on rating:
      1 → 3 positions ahead  (see again very soon)
      2 → 5 positions ahead
      3-4 → middle of remaining deck
      5 → end of deck (mastered)
    Returns updated deck.
    """
    card = deck.pop(index)
    card["rating"] = rating
    remaining = len(deck) - index

    if rating == 1:
        insert_at = min(index + 3, len(deck))
    elif rating == 2:
        insert_at = min(index + 5, len(deck))
    elif rating in (3, 4):
        insert_at = index + max(1, remaining // 2)
    else:
        insert_at = len(deck)

    deck.insert(insert_at, card)
    return deck


def fc_stats(deck, index):
    """Compute live flashcard progress stats for the frontend."""
    rated_5  = [c for c in deck if c.get("rating", 0) == 5]
    rated_12 = [c for c in deck if c.get("rating", 0) in (1, 2)]
    total    = len(deck)
    mastered = len(rated_5)
    pct      = round(mastered / total * 100) if total else 0
    return {
        "total":      total,
        "mastered":   mastered,
        "struggling": len(rated_12),
        "remaining":  max(0, total - index),
        "pct":        pct,
        "position":   index + 1,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Multiple Choice
# ─────────────────────────────────────────────────────────────────────────────

def generate_mc_question(items, used_terms=None):
    """
    Pick a random item (avoiding recently used terms if possible).
    Returns {"term", "correct", "choices": [4 strings]}.
    """
    if not items:
        return {}

    pool = items
    if used_terms:
        filtered = [i for i in items if i["term"] not in used_terms]
        if filtered:
            pool = filtered

    item    = random.choice(pool)
    correct = item["def"]

    others      = [i["def"] for i in items if i["def"] != correct]
    distractors = random.sample(others, min(3, len(others)))

    choices = distractors + [correct]
    random.shuffle(choices)

    return {"term": item["term"], "correct": correct, "choices": choices}


def check_mc(chosen, correct):
    return chosen.strip().lower() == correct.strip().lower()


# ─────────────────────────────────────────────────────────────────────────────
# Identification
# ─────────────────────────────────────────────────────────────────────────────

def generate_id_question(items, used_terms=None):
    """Returns {"term", "correct"}."""
    if not items:
        return {}
    pool = items
    if used_terms:
        filtered = [i for i in items if i["term"] not in used_terms]
        if filtered:
            pool = filtered
    item = random.choice(pool)
    return {"term": item["term"], "correct": item["def"]}


def check_id(given, correct):
    """Case-insensitive, strips whitespace."""
    return given.strip().lower() == correct.strip().lower()


# ─────────────────────────────────────────────────────────────────────────────
# Export  (delegates to exporter.py which holds the JS-heavy HTML template)
# ─────────────────────────────────────────────────────────────────────────────

def generate_export_html(deck_name, subjects):
    """
    Generate a fully standalone HTML reviewer.
    subjects = [{"name": str, "items": [{"term", "def"}]}]
    Delegates to exporter.py to keep JS out of Python source.
    """
    from exporter import build_export_html
    return build_export_html(deck_name, subjects)