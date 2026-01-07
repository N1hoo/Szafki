from __future__ import annotations
from typing import Optional

from database import edytuj_szafke, pobierz_szafki

class AssignmentService:
    """
    Minimalna wersja:
    - bierze locker_id i dane pracownika
    - zapisuje je do szafki w DB
    """
    def assign_locker_to_employee(
        self,
        locker_id: int,
        *,
        kod_pracownika: str,
        nazwisko: str,
        imie: str,
        dzial: str,
        stanowisko: str,
        plec: str,
        zmiana: str = "",
        status: str = "Zajęta",
    ) -> bool:
        rows = pobierz_szafki()
        target = next((r for r in rows if r and len(r) >= 14 and r[0] == locker_id), None)
        if target is None:
            return False

        # target = (id, miejsce, nr_szafki, nr_zamka, plec_szatni, kod, nazw, im, dzial, stan, plec, zm, status, komentarz)
        edytuj_szafke(
            id_szafki=target[0],
            miejsce=target[1],
            nr_szafki=target[2],
            nr_zamka=target[3],
            plec_szatni=target[4],

            kod_pracownika=(kod_pracownika or "").strip(),
            nazwisko=(nazwisko or "").strip(),
            imie=(imie or "").strip(),
            dzial=(dzial or "").strip(),
            stanowisko=(stanowisko or "").strip(),
            plec=(plec or "").strip(),
            zmiana=(zmiana or "").strip(),

            status=status,
            komentarz=(target[13] or "")
        )
        return True