from PyQt6.QtWidgets import QDialog, QMessageBox
from ui_generated.ui_dodaj_pracownika import Ui_Dialog
from pracownicy import DF_PRACOWNICY


class EmployeesHandlersMixin:
    def on_przydziel_szafke_pracownikowi(self):
        # Assignment from the Pracownicy tab - redirect users to the Szafki tab
        QMessageBox.information(
            self, 
            "Przydział", 
            "Przydział szafek odbywa się teraz przez zakładkę 'Szafki'.\n"
            "Wybierz szafkę i kliknij 'Przydziel'."
        )

    def on_kod_changed(self, ui):
        kod = ui.KodPracDP.text().strip()
        if not kod or kod not in DF_PRACOWNICY.index:
            # Wyczyść pola
            if hasattr(ui, "NazwiskoDP"): ui.NazwiskoDP.setText("")
            if hasattr(ui, "ImieDP"): ui.ImieDP.setText("")
            if hasattr(ui, "DzialDP"): ui.DzialDP.setText("")
            if hasattr(ui, "StanowiskoDP"): ui.StanowiskoDP.setText("")
            if hasattr(ui, "PlecDP"): ui.PlecDP.setText("")
            if hasattr(ui, "ZmianaDP"): ui.ZmianaDP.setText("")
            # Opcjonalny label statusu
            if hasattr(ui, "parent"):
                try:
                    lbl = ui.parent().findChild(type(ui), "StatusLabel")
                except Exception:
                    lbl = None
            return

        r = DF_PRACOWNICY.loc[kod]
        if hasattr(ui, "NazwiskoDP"):
            ui.NazwiskoDP.setText(str(r.get("Nazwisko", "") or ""))
        if hasattr(ui, "ImieDP"):
            ui.ImieDP.setText(str(r.get("Imię", "") or ""))
        if hasattr(ui, "DzialDP"):
            try:
                ui.DzialDP.setText(str(r.get("Dział", "") or ""))
            except Exception:
                pass
        if hasattr(ui, "StanowiskoDP"):
            try:
                ui.StanowiskoDP.setText(str(r.get("Stanowisko", "") or ""))
            except Exception:
                pass
        if hasattr(ui, "PlecDP"):
            try:
                ui.PlecDP.setText(str(r.get("Płeć", "") or ""))
            except Exception:
                pass
        if hasattr(ui, "ZmianaDP"):
            try:
                ui.ZmianaDP.setText(str(r.get("Zmiana", "") or ""))
            except Exception:
                pass

        # Określenie statusu pracownika
        status = "Obecny"
        dz_zw = str(r.get("Data_zwolnienia", "") or "").strip()
        dz_zatr = str(r.get("Data_zatrudnienia", "") or "").strip()
        if dz_zw:
            status = "Zwolniony"
        else:
            assigned = len(self._szafki_by_kod.get(kod, []))
            last_edit = None
            try:
                from session import get_current_user
                from history import get_events
                u = get_current_user() or {}
                if u.get('login'):
                    evs = get_events(1000)
                    for ev in evs:
                        if ev.get('performed_by') == u.get('login'):
                            try:
                                ts = ev.get('ts')
                                dt = None
                                if ts:
                                    dt = __import__('datetime').datetime.fromisoformat(ts.replace('Z',''))
                                if dt and (last_edit is None or dt > last_edit):
                                    last_edit = dt
                            except Exception:
                                pass
            except Exception:
                last_edit = None

            hire_dt = None
            try:
                if dz_zatr:
                    hire_dt = __import__('datetime').datetime.strptime(dz_zatr, "%d.%m.%Y")
            except Exception:
                hire_dt = None

            if hire_dt and last_edit and assigned == 0 and hire_dt > last_edit:
                status = "Nowy"
            elif assigned > 0:
                status = "Obecny"
            else:
                status = "Obecny"

        # Aktualizacja labela statusu
        try:
            parent = ui.parent() if hasattr(ui, 'parent') else None
            if parent is not None:
                for child in parent.findChildren(type(__import__('builtins').object)):
                    pass
        except Exception:
            pass

        # Beśli jest StatusLabel w ui, ustaw jego tekst
        try:
            if hasattr(ui, 'StatusLabel'):
                ui.StatusLabel.setText(f"Status: {status}")
        except Exception:
            pass

        # Jako ostateczność, spróbuj ustawić dowolny QLabel o nazwie 'status_lbl' w rodzicu
        try:
            parent = ui.parent()
            if parent is not None:
                lbl = parent.findChild(None, "status_lbl")
                if lbl:
                    lbl.setText(f"Status: {status}")
        except Exception:
            pass