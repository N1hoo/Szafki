import sqlite3
from typing import List, Tuple

DB_NAME = "szafki.db"

def connect():
    return sqlite3.connect(DB_NAME)

def inicjuj_baze():
    """Tworzy tabelę szafek jeśli nie istnieje."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS szafki (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Miejsce TEXT,
            Nr_szafki TEXT,
            Nr_zamka TEXT,
            "Płeć_szatni" TEXT,
            Kod_pracownika TEXT,
            "Dział" TEXT,
            Status TEXT,
            Komentarz TEXT
        )
    """)
    conn.commit()
    conn.close()

def dodaj_szafke(
    miejsce, nr_szafki, nr_zamka, plec_szatni,
    kod_pracownika, dzial, status, komentarz
):
    """Dodaje nową szafkę do bazy."""
    conn = connect()
    cursor = conn.cursor()
    cur = cursor
    cur.execute("""
        INSERT INTO szafki (
            Miejsce, Nr_szafki, Nr_zamka, "Płeć_szatni",
            Kod_pracownika, "Dział", Status, Komentarz
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        miejsce, nr_szafki, nr_zamka, plec_szatni,
        kod_pracownika, dzial, status, komentarz
    ))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def edytuj_szafke(
    id_szafki, miejsce, nr_szafki, nr_zamka, plec_szatni,
    kod_pracownika, dzial, status, komentarz
):
    """Aktualizuje dane szafki."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE szafki SET
            Miejsce=?,
            Nr_szafki=?,
            Nr_zamka=?,
            "Płeć_szatni"=?,
            Kod_pracownika=?,
            "Dział"=?,
            Status=?,
            Komentarz=?
        WHERE ID=?
    """, (
        miejsce, nr_szafki, nr_zamka, plec_szatni,
        kod_pracownika, dzial, status, komentarz,
        id_szafki
    ))
    conn.commit()
    conn.close()

def usun_szafke(id_szafki):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM szafki WHERE ID=?", (id_szafki,))
    conn.commit()
    conn.close()

def pobierz_szafki() -> List[Tuple]:
    """Pobiera wszystkie szafki wraz z danymi pracowników z CSV."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT ID, Miejsce, Nr_szafki, Nr_zamka, "Płeć_szatni", Kod_pracownika, "Dział", Status, Komentarz FROM szafki')
    rows = cursor.fetchall()
    conn.close()

    # Wzbogacenie o dane z CSV
    try:
        from pracownicy import DF_PRACOWNICY
    except Exception:
        DF_PRACOWNICY = None

    result = []
    for r in rows:
        kod = (r[5] or "").strip() if r[5] is not None else ""
        dzial_db = (r[6] or "").strip() if r[6] is not None else ""
        if DF_PRACOWNICY is not None and kod and kod in DF_PRACOWNICY.index:
            p = DF_PRACOWNICY.loc[kod]
            nazw = str(p.get("Nazwisko", "") or "")
            im = str(p.get("Imię", "") or "")
            csv_dzial = str(p.get("Dział", "") or "")
            stan = str(p.get("Stanowisko", "") or "")
            plec = str(p.get("Płeć", "") or "")
            zm = str(p.get("Zmiana", "") or "")
        else:
            nazw = im = csv_dzial = stan = plec = zm = ""

        # Dział pracownika (CSV) i dział szafki (DB) rozdzielone
        employee_dzial = csv_dzial
        physical_dzial = dzial_db

        tup = (
            r[0], r[1], r[2], r[3], r[4], r[5],
            nazw, im, employee_dzial, stan, plec, zm,
            r[7], r[8], physical_dzial,
        )
        result.append(tup)
    return result

def pobierz_szafke(id_szafki):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM szafki WHERE ID=?", (id_szafki,))
    row = cursor.fetchone()
    conn.close()
    return row

def pobierz_wszystkie_miejsca() -> List[str]:
    """Pobiera unikalne miejsca szafek."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Miejsce FROM szafki WHERE Miejsce IS NOT NULL ORDER BY Miejsce")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

def pobierz_wszystkie_plci() -> List[str]:
    """Pobiera unikalne płcie szatni."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT "Płeć_szatni" FROM szafki WHERE "Płeć_szatni" IS NOT NULL ORDER BY "Płeć_szatni"')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

def pobierz_max_nr_szafki(miejsce: str, plec_szatni: str, dzial: str) -> int:
    """Pobiera maksymalny numer szafki dla danego miejsca, płci i działu."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT MAX(CAST(Nr_szafki AS INTEGER)) FROM szafki WHERE Miejsce=? AND "Płeć_szatni"=? AND "Dział"=?',
        (miejsce, plec_szatni, dzial)
    )
    row = cursor.fetchone()
    conn.close()
    max_nr = row[0] if row and row[0] else 0
    return max_nr

def dodaj_szafke_dla_miejsca(miejsce: str, nr_szafki: int, nr_zamka: int, plec_szatni: str, dzial: str, status: str = "Wolna"):
    """Dodaje szafkę dla określonego miejsca."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO szafki (
            Miejsce, Nr_szafki, Nr_zamka, "Płeć_szatni",
            Kod_pracownika, "Dział", Status, Komentarz
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        miejsce, str(nr_szafki), str(nr_zamka) if nr_zamka else None, plec_szatni,
        "", dzial, status, ""
    ))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id