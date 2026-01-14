from __future__ import annotations
from typing import Optional

from database import edytuj_szafke, pobierz_szafki

class AssignmentService:
    """Serwis przypisywania szafek do pracowników."""
    def _row_to_dict(self, r):
        return {
            'id': r[0], 'miejsce': r[1], 'nr_szafki': r[2], 'nr_zamka': r[3],
            'plec_szatni': r[4], 'kod_pracownika': r[5], 'nazwisko': r[6], 'imie': r[7],
            'employee_dzial': r[8], 'stanowisko': r[9], 'plec': r[10], 'zmiana': r[11],
            'status': r[12], 'komentarz': r[13], 'physical_dzial': (r[14] if len(r) > 14 else '')
        }

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

        # Zapis kodu pracownika i statusu w DB
        edytuj_szafke(
            id_szafki=target[0],
            miejsce=target[1],
            nr_szafki=target[2],
            nr_zamka=target[3],
            plec_szatni=target[4],

            kod_pracownika=(kod_pracownika or "").strip(),
            dzial=(target[14] if len(target) > 14 else ""),
            status=status,
            komentarz=(target[13] or "")
        )

        # Pobranie zaktualizowanego wiersza
        try:
            new_rows = pobierz_szafki()
            after = self._row_to_dict(next(r for r in new_rows if r and r[0] == target[0]))
            if log_event:
                log_event("assign", target[0], before, after, performed_by)
        except Exception:
            pass

        return True