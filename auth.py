import os
import sqlite3
import secrets
from typing import Optional

DB = os.path.join(os.path.dirname(__file__), "users.db")

# Próba użycia argon2, w razie błędu fallback na PBKDF2
try:
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    _hasher_type = "argon2"
except Exception:
    import hashlib
    import base64
    _hasher_type = "pbkdf2"


def connect_users():
    return sqlite3.connect(DB)


def init_users_db():
    conn = connect_users()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            login TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            role TEXT NOT NULL,
            dzial TEXT,
            one_time INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    if _hasher_type == "argon2":
        return ph.hash(password)
    # pbkdf2 fallback
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return "pbkdf2$" + base64.b64encode(salt + dk).decode()


def verify_password(stored: str, password: str) -> bool:
    if _hasher_type == "argon2":
        try:
            return ph.verify(stored, password)
        except Exception:
            return False
    if stored.startswith("pbkdf2$"):
        import base64
        raw = base64.b64decode(stored.split("$", 1)[1].encode())
        salt = raw[:16]
        dk = raw[16:]
        import hashlib
        test = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return secrets.compare_digest(test, dk)
    return False


def validate_password(password: str) -> tuple[bool, str]:
    """Walidacja hasła: min 6 znaków, 1 cyfra, 1 litera."""
    if len(password) < 6:
        return False, "Hasło musi mieć co najmniej 6 znaków"
    if not any(c.isdigit() for c in password):
        return False, "Hasło musi zawierać co najmniej jedną cyfrę"
    if not any(c.isalpha() for c in password):
        return False, "Hasło musi zawierać co najmniej jedną literę"
    return True, ""


def create_user(login: str, password: str, *, first_name: str = "", last_name: str = "", role: str = "user", dzial: str = "produkcja", one_time: bool = False) -> bool:
    # Pomijamy walidację dla haseł jednorazowych
    if not one_time:
        valid, _ = validate_password(password)
        if not valid:
            return False
    init_users_db()
    conn = connect_users()
    cur = conn.cursor()
    pw = hash_password(password)
    try:
        cur.execute("INSERT INTO users (login, password_hash, first_name, last_name, role, dzial, one_time) VALUES (?, ?, ?, ?, ?, ?, ?)", (login, pw, first_name, last_name, role, dzial, 1 if one_time else 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(login: str) -> Optional[dict]:
    init_users_db()
    conn = connect_users()
    cur = conn.cursor()
    cur.execute("SELECT login, password_hash, first_name, last_name, role, dzial, one_time FROM users WHERE login=?", (login,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "login": r[0],
        "password_hash": r[1],
        "first_name": r[2],
        "last_name": r[3],
        "role": r[4],
        "dzial": r[5],
        "one_time": bool(r[6])
    }


def list_users() -> list[dict]:
    """Zwraca listę wszystkich użytkowników."""
    init_users_db()
    conn = connect_users()
    cur = conn.cursor()
    cur.execute("SELECT login, first_name, last_name, role, dzial, one_time FROM users ORDER BY login")
    rows = cur.fetchall()
    conn.close()
    res = []
    for r in rows:
        res.append({
            "login": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "role": r[3],
            "dzial": r[4],
            "one_time": bool(r[5])
        })
    return res


def update_user(login: str, *, first_name: str = None, last_name: str = None, role: str = None, dzial: str = None) -> bool:
    """Aktualizuje dane użytkownika (bez hasła)."""
    init_users_db()
    conn = connect_users()
    cur = conn.cursor()
    cur.execute("SELECT login FROM users WHERE login=?", (login,))
    if not cur.fetchone():
        conn.close()
        return False
    # Dynamiczne budowanie UPDATE
    fields = []
    params = []
    if first_name is not None:
        fields.append("first_name=?")
        params.append(first_name)
    if last_name is not None:
        fields.append("last_name=?")
        params.append(last_name)
    if role is not None:
        fields.append("role=?")
        params.append(role)
    if dzial is not None:
        fields.append("dzial=?")
        params.append(dzial)
    if not fields:
        conn.close()
        return True
    params.append(login)
    cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE login=?", tuple(params))
    conn.commit()
    conn.close()
    return True


def set_one_time_password(login: str, password: str | None = None) -> Optional[str]:
    """Ustawia hasło jednorazowe. Generuje losowe jeśli nie podano."""
    u = get_user(login)
    if not u:
        return None
    # Generowanie losowego hasła jeśli brak
    if password is None:
        password = secrets.token_urlsafe(8)
    # Walidacja podanego hasła
    else:
        valid, _ = validate_password(password)
        if not valid:
            return None  # Nieprawidłowe hasło
    phash = hash_password(password)
    conn = connect_users()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash=?, one_time=1 WHERE login=?", (phash, login))
    conn.commit()
    conn.close()
    return password


def change_password(login: str, new_password: str) -> bool:
    # Walidacja nowego hasła
    valid, _ = validate_password(new_password)
    if not valid:
        return False
    u = get_user(login)
    if not u:
        return False
    phash = hash_password(new_password)
    conn = connect_users()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash=?, one_time=0 WHERE login=?", (phash, login))
    conn.commit()
    conn.close()
    return True