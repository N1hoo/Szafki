import sqlite3

DB_NAME = "szafki.db"

# Połączenie z bazą
def connect():
    return sqlite3.connect(DB_NAME)

# 1️⃣ Dodawanie nowej szafki
def dodaj_szafke(miejsce, typ, nr_szafki, nr_zamka, plec, segment, kod_pracownika, nazwisko, imie, dzial, stanowisko, zmiana, komentarz):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO szafki (Miejsce, Typ, Nr_szafki, Nr_zamka, Płeć, Segment, Kod_pracownika, Nazwisko, Imię, Dział, Stanowisko, Zmiana, Komentarz)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (miejsce, typ, nr_szafki, nr_zamka, plec, segment, kod_pracownika, nazwisko, imie, dzial, stanowisko, zmiana, komentarz))
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
def edytuj_szafke(id, miejsce, typ, nr_szafki, nr_zamka, plec, segment, kod_pracownika, nazwisko, imie, dzial, stanowisko, zmiana, komentarz):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE szafki SET Miejsce=?, Typ=?, Nr_szafki=?, Nr_zamka=?, Płeć=?, Segment=?, Kod_pracownika=?, Nazwisko=?, Imię=?, Dział=?, Stanowisko=?, Zmiana=?, Komentarz=?
        WHERE ID=?
    """, (miejsce, typ, nr_szafki, nr_zamka, plec, segment, kod_pracownika, nazwisko, imie, dzial, stanowisko, zmiana, komentarz, id))
    conn.commit()
    conn.close()

# 4️⃣ Usuwanie szafki
def usun_szafke(id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM szafki WHERE ID=?", (id,))
    conn.commit()
    conn.close()