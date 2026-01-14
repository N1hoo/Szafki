import os
import pandas as pd

# Wczytanie CSV z pracownikami
_path = os.path.join(os.path.dirname(__file__), "pracownicy.csv")
DF_PRACOWNICY = pd.read_csv(_path, sep=";", dtype=str, na_filter=False)
if "Kod" in DF_PRACOWNICY.columns:
    DF_PRACOWNICY.set_index("Kod", inplace=True)
DF_PRACOWNICY.index.name = "Kod"

# Zastąpienie NaN pustymi stringami
DF_PRACOWNICY = DF_PRACOWNICY.fillna("")


def reload_from_csv(path: str | None = None):
    """Przeładowanie CSV (do dev)."""
    global DF_PRACOWNICY
    p = path or _path
    DF_PRACOWNICY = pd.read_csv(p, sep=";", dtype=str, na_filter=False)
    if "Kod" in DF_PRACOWNICY.columns:
        DF_PRACOWNICY.set_index("Kod", inplace=True)
    DF_PRACOWNICY.index.name = "Kod"
    DF_PRACOWNICY = DF_PRACOWNICY.fillna("")
    return DF_PRACOWNICY
