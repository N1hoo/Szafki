import sqlite3

DB_NAME = "szafki.db"

def connect():
    return sqlite3.connect(DB_NAME)

def inicjuj_baze():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS szafki (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Miejsce TEXT,
            Nr_szafki INTEGER,
            Nr_zamka INTEGER,
            Plec_szatni TEXT,
            Kod_pracownika TEXT,
            Nazwisko TEXT,
            Imię TEXT,
            Dział TEXT,
            Stanowisko TEXT,
            Płeć TEXT,
            Zmiana TEXT,
            Status TEXT,
            Komentarz TEXT,
            Data_zatrudnienia TEXT,
            Data_zwolnienia TEXT
        )
    """)
    conn.commit()
    conn.close()

def dodaj_szafke(miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz, data_zatrudnienia, data_zwolnienia):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO szafki VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz, data_zatrudnienia, data_zwolnienia))
    conn.commit()
    conn.close()

def edytuj_szafke(id_szafki, miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz, data_zatrudnienia, data_zwolnienia):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE szafki SET
        Miejsce=?, Nr_szafki=?, Nr_zamka=?, Plec_szatni=?, Kod_pracownika=?,
        Nazwisko=?, Imię=?, Dział=?, Stanowisko=?, Płeć=?, Zmiana=?,
        Status=?, Komentarz=?, Data_zatrudnienia=?, Data_zwolnienia=?
        WHERE ID=?
    """, (miejsce, nr_szafki, nr_zamka, plec_szatni, kod_pracownika, nazwisko, imie, dzial, stanowisko, plec, zmiana, status, komentarz, data_zatrudnienia, data_zwolnienia, id_szafki))
    conn.commit()
    conn.close()

def usun_szafke(id_szafki):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM szafki WHERE ID=?", (id_szafki,))
    conn.commit()
    conn.close()

def pobierz_szafki():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM szafki")
    rows = cursor.fetchall()
    conn.close()
    return rows

def pobierz_szafke(id_szafki):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM szafki WHERE ID=?", (id_szafki,))
    row = cursor.fetchone()
    conn.close()
    return row