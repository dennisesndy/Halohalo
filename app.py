"""
app.py
------
Flask application — all routes organised by feature section.

Sections:
  AUTH      /api/auth/*
  DASHBOARD /api/decks/*
  DECK      /api/decks/<id>/subjects, /api/subjects/<id>
  STUDY     /study/<id>, /api/study/<id>/fc|mc|id/*
  EXPORT    /api/decks/<id>/export
"""

import json
import os
import random
import requests

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, Response
)

from database import (
    init_db, register_user, login_user,
    get_decks, create_deck, update_deck, delete_deck, get_deck,
    get_subjects, get_subject, create_subject, update_subject, delete_subject,
    get_progress, upsert_progress, get_subject_mastery,
    get_score, upsert_score,
)
from engine import (
    parse_notes,
    build_fc_session, fc_insert_after_rating, fc_stats,
    generate_mc_question, check_mc, _is_true_false_item,
    generate_id_question, check_id,
    build_round_queue, build_explanation_prompt
)

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))

ROUND_SIZE = 10   # questions per MC / ID round

with app.app_context():
    init_db()


# ── Auth guard ─────────────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper


# ── AI explanation helper ──────────────────────────────────────────────────
def _get_ai_explanation(term, correct_def, chosen, is_correct, mode="mc"):
    """
    Call the Anthropic API for a short contextual explanation.
    Falls back to a static string if the call fails or the key is missing.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # No key — return a decent static fallback
        if is_correct:
            return f"✅ Correct! \"{correct_def}\" is the right answer."
        else:
            return f"The correct answer is: \"{correct_def}\"."

    prompt = build_explanation_prompt(term, correct_def, chosen, is_correct, mode)
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",
                "max_tokens": 120,
                "messages":   [{"role": "user", "content": prompt}],
            },
            timeout=8,
        )
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception:
        if is_correct:
            return f"✅ Correct! \"{correct_def}\" is the right answer."
        return f"The correct answer is: \"{correct_def}\"."


# =============================================================================
# AUTH ROUTES
# =============================================================================

@app.route("/")
def root():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/login")
def login_page():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.json or {}
    user, err = register_user(data.get("username", ""), data.get("pin", ""))
    if err:
        return jsonify({"error": err}), 400
    session["user_id"]  = user["id"]
    session["username"] = user["username"]
    return jsonify({"ok": True, "username": user["username"]})


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    user = login_user(data.get("username", ""), data.get("pin", ""))
    if not user:
        return jsonify({"error": "Invalid username or PIN."}), 401
    session["user_id"]  = user["id"]
    session["username"] = user["username"]
    return jsonify({"ok": True, "username": user["username"]})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})


# =============================================================================
# DASHBOARD
# =============================================================================

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])


@app.route("/api/decks", methods=["GET"])
@login_required
def api_get_decks():
    uid   = session["user_id"]
    decks = get_decks(uid)
    for deck in decks:
        subjects = get_subjects(deck["id"])
        deck["subject_count"] = len(subjects)
        total_mastery = sum(
            get_subject_mastery(uid, s["id"], len(json.loads(s["items_json"])))
            for s in subjects
        )
        deck["mastery"] = round(total_mastery / len(subjects)) if subjects else 0
    return jsonify(decks)


@app.route("/api/decks", methods=["POST"])
@login_required
def api_create_deck():
    data  = request.json or {}
    name  = data.get("name", "").strip()
    emoji = data.get("emoji", "📚")
    if not name:
        return jsonify({"error": "Deck name is required."}), 400
    deck_id = create_deck(session["user_id"], name, emoji)
    return jsonify({"id": deck_id, "name": name, "emoji": emoji})


@app.route("/api/decks/<int:deck_id>", methods=["PUT"])
@login_required
def api_update_deck(deck_id):
    data = request.json or {}
    update_deck(deck_id, data.get("name", "Untitled"), data.get("emoji", "📚"))
    return jsonify({"ok": True})


@app.route("/api/decks/<int:deck_id>", methods=["DELETE"])
@login_required
def api_delete_deck(deck_id):
    delete_deck(deck_id)
    return jsonify({"ok": True})


# =============================================================================
# DECK (subjects inside a deck)
# =============================================================================

@app.route("/deck/<int:deck_id>")
@login_required
def deck_page(deck_id):
    deck = get_deck(deck_id)
    if not deck:
        return redirect(url_for("dashboard"))
    return render_template("deck.html", deck=deck, username=session["username"])


@app.route("/api/decks/<int:deck_id>/subjects", methods=["GET"])
@login_required
def api_get_subjects(deck_id):
    uid      = session["user_id"]
    subjects = get_subjects(deck_id)
    result   = []
    for s in subjects:
        items    = json.loads(s["items_json"])
        mastery  = get_subject_mastery(uid, s["id"], len(items))
        mc_score = get_score(uid, s["id"], "mc")
        id_score = get_score(uid, s["id"], "id")
        result.append({
            "id":       s["id"],
            "name":     s["name"],
            "count":    len(items),
            "mastery":  mastery,
            "mc_score": mc_score,
            "id_score": id_score,
        })
    return jsonify(result)


@app.route("/api/decks/<int:deck_id>/subjects", methods=["POST"])
@login_required
def api_create_subject(deck_id):
    data = request.json or {}
    name = data.get("name", "").strip()
    raw  = data.get("raw", "")
    if not name:
        return jsonify({"error": "Subject name is required."}), 400
    items, errors = parse_notes(raw)
    if len(items) < 2:
        return jsonify({"error": "Need at least 2 valid items (term [TAB] definition)."}), 400
    sid = create_subject(deck_id, name, items)
    return jsonify({"id": sid, "name": name, "count": len(items), "skipped": errors})


@app.route("/api/subjects/<int:subject_id>", methods=["PUT"])
@login_required
def api_update_subject(subject_id):
    data  = request.json or {}
    name  = data.get("name", "").strip()
    raw   = data.get("raw", "")
    items, errors = parse_notes(raw)
    if len(items) < 2:
        return jsonify({"error": "Need at least 2 valid items."}), 400
    update_subject(subject_id, name, items)
    return jsonify({"ok": True, "count": len(items), "skipped": errors})


@app.route("/api/subjects/<int:subject_id>", methods=["DELETE"])
@login_required
def api_delete_subject(subject_id):
    delete_subject(subject_id)
    return jsonify({"ok": True})


# =============================================================================
# STUDY PAGE
# =============================================================================

@app.route("/study/<int:subject_id>")
@login_required
def study_page(subject_id):
    subj = get_subject(subject_id)
    if not subj:
        return redirect(url_for("dashboard"))
    deck = get_deck(subj["deck_id"])
    return render_template("study.html", subject=subj, deck=deck, ROUNDS=ROUND_SIZE,
                           username=session["username"])


# ── Flashcard ──────────────────────────────────────────────────────────────

@app.route("/api/study/<int:subject_id>/fc/start", methods=["POST"])
@login_required
def fc_start(subject_id):
    """Build / reset flashcard session using saved progress."""
    uid   = session["user_id"]
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    prog  = get_progress(uid, subject_id)
    deck  = build_fc_session(items, prog)
    session["fc"] = {"deck": deck, "index": 0, "sid": subject_id}
    return jsonify(_fc_state())


@app.route("/api/study/<int:subject_id>/fc/rate", methods=["POST"])
@login_required
def fc_rate(subject_id):
    """Rate the current card and advance the deck."""
    uid    = session["user_id"]
    rating = request.json.get("rating", 3)
    fc     = session.get("fc", {})

    if not fc or fc.get("sid") != subject_id:
        return jsonify({"error": "No active session"}), 400

    deck  = fc["deck"]
    index = fc["index"]

    if index < len(deck):
        term = deck[index]["term"]
        upsert_progress(uid, subject_id, term, rating)
        deck = fc_insert_after_rating(deck, index, rating)

    fc["deck"]  = deck
    fc["index"] = index
    session["fc"] = fc
    session.modified = True
    return jsonify(_fc_state())


def _fc_state():
    """Serialize current flashcard state for the frontend."""
    fc    = session.get("fc", {})
    deck  = fc.get("deck", [])
    index = fc.get("index", 0)
    stats = fc_stats(deck, index)

    if index >= len(deck):
        return {"done": True, **stats}

    card = deck[index]
    return {
        "done":    False,
        "term":    card["term"],
        "def":     card["def"],
        "rating":  card.get("rating", 0),
        **stats,
    }


# ── Multiple Choice ────────────────────────────────────────────────────────

def _mc_state(subject_id):
    """Return (or create) the MC session dict."""
    key = f"mc_{subject_id}"
    if key not in session:
        session[key] = {
            "correct": 0, "total": 0,
            "round": 1,
            "queue": [],        # terms remaining this round
            "used":  [],        # terms asked this round
            "wrong": [],        # wrong answers this round
            "prev_wrong": [],   # wrong answers last round (for next-round priority)
        }
    return session[key]


@app.route("/api/study/<int:subject_id>/mc/start", methods=["POST"])
@login_required
def mc_start(subject_id):
    """Reset and start a fresh MC session."""
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    session.pop(f"mc_{subject_id}", None)
    state = _mc_state(subject_id)
    state["queue"] = build_round_queue(items, [], 1, ROUND_SIZE)
    session[f"mc_{subject_id}"] = state
    session.modified = True
    return jsonify({"ok": True, "round": 1, "queue_size": len(state["queue"])})


@app.route("/api/study/<int:subject_id>/mc/question", methods=["GET"])
@login_required
def mc_question(subject_id):
    """Return next MC question from the round queue."""
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    if len(items) < 2:
        return jsonify({"error": "Need at least 2 items."}), 400

    state = _mc_state(subject_id)

    # Rebuild queue if somehow empty (defensive)
    if not state["queue"]:
        state["queue"] = build_round_queue(
            items, state.get("prev_wrong", []), state.get("round", 1), ROUND_SIZE)

    term_to_ask = state["queue"].pop(0)
    state["used"].append(term_to_ask)

    item_map = {i["term"]: i for i in items}
    item     = item_map.get(term_to_ask) or random.choice(items)
    correct  = item["def"]

    # Build choices
    if _is_true_false_item(item):
        q = {
            "term":    item["term"],
            "correct": correct.strip().capitalize(),
            "choices": ["True", "False"],
            "is_tf":   True,
        }
    else:
        others      = [i["def"] for i in items if i["def"].lower() != correct.lower()]
        distractors = random.sample(others, min(3, len(others)))
        choices     = distractors + [correct]
        random.shuffle(choices)
        q = {
            "term":    item["term"],
            "correct": correct,
            "choices": choices,
            "is_tf":   False,
        }

    q["round"]     = state.get("round", 1)
    q["remaining"] = len(state["queue"])

    session[f"mc_{subject_id}"] = state
    session.modified = True
    return jsonify(q)


@app.route("/api/study/<int:subject_id>/mc/answer", methods=["POST"])
@login_required
def mc_answer(subject_id):
    """Record MC answer and return AI explanation."""
    uid  = session["user_id"]
    data = request.json or {}
    term        = data.get("term", "")
    chosen      = data.get("chosen", "")
    correct_def = data.get("correct", "")
    is_correct  = check_mc(chosen, correct_def)

    state = _mc_state(subject_id)
    state["total"]   += 1
    state["correct"] += 1 if is_correct else 0
    if not is_correct:
        if term not in state["wrong"]:
            state["wrong"].append(term)

    session[f"mc_{subject_id}"] = state
    session.modified = True
    upsert_score(uid, subject_id, "mc", state["correct"], state["total"])

    explanation = _get_ai_explanation(term, correct_def, chosen, is_correct, "mc")
    pct = round(state["correct"] / state["total"] * 100) if state["total"] else 0

    return jsonify({
        "correct":     is_correct,
        "explanation": explanation,
        "mc_correct":  state["correct"],
        "mc_total":    state["total"],
        "mc_pct":      pct,
    })


@app.route("/api/study/<int:subject_id>/mc/next-round", methods=["POST"])
@login_required
def mc_next_round(subject_id):
    """Start the next MC round, prioritising previously-wrong answers."""
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    state = _mc_state(subject_id)

    state["round"]      += 1
    state["prev_wrong"]  = state["wrong"][:]
    state["wrong"]       = []
    state["used"]        = []
    state["queue"]       = build_round_queue(
        items, state["prev_wrong"], state["round"], ROUND_SIZE)

    session[f"mc_{subject_id}"] = state
    session.modified = True
    return jsonify({
        "ok":    True,
        "round": state["round"],
        "prev_wrong_count": len(state["prev_wrong"]),
    })


@app.route("/api/study/<int:subject_id>/mc/reset", methods=["POST"])
@login_required
def mc_reset(subject_id):
    session.pop(f"mc_{subject_id}", None)
    return jsonify({"ok": True})


# ── Identification ─────────────────────────────────────────────────────────

def _id_state(subject_id):
    """Return (or create) the ID session dict."""
    key = f"id_{subject_id}"
    if key not in session:
        session[key] = {
            "correct": 0, "total": 0,
            "round": 1,
            "queue": [], "used": [], "wrong": [], "prev_wrong": [],
        }
    return session[key]


@app.route("/api/study/<int:subject_id>/id/start", methods=["POST"])
@login_required
def id_start(subject_id):
    """Reset and start a fresh ID session."""
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    session.pop(f"id_{subject_id}", None)
    state = _id_state(subject_id)
    state["queue"] = build_round_queue(items, [], 1, ROUND_SIZE)
    session[f"id_{subject_id}"] = state
    session.modified = True
    return jsonify({"ok": True, "round": 1, "queue_size": len(state["queue"])})


@app.route("/api/study/<int:subject_id>/id/question", methods=["GET"])
@login_required
def id_question(subject_id):
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    state = _id_state(subject_id)

    if not state["queue"]:
        state["queue"] = build_round_queue(
            items, state.get("prev_wrong", []), state.get("round", 1), ROUND_SIZE)

    term_to_ask = state["queue"].pop(0)
    state["used"].append(term_to_ask)

    item_map = {i["term"]: i for i in items}
    item     = item_map.get(term_to_ask) or random.choice(items)

    session[f"id_{subject_id}"] = state
    session.modified = True
    return jsonify({
        "term":      item["term"],
        "correct":   item["def"],
        "round":     state.get("round", 1),
        "remaining": len(state["queue"]),
    })


@app.route("/api/study/<int:subject_id>/id/answer", methods=["POST"])
@login_required
def id_answer(subject_id):
    uid  = session["user_id"]
    data = request.json or {}
    term        = data.get("term", "")
    given       = data.get("given", "")
    correct_def = data.get("correct", "")
    is_correct  = check_id(given, correct_def)

    state = _id_state(subject_id)
    state["total"]   += 1
    state["correct"] += 1 if is_correct else 0
    if not is_correct and term not in state["wrong"]:
        state["wrong"].append(term)

    session[f"id_{subject_id}"] = state
    session.modified = True
    upsert_score(uid, subject_id, "id", state["correct"], state["total"])

    explanation = _get_ai_explanation(term, correct_def, given, is_correct, "id")
    pct = round(state["correct"] / state["total"] * 100) if state["total"] else 0

    return jsonify({
        "correct":     is_correct,
        "explanation": explanation,
        "id_correct":  state["correct"],
        "id_total":    state["total"],
        "id_pct":      pct,
    })


@app.route("/api/study/<int:subject_id>/id/next-round", methods=["POST"])
@login_required
def id_next_round(subject_id):
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    state = _id_state(subject_id)
    state["round"]      += 1
    state["prev_wrong"]  = state["wrong"][:]
    state["wrong"]       = []
    state["used"]        = []
    state["queue"]       = build_round_queue(
        items, state["prev_wrong"], state["round"], ROUND_SIZE)
    session[f"id_{subject_id}"] = state
    session.modified = True
    return jsonify({"ok": True, "round": state["round"],
                    "prev_wrong_count": len(state["prev_wrong"])})


@app.route("/api/study/<int:subject_id>/id/reset", methods=["POST"])
@login_required
def id_reset(subject_id):
    session.pop(f"id_{subject_id}", None)
    return jsonify({"ok": True})


# =============================================================================
# EXPORT
# =============================================================================

@app.route("/api/subjects/<int:subject_id>/export")
@login_required
def export_subject(subject_id):
    """Export a single subject as fully self-contained HTML — no server needed."""
    from exporter import build_subject_html
    subj = get_subject(subject_id)
    if not subj:
        return jsonify({"error": "Subject not found"}), 404
    items     = json.loads(subj["items_json"])
    html      = build_subject_html(subj["name"], items)
    safe_name = "".join(c for c in subj["name"] if c.isalnum() or c in " _-")
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_Reviewer.html"'},
    )


@app.route("/api/decks/<int:deck_id>/export")
@login_required
def export_deck(deck_id):
    """Export all subjects in a deck merged into one reviewer."""
    from exporter import build_subject_html
    deck     = get_deck(deck_id)
    subjects = get_subjects(deck_id)
    all_items = []
    for s in subjects:
        all_items.extend(json.loads(s["items_json"]))
    html      = build_subject_html(deck["name"], all_items)
    safe_name = "".join(c for c in deck["name"] if c.isalnum() or c in " _-")
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_Reviewer.html"'},
    )


# =============================================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)