import sqlite3

DB_NAME = "szafki.db"

# Połączenie z bazą
def connect():
    return sqlite3.connect(DB_NAME)

# 1️⃣ Dodawanie nowej szafki
def dodaj_szafke(miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO szafki (Miejsce, Nr_szafki, Nr_zamka, Płeć_Szatni, Kod_pracownika, Nazwisko, Imię, Dział, Stanowisko, Płeć, Zmiana, Status, Komentarz)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz))
    conn.commit()
    conn.close()

# 2️⃣ Pobieranie wszystkich szafek
def pobierz_szafki():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM szafki")
    rows = cursor.fetchall()
    conn.close()
    return rows

# 3️⃣ Edycja szafki
def edytuj_szafke(id, miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE szafki SET Miejsce=?, Nr_szafki=?, Nr_zamka=?, Płec_szatni=?, Kod_pracownika=?, Nazwisko=?, Imię=?, Dział=?, Stanowisko=?, Płeć=?, Zmiana=?, Status, Komentarz=?
        WHERE ID=?
    """, (miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz, id))
    conn.commit()
    conn.close()

# 4️⃣ Usuwanie szafki
def usun_szafke(id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM szafki WHERE ID=?", (id,))
    conn.commit()
    conn.close()

def znajdz_pracownika_w_db(kod):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        SELECT Nazwisko, Imię, Dział, Stanowisko, Płeć
        FROM szafki
        WHERE Kod_pracownika=?
        LIMIT 1
    """, (kod,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "Nazwisko": row[0],
            "Imię": row[1],
            "Dział": row[2],
            "Stanowisko": row[3],
            "Płeć": row[4]
        }
    else:
        return None