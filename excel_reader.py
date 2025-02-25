import msoffcrypto
import pandas as pd
import io

sciezka_pliku = r"R:\Kadry\Analizy i kalkulacje - Paweł\Szafki\pracownicy.xlsx"
haslo = "poznan13"


def znajdz_pracownika(kod_pracownika, sciezka_pliku, haslo):
    """
    Szuka danych pracownika w pliku Excel zabezpieczonym hasłem.
    """
    try:
        # Otwieramy zaszyfrowany plik
        with open(sciezka_pliku, "rb") as f:
            file = msoffcrypto.OfficeFile(f)
            file.load_key(password=haslo)

            # Odszyfrowujemy plik do pamięci
            decrypted = io.BytesIO()
            file.decrypt(decrypted)

            # Wczytujemy plik do pandas
            df = pd.read_excel(decrypted, engine='openpyxl')

        # Szukamy pracownika po "Symbol"
        wynik = df[df['Symbol'] == int(kod_pracownika)]

        if not wynik.empty:
            return {
                "Nazwisko": wynik.iloc[0]["Nazwisko"],
                "Imię": wynik.iloc[0]["Imię"],
                "Dział": wynik.iloc[0]["Jedn.org.-nazwa"],
                "Stanowisko": wynik.iloc[0]["Stanowisko-nazwa"],
                "Płeć": wynik.iloc[0]["Płeć"]
            }
        else:
            return None
    except Exception as e:
        print(f"Błąd podczas odczytu pliku: {e}")
        return None
