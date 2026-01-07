from __future__ import annotations
from typing import Dict, List, Any, Tuple, Optional

from database import pobierz_szafki, edytuj_szafke

LockerRow = Tuple[Any, ...]  # (id, miejsce, nr_szafki, nr_zamka, plec_szatni, kod, nazw, im, dzial, stan, plec, zm, status, komentarz)

class LockersService:
    def get_all(self) -> List[LockerRow]:
        return pobierz_szafki()

    def map_by_employee_code(self, rows: List[LockerRow]) -> Dict[str, List[dict]]:
        m: Dict[str, List[dict]] = {}
        for r in rows:
            if not r or len(r) < 14:
                continue
            kod = str(r[5] or "").strip()
            status = str(r[12] or "").strip()
            if not kod or status == "Wolna":
                continue

            m.setdefault(kod, []).append({
                "id": r[0],
                "miejsce": str(r[1] or "").strip(),
                "nr_szafki": str(r[2] or "").strip(),
                "nr_zamka": str(r[3] or "").strip(),
                "plec_szatni": str(r[4] or "").strip(),
                "status": status,
                "komentarz": str(r[13] or "").strip(),
            })
        return m

    def assigned_codes(self, rows: List[LockerRow]) -> set[str]:
        codes = set()
        for r in rows:
            if not r or len(r) < 14:
                continue
            kod = str(r[5] or "").strip()
            status = str(r[12] or "").strip()
            if kod and status != "Wolna":
                codes.add(kod)
        return codes

    def release_locker_by_id(self, locker_id: int, rows: Optional[List[LockerRow]] = None) -> bool:
        rows = rows if rows is not None else self.get_all()

        target = None
        for r in rows:
            if r and len(r) >= 14 and r[0] == locker_id:
                target = r
                break
        if target is None:
            return False

        edytuj_szafke(
            id_szafki=target[0],
            miejsce=target[1],
            nr_szafki=target[2],
            nr_zamka=target[3],
            plec_szatni=target[4],
            kod_pracownika="",
            nazwisko="",
            imie="",
            dzial="",
            stanowisko="",
            plec="",
            zmiana="",
            status="Wolna",
            komentarz=(target[13] or "")
        )
        return True

    def release_all_for_employee(self, kod: str, rows: Optional[List[LockerRow]] = None) -> int:
        rows = rows if rows is not None else self.get_all()
        released = 0
        for r in rows:
            if not r or len(r) < 14:
                continue
            r_kod = str(r[5] or "").strip()
            status = str(r[12] or "").strip()
            if r_kod == kod and status != "Wolna":
                ok = self.release_locker_by_id(int(r[0]), rows=rows)
                if ok:
                    released += 1
        return released