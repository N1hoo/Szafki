from __future__ import annotations
from typing import Dict, List, Any, Tuple, Optional

from database import pobierz_szafki, edytuj_szafke

LockerRow = Tuple[Any, ...]  # (id, miejsce, nr_szafki, nr_zamka, plec_szatni, kod, nazw, im, dzial, stan, plec, zm, status, komentarz)


class LockersService:
    def _row_to_dict(self, r: LockerRow) -> dict:
        return {
            'id': r[0], 'miejsce': r[1], 'nr_szafki': r[2], 'nr_zamka': r[3],
            'plec_szatni': r[4], 'kod_pracownika': r[5], 'nazwisko': r[6], 'imie': r[7],
            'employee_dzial': r[8], 'stanowisko': r[9], 'plec': r[10], 'zmiana': r[11],
            'status': r[12], 'komentarz': r[13], 'physical_dzial': (r[14] if len(r) > 14 else '')
        }

    def get_all(self, current_user: dict | None = None) -> List[LockerRow]:
        """Zwraca szafki; dla zwykłych użytkowników tylko z ich działu."""
        rows = pobierz_szafki()
        if current_user and current_user.get('role') != 'admin':
            # Zwykli użytkownicy widzą tylko szafki ze swojego działu
            allowed = (current_user.get('dzial') or '').strip()
            if not allowed:
                return []
            def physical(r):
                return str((r[14] if len(r) > 14 else r[8] or '') or '').strip()
            return [r for r in rows if r and len(r) >= 9 and physical(r) == allowed]
        return rows

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

    def add_locker(self, *, miejsce, nr_szafki=None, nr_zamka=None, plec_szatni=None, kod_pracownika="", dzial="", status="Wolna", komentarz="") -> int | None:
        """Dodaje szafkę i loguje do historii."""
        try:
            from history import log_event
            from session import get_current_user
            performed_by = (get_current_user() or {}).get('login')
        except Exception:
            log_event = None
            performed_by = None

        # Wstawienie do bazy
        try:
            from database import dodaj_szafke
            new_id = dodaj_szafke(
                miejsce=miejsce,
                nr_szafki=nr_szafki,
                nr_zamka=nr_zamka,
                plec_szatni=plec_szatni,
                kod_pracownika=kod_pracownika,
                dzial=dzial,
                status=status,
                komentarz=komentarz
            )
        except Exception:
            return None

        # Pobranie nowo dodanego wiersza
        try:
            new_rows = pobierz_szafki()
            new_row = next(r for r in new_rows if r and r[0] == new_id)
            if log_event:
                log_event("create", new_id, None, self._row_to_dict(new_row), performed_by)
        except Exception:
            pass

        return new_id

    def release_locker_by_id(self, locker_id: int, rows: Optional[List[LockerRow]] = None, current_user: dict | None = None) -> bool:
        rows = rows if rows is not None else self.get_all(current_user=current_user)

        target = None
        for r in rows:
            if r and len(r) >= 14 and r[0] == locker_id:
                target = r
                break
        if target is None:
            return False

        # Uprawnienia: tylko admin lub właściwy dział
        if current_user and current_user.get('role') != 'admin':
            allowed = (current_user.get('dzial') or '').strip()
            physical = str((target[14] if len(target) > 14 else target[8] or '') or '').strip()
            if physical != allowed:
                return False

        # Log przed zmianą
        try:
            from history import log_event
            from session import get_current_user
            performed_by = (get_current_user() or {}).get('login')
            before = self._row_to_dict(target)
        except Exception:
            log_event = None
            performed_by = None
            before = None

        # Zwolnienie szafki
        db_dzial = target[14] if len(target) > 14 else (target[8] or '')
        edytuj_szafke(
            id_szafki=target[0],
            miejsce=target[1],
            nr_szafki=target[2],
            nr_zamka=target[3],
            plec_szatni=target[4],
            kod_pracownika="",
            dzial=db_dzial,
            status="Wolna",
            komentarz=(target[13] or "")
        )

        # Pobranie zaktualizowanego wiersza
        try:
            new_rows = pobierz_szafki()
            after = self._row_to_dict(next(r for r in new_rows if r and r[0] == target[0]))
            if log_event:
                log_event("release", target[0], before, after, performed_by)
        except Exception:
            pass

        return True

    def release_all_for_employee(self, kod: str, rows: List[LockerRow] | None = None, current_user: dict | None = None) -> int:
        """Zwalnia wszystkie szafki pracownika. Zwraca liczbę zwolnionych."""
        rows = rows if rows is not None else self.get_all(current_user=current_user)
        count = 0
        for r in rows:
            if not r or len(r) < 14:
                continue
            locker_kod = str(r[5] or "").strip()
            if locker_kod == kod:
                if self.release_locker_by_id(r[0], rows=rows, current_user=current_user):
                    count += 1
        return count

    def edit_locker(self, *, id_szafki, miejsce, nr_szafki=None, nr_zamka=None, plec_szatni=None, kod_pracownika="", dzial="", status="Wolna", komentarz="") -> bool:
        """Edytuje szafkę i loguje zmianę."""
        rows = pobierz_szafki()
        target = next((r for r in rows if r and r[0] == id_szafki), None)
        if target is None:
            return False

        try:
            from history import log_event
            from session import get_current_user
            performed_by = (get_current_user() or {}).get('login')
            before = self._row_to_dict(target)
        except Exception:
            log_event = None
            performed_by = None
            before = None

        from database import edytuj_szafke
        edytuj_szafke(
            id_szafki=id_szafki,
            miejsce=miejsce,
            nr_szafki=nr_szafki,
            nr_zamka=nr_zamka,
            plec_szatni=plec_szatni,
            kod_pracownika=kod_pracownika,
            dzial=dzial,
            status=status,
            komentarz=komentarz,
        )

        try:
            new_rows = pobierz_szafki()
            after = self._row_to_dict(next(r for r in new_rows if r and r[0] == id_szafki))
            if log_event:
                log_event("edit", id_szafki, before, after, performed_by)
        except Exception:
            pass

        return True