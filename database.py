"""
database.py
-----------
SQLite schema + helper functions for Halo-Halo.

Tables:
  users       – accounts (username + 4-digit PIN hash)
  decks       – top-level containers owned by a user
  subjects    – belong to a deck, hold flashcard data
  progress    – per-user, per-subject flashcard ratings
  scores      – per-user, per-subject MC / ID score history
"""

import sqlite3
import hashlib
import os

# ── Path ──────────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "haohalo.db")


def get_db():
    """Return a new database connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── Schema ────────────────────────────────────────────────────────────────────
def init_db():
    """Create all tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
        -- Users ---------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            pin_hash    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        -- Decks ---------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS decks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name        TEXT    NOT NULL,
            emoji       TEXT    DEFAULT '📚',
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        -- Subjects ------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS subjects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id     INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
            name        TEXT    NOT NULL,
            items_json  TEXT    NOT NULL DEFAULT '[]',
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        -- Flashcard progress (per user + subject) -----------------------------
        CREATE TABLE IF NOT EXISTS progress (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id  INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            term        TEXT    NOT NULL,
            rating      INTEGER NOT NULL DEFAULT 0,
            seen_count  INTEGER NOT NULL DEFAULT 0,
            updated_at  TEXT    DEFAULT (datetime('now')),
            UNIQUE(user_id, subject_id, term)
        );

        -- MC / ID score snapshots ---------------------------------------------
        CREATE TABLE IF NOT EXISTS scores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id  INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            mode        TEXT    NOT NULL CHECK(mode IN ('mc','id')),
            correct     INTEGER NOT NULL DEFAULT 0,
            total       INTEGER NOT NULL DEFAULT 0,
            updated_at  TEXT    DEFAULT (datetime('now')),
            UNIQUE(user_id, subject_id, mode)
        );
        """)


# ── Auth helpers ──────────────────────────────────────────────────────────────
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def register_user(username: str, pin: str):
    """Create a new user. Returns (user_row, error_str)."""
    if not username or not pin.isdigit() or len(pin) != 4:
        return None, "Username and a 4-digit PIN are required."
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, pin_hash) VALUES (?, ?)",
                (username.strip(), hash_pin(pin))
            )
            conn.commit()
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username.strip(),)
            ).fetchone()
            return dict(user), None
        except sqlite3.IntegrityError:
            return None, "Username already taken."


def login_user(username: str, pin: str):
    """Return user dict if credentials match, else None."""
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND pin_hash = ?",
            (username.strip(), hash_pin(pin))
        ).fetchone()
        return dict(user) if user else None


# ── Deck helpers ──────────────────────────────────────────────────────────────
def get_decks(user_id: int):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM decks WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def create_deck(user_id: int, name: str, emoji: str = "📚"):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO decks (user_id, name, emoji) VALUES (?, ?, ?)",
            (user_id, name.strip(), emoji)
        )
        conn.commit()
        return cur.lastrowid


def update_deck(deck_id: int, name: str, emoji: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE decks SET name=?, emoji=? WHERE id=?",
            (name.strip(), emoji, deck_id)
        )
        conn.commit()


def delete_deck(deck_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM decks WHERE id=?", (deck_id,))
        conn.commit()


def get_deck(deck_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM decks WHERE id=?", (deck_id,)).fetchone()
        return dict(row) if row else None


# ── Subject helpers ───────────────────────────────────────────────────────────
def get_subjects(deck_id: int):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM subjects WHERE deck_id = ? ORDER BY created_at",
            (deck_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_subject(subject_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM subjects WHERE id=?", (subject_id,)
        ).fetchone()
        return dict(row) if row else None


def create_subject(deck_id: int, name: str, items: list):
    import json
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO subjects (deck_id, name, items_json) VALUES (?, ?, ?)",
            (deck_id, name.strip(), json.dumps(items))
        )
        conn.commit()
        return cur.lastrowid


def update_subject(subject_id: int, name: str, items: list):
    import json
    with get_db() as conn:
        conn.execute(
            "UPDATE subjects SET name=?, items_json=? WHERE id=?",
            (name.strip(), json.dumps(items), subject_id)
        )
        conn.commit()


def delete_subject(subject_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
        conn.commit()


# ── Progress helpers ──────────────────────────────────────────────────────────
def get_progress(user_id: int, subject_id: int):
    """Return dict of term -> {rating, seen_count}."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT term, rating, seen_count FROM progress WHERE user_id=? AND subject_id=?",
            (user_id, subject_id)
        ).fetchall()
        return {r["term"]: {"rating": r["rating"], "seen": r["seen_count"]} for r in rows}


def upsert_progress(user_id: int, subject_id: int, term: str, rating: int):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO progress (user_id, subject_id, term, rating, seen_count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(user_id, subject_id, term)
            DO UPDATE SET
                rating     = excluded.rating,
                seen_count = seen_count + 1,
                updated_at = datetime('now')
        """, (user_id, subject_id, term, rating))
        conn.commit()


def get_subject_mastery(user_id: int, subject_id: int, total_items: int):
    """Return 0-100 mastery % (cards rated >=4 / total)."""
    if total_items == 0:
        return 0
    with get_db() as conn:
        row = conn.execute("""
            SELECT COUNT(*) as cnt FROM progress
            WHERE user_id=? AND subject_id=? AND rating >= 4
        """, (user_id, subject_id)).fetchone()
        return round(row["cnt"] / total_items * 100)


# ── Score helpers ─────────────────────────────────────────────────────────────
def get_score(user_id: int, subject_id: int, mode: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT correct, total FROM scores WHERE user_id=? AND subject_id=? AND mode=?",
            (user_id, subject_id, mode)
        ).fetchone()
        if not row:
            return {"correct": 0, "total": 0, "pct": 0}
        pct = round(row["correct"] / row["total"] * 100) if row["total"] else 0
        return {"correct": row["correct"], "total": row["total"], "pct": pct}


def upsert_score(user_id: int, subject_id: int, mode: str, correct: int, total: int):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO scores (user_id, subject_id, mode, correct, total)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, subject_id, mode)
            DO UPDATE SET
                correct    = excluded.correct,
                total      = excluded.total,
                updated_at = datetime('now')
        """, (user_id, subject_id, mode, correct, total))
        conn.commit()