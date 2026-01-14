import os
import sqlite3
import json
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), "historia.db")


def connect_history():
    return sqlite3.connect(DB)


def init_history_db():
    conn = connect_history()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            event_type TEXT,
            locker_id INTEGER,
            before TEXT,
            after TEXT,
            performed_by TEXT,
            undone INTEGER DEFAULT 0,
            undone_at TEXT,
            undone_by TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_event(event_type: str, locker_id: int, before: dict | None, after: dict | None, performed_by: str | None = None) -> int:
    init_history_db()
    conn = connect_history()
    cur = conn.cursor()
    ts = datetime.utcnow().isoformat() + "Z"
    cur.execute("INSERT INTO history (ts, event_type, locker_id, before, after, performed_by) VALUES (?, ?, ?, ?, ?, ?)",
                (ts, event_type, locker_id, json.dumps(before or {}), json.dumps(after or {}), performed_by))
    conn.commit()
    hid = cur.lastrowid
    conn.close()
    return hid


def get_events(limit: int = 100):
    init_history_db()
    conn = connect_history()
    cur = conn.cursor()
    cur.execute("SELECT id, ts, event_type, locker_id, before, after, performed_by, undone FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    res = []
    for r in rows:
        res.append({
            "id": r[0],
            "ts": r[1],
            "event_type": r[2],
            "locker_id": r[3],
            "before": json.loads(r[4] or "{}"),
            "after": json.loads(r[5] or "{}"),
            "performed_by": r[6],
            "undone": bool(r[7])
        })
    return res


def mark_undone(event_id: int, undone_by: str | None = None):
    init_history_db()
    conn = connect_history()
    cur = conn.cursor()
    ts = datetime.utcnow().isoformat() + "Z"
    cur.execute("UPDATE history SET undone=1, undone_at=?, undone_by=? WHERE id=?", (ts, undone_by, event_id))
    conn.commit()
    conn.close()


def undo_event(event_id: int, undone_by: str | None = None) -> bool:
    """Cofa zdarzenie historii. Obsługuje: assign, release, edit, create, delete."""
    init_history_db()
    conn = connect_history()
    cur = conn.cursor()
    cur.execute("SELECT id, ts, event_type, locker_id, before, after, performed_by, undone FROM history WHERE id=?", (event_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False

    if row[7]:
        # Już cofnięte
        conn.close()
        return False

    event_type = row[2]
    locker_id = row[3]
    before = json.loads(row[4] or "{}")
    after = json.loads(row[5] or "{}")

    # Eksport nie można cofnąć
    if event_type == "export":
        conn.close()
        return False

    # Wykonanie cofnięcia
    try:
        from database import edytuj_szafke, usun_szafke, dodaj_szafke
    except Exception:
        conn.close()
        return False

    try:
        before_nonempty = bool(before and any(v is not None and v != "" for v in before.values()))
        if event_type in ("assign", "release", "edit") and before_nonempty:
            # Przywrócenie poprzedniego stanu
            edytuj_szafke(
                id_szafki=locker_id,
                miejsce=before.get('miejsce'),
                nr_szafki=before.get('nr_szafki'),
                nr_zamka=before.get('nr_zamka'),
                plec_szatni=before.get('plec_szatni'),
                kod_pracownika=before.get('kod_pracownika') or "",
                dzial=before.get('physical_dzial') or before.get('employee_dzial') or "",
                status=before.get('status') or "Wolna",
                komentarz=before.get('komentarz') or ""
            )
        elif event_type == 'create':
            # Usunięcie utworzonej szafki
            usun_szafke(locker_id)
        elif event_type == 'delete' and before_nonempty:
            # Odtworzenie usuniętej szafki
            dodaj_szafke(
                miejsce=before.get('miejsce'),
                nr_szafki=before.get('nr_szafki'),
                nr_zamka=before.get('nr_zamka'),
                plec_szatni=before.get('plec_szatni'),
                kod_pracownika=before.get('kod_pracownika') or "",
                dzial=before.get('physical_dzial') or before.get('employee_dzial') or "",
                status=before.get('status') or "Wolna",
                komentarz=before.get('komentarz') or ""
            )
        else:
            # Nieobsługiwany typ zdarzenia
            conn.close()
            return False

        # Oznaczenie jako cofnięte
        mark_undone(event_id, undone_by=undone_by)

        # Zapis nowego zdarzenia undo
        log_event("undo", locker_id, before, after, undone_by)
        conn.close()
        return True
    except Exception:
        conn.close()
        return False
