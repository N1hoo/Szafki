from __future__ import annotations
from typing import List
from pracownicy import DF_PRACOWNICY
from services.lockers_service import LockersService

class EmployeesService:
    def __init__(self, lockers: LockersService):
        self.lockers = lockers

    def is_active_employee(self, kod: str) -> bool:
        kod = (kod or "").strip()
        if not kod or kod not in DF_PRACOWNICY.index:
            return False
        zw = DF_PRACOWNICY.loc[kod].get("Data_zwolnienia", "")
        zw = "" if zw is None else str(zw).strip()
        return zw == ""

    def find_new_active_without_lockers(self, rows_lockers) -> List[str]:
        assigned = self.lockers.assigned_codes(rows_lockers)
        active_codes = [kod for kod in DF_PRACOWNICY.index if self.is_active_employee(kod)]
        return sorted(set(active_codes) - assigned)