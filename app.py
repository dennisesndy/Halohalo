"""
app.py
------
Flask application entry point.
All routes are grouped by feature: Auth, Decks, Subjects, Study, Export.
"""

import json
import os
import random


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
    generate_mc_question, check_mc,
    generate_id_question, check_id,
    generate_export_html,
)

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))

# Initialise database on startup
with app.app_context():
    init_db()


# ── Auth guard decorator ───────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])


@app.route("/api/decks", methods=["GET"])
@login_required
def api_get_decks():
    uid   = session["user_id"]
    decks = get_decks(uid)

    # Enrich each deck with subject count + overall mastery
    for deck in decks:
        subjects = get_subjects(deck["id"])
        deck["subject_count"] = len(subjects)

        # Aggregate mastery across all subjects in this deck
        total_mastery = 0
        for subj in subjects:
            items = json.loads(subj["items_json"])
            total_mastery += get_subject_mastery(uid, subj["id"], len(items))

        deck["mastery"] = round(total_mastery / len(subjects)) if subjects else 0

    return jsonify(decks)


@app.route("/api/decks", methods=["POST"])
@login_required
def api_create_deck():
    data = request.json or {}
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


# ─────────────────────────────────────────────────────────────────────────────
# DECK VIEW  (subjects inside a deck)
# ─────────────────────────────────────────────────────────────────────────────

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
        items   = json.loads(s["items_json"])
        mastery = get_subject_mastery(uid, s["id"], len(items))
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


# ─────────────────────────────────────────────────────────────────────────────
# STUDY PAGE
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/study/<int:subject_id>")
@login_required
def study_page(subject_id):
    subj = get_subject(subject_id)
    if not subj:
        return redirect(url_for("dashboard"))
    deck = get_deck(subj["deck_id"])
    return render_template("study.html",
                           subject=subj, deck=deck,
                           username=session["username"])


# ── Flashcard endpoints ───────────────────────────────────────────────────

@app.route("/api/study/<int:subject_id>/fc/start", methods=["POST"])
@login_required
def fc_start(subject_id):
    """Build / reset flashcard session."""
    uid   = session["user_id"]
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    prog  = get_progress(uid, subject_id)

    deck  = build_fc_session(items, prog)
    session["fc"] = {"deck": deck, "index": 0, "sid": subject_id}
    return jsonify(fc_current_state())


@app.route("/api/study/<int:subject_id>/fc/rate", methods=["POST"])
@login_required
def fc_rate(subject_id):
    """Rate current card and advance."""
    uid    = session["user_id"]
    rating = request.json.get("rating", 3)
    fc     = session.get("fc", {})

    if not fc or fc.get("sid") != subject_id:
        return jsonify({"error": "No active session"}), 400

    deck  = fc["deck"]
    index = fc["index"]

    if index < len(deck):
        term = deck[index]["term"]
        # Save rating to DB
        upsert_progress(uid, subject_id, term, rating)
        # Re-shuffle deck with SM-2 logic
        deck = fc_insert_after_rating(deck, index, rating)

    fc["deck"]  = deck
    fc["index"] = index   # index stays; card was removed and re-inserted
    session["fc"] = fc
    session.modified = True

    return jsonify(fc_current_state())


def fc_current_state():
    """Serialize current FC session state for the frontend."""
    fc    = session.get("fc", {})
    deck  = fc.get("deck", [])
    index = fc.get("index", 0)
    stats = fc_stats(deck, index)

    if index >= len(deck):
        return {"done": True, **stats}

    card = deck[index]
    return {
        "done":  False,
        "term":  card["term"],
        "def":   card["def"],
        "rating": card.get("rating", 0),
        **stats,
    }


# ── Multiple Choice endpoints ─────────────────────────────────────────────

@app.route("/api/study/<int:subject_id>/mc/question", methods=["GET"])
@login_required
def mc_question(subject_id):
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    if len(items) < 4:
        return jsonify({"error": "Need at least 4 items for Multiple Choice."}), 400

    used  = session.get("mc_used", [])
    q     = generate_mc_question(items, used)

    # Track recently used to avoid repeats
    used.append(q["term"])
    if len(used) > len(items) // 2:
        used = used[-(len(items) // 2):]
    session["mc_used"] = used

    return jsonify(q)


@app.route("/api/study/<int:subject_id>/mc/answer", methods=["POST"])
@login_required
def mc_answer(subject_id):
    uid     = session["user_id"]
    data    = request.json or {}
    correct = check_mc(data.get("chosen", ""), data.get("correct", ""))

    # Update running score in session
    mc = session.get(f"mc_{subject_id}", {"correct": 0, "total": 0})
    mc["total"]   += 1
    mc["correct"] += 1 if correct else 0
    session[f"mc_{subject_id}"] = mc
    session.modified = True

    # Persist to DB
    upsert_score(uid, subject_id, "mc", mc["correct"], mc["total"])

    return jsonify({
        "correct":    correct,
        "mc_correct": mc["correct"],
        "mc_total":   mc["total"],
        "mc_pct":     round(mc["correct"] / mc["total"] * 100),
    })


@app.route("/api/study/<int:subject_id>/mc/reset", methods=["POST"])
@login_required
def mc_reset(subject_id):
    session.pop(f"mc_{subject_id}", None)
    session.pop("mc_used", None)
    return jsonify({"ok": True})


# ── Identification endpoints ──────────────────────────────────────────────

@app.route("/api/study/<int:subject_id>/id/question", methods=["GET"])
@login_required
def id_question(subject_id):
    subj  = get_subject(subject_id)
    items = json.loads(subj["items_json"])
    used  = session.get("id_used", [])
    q     = generate_id_question(items, used)

    used.append(q["term"])
    if len(used) > len(items) // 2:
        used = used[-(len(items) // 2):]
    session["id_used"] = used

    return jsonify(q)


@app.route("/api/study/<int:subject_id>/id/answer", methods=["POST"])
@login_required
def id_answer(subject_id):
    uid     = session["user_id"]
    data    = request.json or {}
    correct = check_id(data.get("given", ""), data.get("correct", ""))

    id_ = session.get(f"id_{subject_id}", {"correct": 0, "total": 0})
    id_["total"]   += 1
    id_["correct"] += 1 if correct else 0
    session[f"id_{subject_id}"] = id_
    session.modified = True

    upsert_score(uid, subject_id, "id", id_["correct"], id_["total"])

    return jsonify({
        "correct":    correct,
        "id_correct": id_["correct"],
        "id_total":   id_["total"],
        "id_pct":     round(id_["correct"] / id_["total"] * 100),
    })


@app.route("/api/study/<int:subject_id>/id/reset", methods=["POST"])
@login_required
def id_reset(subject_id):
    session.pop(f"id_{subject_id}", None)
    session.pop("id_used", None)
    return jsonify({"ok": True})


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/decks/<int:deck_id>/export")
@login_required
def export_deck(deck_id):
    deck     = get_deck(deck_id)
    subjects = get_subjects(deck_id)

    payload  = [
        {"name": s["name"], "items": json.loads(s["items_json"])}
        for s in subjects
    ]
    html = generate_export_html(deck["name"], payload)

    safe_name = "".join(c for c in deck["name"] if c.isalnum() or c in " _-")
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_Reviewer.html"'}
    )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)