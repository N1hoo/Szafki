import pandas as pd

DF_PRACOWNICY = pd.read_csv("pracownicy.csv", sep=";", dtype=str).set_index("Kod")

def pobierz_dane_pracownika(kod_pracownika):
    if kod_pracownika in DF_PRACOWNICY.index:
        dane = DF_PRACOWNICY.loc[kod_pracownika]
        return dane.to_dict()
    return None