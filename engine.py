"""
engine.py
---------
Pure-logic study engine (stateless functions).
State is stored in Flask session; DB handles persistence.

Key changes vs previous version:
  - MC: detects True/False questions → 2 choices only
  - MC: uses term-distractors instead of definition-distractors
        (question shows term, choices are definitions — so distractors
         must be other definitions from the same pool)
  - MC: generates an AI explanation via Claude API (called from app.py)
  - FC: fc_stats now counts every rating bucket (1-2, 3-4, 5, unseen)
  - Round queue: tracks wrong answers for re-appearance next round
"""

import random


# ─────────────────────────────────────────────────────────────────────────────
# Text parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_notes(raw: str):
    """
    Parse tab-separated (or 2+-space-separated) notes.
    Returns (items, errors).
    items = [{"term": str, "def": str}]
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
            errors.append(f"Line {i} skipped (no tab/double-space separator found)")
    return items, errors


# ─────────────────────────────────────────────────────────────────────────────
# Flashcard – SM-2 inspired spaced repetition
# ─────────────────────────────────────────────────────────────────────────────

def build_fc_session(items, progress):
    """
    Build an ordered deck from saved progress.
    Unseen cards (rating 0) come first, then low-rated, then high-rated.
    Returns list of {"term", "def", "rating"}.
    """
    def sort_key(item):
        return progress.get(item["term"], {}).get("rating", 0)

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
    Remove card at index and re-insert it based on difficulty rating:
      1 (Again)  → back in 3 slots  — see very soon
      2 (Hard)   → back in 5 slots  — see soon
      3 (Okay)   → middle of remaining deck
      4 (Good)   → ¾ through remaining deck
      5 (Easy)   → end of deck (mastered)
    """
    card = deck.pop(index)
    card["rating"] = rating
    remaining = len(deck) - index

    if rating == 1:
        insert_at = min(index + 3, len(deck))
    elif rating == 2:
        insert_at = min(index + 5, len(deck))
    elif rating == 3:
        insert_at = index + max(1, remaining // 2)
    elif rating == 4:
        insert_at = index + max(1, (remaining * 3) // 4)
    else:  # 5 — mastered
        insert_at = len(deck)

    deck.insert(insert_at, card)
    return deck


def fc_stats(deck, index):
    """
    Return counts for every rating bucket so the UI can colour-code them.
    Buckets:
      unseen     rating == 0
      again      rating == 1
      hard       rating == 2
      okay       rating == 3
      good       rating == 4
      mastered   rating == 5
    """
    counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for card in deck:
        r = card.get("rating", 0)
        counts[r] = counts.get(r, 0) + 1

    total    = len(deck)
    mastered = counts[5]
    pct      = round(mastered / total * 100) if total else 0

    return {
        "total":     total,
        "unseen":    counts[0],
        "again":     counts[1],
        "hard":      counts[2],
        "okay":      counts[3],
        "good":      counts[4],
        "mastered":  counts[5],
        "struggling": counts[1] + counts[2],      # kept for backwards compat
        "remaining": max(0, total - index),
        "pct":       pct,
        "position":  index + 1,
        # breakdown list for the colour bar
        "breakdown": [
            {"label": "Unseen",   "count": counts[0], "color": "#9ca3af"},
            {"label": "Again",    "count": counts[1], "color": "#ef4444"},
            {"label": "Hard",     "count": counts[2], "color": "#f97316"},
            {"label": "Okay",     "count": counts[3], "color": "#eab308"},
            {"label": "Good",     "count": counts[4], "color": "#84cc16"},
            {"label": "Mastered", "count": counts[5], "color": "#22c55e"},
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Multiple Choice — smart question generation
# ─────────────────────────────────────────────────────────────────────────────

_TRUE_FALSE_KEYWORDS = frozenset([
    "true", "false", "yes", "no", "correct", "incorrect",
    "right", "wrong", "always", "never",
])

def _is_true_false_item(item):
    """
    Return True if this item's definition looks like a True/False question.
    Heuristic: definition is a single word that is in the T/F keyword set.
    """
    defn = item["def"].strip().lower()
    return defn in _TRUE_FALSE_KEYWORDS


def generate_mc_question(items, priority_terms=None, used_terms=None):
    """
    Build one multiple-choice question.

    Selection priority:
      1. priority_terms (wrong answers from last round) if available
      2. items not in used_terms (avoids recent repeats within same round)
      3. any item (fallback)

    True/False detection:
      If the chosen item's definition is a T/F keyword, return only
      ["True", "False"] as choices.

    Otherwise return up to 4 choices (1 correct + 3 distractors drawn
    from OTHER definitions in the pool, not terms).

    Returns:
      {
        "term": str,
        "correct": str,
        "choices": [str, ...],   # 2 or 4 items, shuffled
        "is_tf": bool,
      }
    """
    if not items:
        return {}

    # ── Choose which item to ask about ────────────────────────────────────
    pool = items

    # Prioritise previously-wrong items
    if priority_terms:
        pri = [i for i in items if i["term"] in priority_terms]
        if pri:
            pool = pri

    # Within that pool, avoid recently used
    if used_terms:
        fresh = [i for i in pool if i["term"] not in used_terms]
        if fresh:
            pool = fresh

    item    = random.choice(pool)
    correct = item["def"]

    # ── True / False branch ────────────────────────────────────────────────
    if _is_true_false_item(item):
        choices = ["True", "False"]
        # Normalise correct to match capitalisation
        correct = correct.strip().capitalize()
        return {
            "term":    item["term"],
            "correct": correct,
            "choices": choices,
            "is_tf":   True,
        }

    # ── Normal MC branch ───────────────────────────────────────────────────
    # Distractors = other definitions (not the correct one)
    other_defs   = [i["def"] for i in items if i["def"].lower() != correct.lower()]
    distractors  = random.sample(other_defs, min(3, len(other_defs)))

    choices = distractors + [correct]
    random.shuffle(choices)

    return {
        "term":    item["term"],
        "correct": correct,
        "choices": choices,
        "is_tf":   False,
    }


def check_mc(chosen, correct):
    """Case-insensitive exact match."""
    return chosen.strip().lower() == correct.strip().lower()


# ─────────────────────────────────────────────────────────────────────────────
# Identification
# ─────────────────────────────────────────────────────────────────────────────

def generate_id_question(items, priority_terms=None, used_terms=None):
    """
    Pick an item to ask, honouring priority_terms (wrong last round)
    and avoiding used_terms (recent repeats).
    Returns {"term", "correct"}.
    """
    if not items:
        return {}

    pool = items
    if priority_terms:
        pri = [i for i in items if i["term"] in priority_terms]
        if pri:
            pool = pri

    if used_terms:
        fresh = [i for i in pool if i["term"] not in used_terms]
        if fresh:
            pool = fresh

    item = random.choice(pool)
    return {"term": item["term"], "correct": item["def"]}


def check_id(given, correct):
    """Case-insensitive, strips leading/trailing whitespace."""
    return given.strip().lower() == correct.strip().lower()


# ─────────────────────────────────────────────────────────────────────────────
# AI Explanation  (called from app.py after an MC/ID answer)
# ─────────────────────────────────────────────────────────────────────────────

def build_explanation_prompt(term, correct_def, chosen, is_correct, mode="mc"):
    """
    Build a prompt for the Claude API to explain a MC or ID answer.
    Returns a short prompt string.
    """
    if is_correct:
        return (
            f"The student answered a flashcard question correctly.\n"
            f"Term: \"{term}\"\n"
            f"Definition: \"{correct_def}\"\n"
            f"Give a single encouraging sentence (max 25 words) that reinforces why "
            f"this answer is right. Be warm and specific to the content."
        )
    else:
        if mode == "mc":
            return (
                f"A student chose the wrong answer in a multiple-choice quiz.\n"
                f"Term: \"{term}\"\n"
                f"Correct definition: \"{correct_def}\"\n"
                f"Student chose: \"{chosen}\"\n"
                f"In 1–2 sentences (max 40 words), explain clearly why the correct "
                f"answer is right and why their choice was wrong. Be kind but direct."
            )
        else:  # identification
            return (
                f"A student typed the wrong answer in an identification quiz.\n"
                f"Term: \"{term}\"\n"
                f"Correct definition: \"{correct_def}\"\n"
                f"Student wrote: \"{chosen}\"\n"
                f"In 1–2 sentences (max 40 words), explain why the correct answer "
                f"is right. Be encouraging and clear."
            )


# ─────────────────────────────────────────────────────────────────────────────
# Round queue management  (knowledge-retention logic)
# ─────────────────────────────────────────────────────────────────────────────

def build_round_queue(items, wrong_from_last_round, round_number, round_size=10):
    """
    Build the ordered list of terms for a quiz round.

    Strategy:
      - Always include all wrong-from-last-round items (up to round_size)
      - Fill remaining slots with fresh items not seen in last round
      - Shuffle the result

    Returns a list of term strings (not full item dicts).
    """
    wrong_set = set(wrong_from_last_round or [])
    all_terms = [i["term"] for i in items]

    priority = [t for t in all_terms if t in wrong_set]
    fresh    = [t for t in all_terms if t not in wrong_set]
    random.shuffle(fresh)

    # Fill up to round_size: wrongs first, then fresh
    queue = priority + fresh
    queue = queue[:round_size]
    random.shuffle(queue)
    return queue


# ─────────────────────────────────────────────────────────────────────────────
# Export  (delegates to exporter.py)
# ─────────────────────────────────────────────────────────────────────────────

def generate_export_html(deck_name, subjects):
    """Delegates to exporter.py to keep JS out of this file."""
    from exporter import build_export_html
    return build_export_html(deck_name, subjects)