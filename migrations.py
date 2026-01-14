import shutil
import os
import sqlite3
from datetime import datetime
from auth import init_users_db, create_user

SZAFKI_DB = os.path.join(os.path.dirname(__file__), "szafki.db")


def backup_db(path: str):
    if not os.path.exists(path):
        return None
    bak = path + ".bak." + datetime.utcnow().strftime("%Y%m%d%H%M%S")
    shutil.copy2(path, bak)
    return bak


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info('%s')" % table)
    rows = cur.fetchall()
    for r in rows:
        if r[1] == column:
            return True
    return False


def run_migrations():
    # Kopia zapasowa
    bak = backup_db(SZAFKI_DB)
    if bak:
        print(f"Backed up {SZAFKI_DB} -> {bak}")

    conn = sqlite3.connect(SZAFKI_DB)
    cur = conn.cursor()

    # Dodanie kolumny Dział jeśli brakuje
    if not column_exists(conn, 'szafki', 'Dział'):
        print("Adding column 'Dział' to szafki.db and backfilling with 'produkcja'...")
        cur.execute("ALTER TABLE szafki ADD COLUMN 'Dział' TEXT DEFAULT 'produkcja'")
        conn.commit()
        # Wypełnienie istniejących wierszy
        cur.execute("UPDATE szafki SET 'Dział' = 'produkcja' WHERE 'Dział' IS NULL OR trim('Dział') = ''")
        conn.commit()
    else:
        print("Column 'Dział' exists in szafki.db; skipping.")

    conn.close()

    # Inicjalizacja bazy użytkowników i utworzenie admina
    init_users_db()
    created = create_user('admin', 'poznan13', first_name='Admin', last_name='', role='admin', dzial='produkcja', one_time=False)
    if created:
        print("Created admin user (login=admin)")
    else:
        print("Admin user already exists or could not be created.")

    # Inicjalizacja bazy historii
    # history.init_history_db()  # importowane leniwie gdzie potrzeba

if __name__ == '__main__':
    run_migrations()
