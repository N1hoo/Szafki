import pandas as pd

# Pełna ścieżka do pliku Excel na serwerze
PLIK_PRACOWNIKOW = r"R:\Kadry\Analizy i kalkulacje - Paweł\Szafki\Lista osób.xlsx"

def znajdz_pracownika(kod_pracownika, sciezka_pliku=PLIK_PRACOWNIKOW):
    """
    Szuka danych pracownika w pliku Excel.
    Zwraca słownik z danymi lub None, jeśli nie znaleziono.
    """
    try:
        # Wczytanie Excela
        df = pd.read_excel(sciezka_pliku, engine='openpyxl')

        # Szukamy pracownika po kolumnie "Symbol"
        wynik = df[df['Symbol'] == int(kod_pracownika)]  # Zakładamy, że kod jest liczbą

        if not wynik.empty:
            return {
                "Nazwisko": wynik.iloc[0]["Nazwisko"],
                "Imię": wynik.iloc[0]["Imię"],
                "Dział": wynik.iloc[0]["Jedn.org.-nazwa"],
                "Stanowisko": wynik.iloc[0]["Stanowisko-nazwa"],
                "Płeć": wynik.iloc[0]["Płeć"]  # Można pominąć, jeśli nie potrzebne
            }
        else:
            return None
    except Exception as e:
        print(f"Błąd podczas odczytu pliku: {e}")
        return None
