from flask import Flask, render_template, request, jsonify, session
import json, random, uuid, os
import sqlite3


app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('halohalo.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the table if it doesn't exist
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS subjects 
                    (id TEXT PRIMARY KEY, name TEXT, data TEXT)''')

def make_engine_state(data):
    deck = [d.copy() for d in data]
    random.shuffle(deck)
    return {
        "deck": deck,
        "index": 0,
        "mastered": 0,
        "struggling": 0,
        "good": 0,
        "ratings": [],
        "mc_total": 0, "mc_correct": 0,
        "id_total": 0, "id_correct": 0,
    }

def handle_rating(state, data, rating):
    deck = state["deck"]
    idx  = state["index"]
    if idx >= len(deck):
        return state
    card = deck.pop(idx)
    if rating <= 2:
        state["struggling"] += 1
        deck.insert(min(idx + 3, len(deck)), card)
    elif rating <= 4:
        state["good"] += 1
        mid = (idx + len(deck)) // 2
        deck.insert(max(idx, min(mid, len(deck))), card)
    else:
        state["mastered"] += 1
        deck.append(card)
    state["ratings"].append({"term": card["term"], "rating": rating})
    state["deck"] = deck
    return state

def get_distractors(data, correct_def, count=3):
    pool = [d["def"] for d in data if d["def"].lower() != correct_def.lower()]
    return random.sample(pool, min(len(pool), count))

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT id, name, data FROM subjects").fetchall()
    
    subject_list = []
    for row in rows:
        # Load the JSON string back into a Python list
        data = json.loads(row['data'])
        subject_list.append({
            "id": row['id'], 
            "name": row['name'], 
            "count": len(data)
        })
        
    return render_template("index.html", subjects=subject_list)
@app.route("/api/import", methods=["POST"])
def import_subject():
    body = request.json
    name = body.get("name", "Untitled").strip()
    raw = body.get("raw", "")
    data = []
    errors = []
    for i, line in enumerate(raw.strip().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if "\t" in line:
            parts = line.split("\t", 1)
        else:
            import re
            parts = re.split(r"  +", line, maxsplit=1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            data.append({"term": parts[0].strip(), "def": parts[1].strip()})
        else:
            errors.append(f"Line {i} skipped")
    if len(data) < 2:
        return jsonify({"error": "Need at least 2 valid items."}), 400
    sid = str(uuid.uuid4())[:8]
    data_json = json.dumps(data)
    
    with get_db_connection() as conn:
        conn.execute("INSERT INTO subjects (id, name, data) VALUES (?, ?, ?)", 
                     (sid, name, data_json))
    
    return jsonify({"id": sid, "name": name, "count": len(data)})

@app.route("/api/subjects/<sid>", methods=["DELETE"])
def delete_subject(sid):
    subjects.pop(sid, None)
    return jsonify({"ok": True})

# ── Flashcard endpoints ───────────────────────────────────────────────────────

@app.route("/api/<sid>/fc/current")
def fc_current(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    eng = s["engine"]
    deck = eng["deck"]
    idx  = eng["index"]
    total = len(s["data"])
    mastered_terms = {r["term"] for r in eng["ratings"] if r["rating"] == 5}
    if idx >= len(deck):
        return jsonify({"done": True, "mastered": len(mastered_terms), "total": total})
    card = deck[idx]
    return jsonify({
        "done": False,
        "term": card["term"],
        "def":  card["def"],
        "position": idx + 1,
        "remaining": len(deck),
        "total": total,
        "mastered": eng["mastered"],
        "struggling": eng["struggling"],
        "good": eng["good"],
        "pct": round(len(mastered_terms) / total * 100) if total else 0,
    })

@app.route("/api/<sid>/fc/rate", methods=["POST"])
def fc_rate(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    rating = request.json.get("rating", 3)
    s["engine"] = handle_rating(s["engine"], s["data"], rating)
    return fc_current(sid)

@app.route("/api/<sid>/fc/reset", methods=["POST"])
def fc_reset(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    s["engine"] = make_engine_state(s["data"])
    return fc_current(sid)

# ── Multiple Choice endpoints ─────────────────────────────────────────────────

@app.route("/api/<sid>/mc/question")
def mc_question(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    if len(s["data"]) < 4:
        return jsonify({"error": "Need at least 4 items for MC"}), 400
    item = random.choice(s["data"])
    correct = item["def"]
    distractors = get_distractors(s["data"], correct, 3)
    choices = distractors + [correct]
    random.shuffle(choices)
    eng = s["engine"]
    return jsonify({
        "term": item["term"],
        "correct": correct,
        "choices": choices,
        "mc_total": eng["mc_total"],
        "mc_correct": eng["mc_correct"],
        "mc_pct": round(eng["mc_correct"] / eng["mc_total"] * 100) if eng["mc_total"] else 0,
    })

@app.route("/api/<sid>/mc/answer", methods=["POST"])
def mc_answer(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    body = request.json
    correct = body.get("correct", "").lower().strip()
    chosen  = body.get("chosen",  "").lower().strip()
    is_correct = chosen == correct
    eng = s["engine"]
    eng["mc_total"]   += 1
    eng["mc_correct"] += 1 if is_correct else 0
    return jsonify({
        "correct": is_correct,
        "mc_total": eng["mc_total"],
        "mc_correct": eng["mc_correct"],
        "mc_pct": round(eng["mc_correct"] / eng["mc_total"] * 100),
    })

@app.route("/api/<sid>/mc/reset", methods=["POST"])
def mc_reset(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    s["engine"]["mc_total"] = s["engine"]["mc_correct"] = 0
    return jsonify({"ok": True})

# ── Identification endpoints ──────────────────────────────────────────────────

@app.route("/api/<sid>/id/question")
def id_question(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    item = random.choice(s["data"])
    eng  = s["engine"]
    return jsonify({
        "term": item["term"],
        "correct": item["def"],
        "id_total": eng["id_total"],
        "id_correct": eng["id_correct"],
        "id_pct": round(eng["id_correct"] / eng["id_total"] * 100) if eng["id_total"] else 0,
    })

@app.route("/api/<sid>/id/answer", methods=["POST"])
def id_answer(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    body = request.json
    correct = body.get("correct", "").lower().strip()
    given   = body.get("given",   "").lower().strip()
    is_correct = given == correct
    eng = s["engine"]
    eng["id_total"]   += 1
    eng["id_correct"] += 1 if is_correct else 0
    return jsonify({
        "correct": is_correct,
        "id_total": eng["id_total"],
        "id_correct": eng["id_correct"],
        "id_pct": round(eng["id_correct"] / eng["id_total"] * 100),
    })

@app.route("/api/<sid>/id/reset", methods=["POST"])
def id_reset(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    s["engine"]["id_total"] = s["engine"]["id_correct"] = 0
    return jsonify({"ok": True})

# ── Export ────────────────────────────────────────────────────────────────────

@app.route("/api/<sid>/export")
def export_subject(sid):
    s = subjects.get(sid)
    if not s: return jsonify({"error": "Not found"}), 404
    from exporter import generate_html_string
    html = generate_html_string(s["name"], s["data"])
    from flask import Response
    return Response(html, mimetype="text/html",
                    headers={"Content-Disposition":
                             f"attachment; filename={s['name']}_Reviewer.html"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)