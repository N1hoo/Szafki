from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from history import get_events, undo_event
from session import get_current_user


class HistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(["Ts", "Locker ID", "Dział", "Miejsce", "Płeć", "Nr szafki", "Kod pracownika", "Typ ruchu", "Użytkownik", "Cofnięte", "Opis"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        row = QHBoxLayout()
        self.refresh_btn = QPushButton("Odśwież")
        self.undo_btn = QPushButton("Cofnij zaznaczone")
        row.addWidget(self.refresh_btn)
        row.addWidget(self.undo_btn)
        row.addStretch(1)
        layout.addLayout(row)

        self.refresh_btn.clicked.connect(self.reload)
        self.undo_btn.clicked.connect(self.on_undo)

        self.reload()

    def reload(self):
        try:
            events = get_events(200)
        except Exception:
            events = []
        self.table.setRowCount(len(events))
        self._events_cache = events  # cache dla undo
        for i, e in enumerate(events):
            # Dane przed/po dla szczegółów
            before = e.get('before', {}) or {}
            after = e.get('after', {}) or {}
            data = after if after else before
            
            locker_id = str(e.get('locker_id', '') or '')
            dzial = str(data.get('physical_dzial') or data.get('employee_dzial') or '')
            miejsce = str(data.get('miejsce') or '')
            plec = str(data.get('plec_szatni') or '')
            nr_sz = str(data.get('nr_szafki') or '')
            kod_prac = str(data.get('kod_pracownika') or '')
            typ = str(e.get('event_type') or '')
            performed_by = str(e.get('performed_by') or '')
            cofniete = "Tak" if e.get('undone') else "Nie"
            
            # Kolumna opisu - szczególnie przydatna dla eksportów
            opis = ""
            if typ == "export":
                export_type = str(data.get('export_type') or '')
                filename = str(data.get('filename') or '')
                if export_type and filename:
                    # Format na podstawie rozszerzenia
                    fmt = "CSV" if filename.lower().endswith('.csv') else "Excel" if filename.lower().endswith('.xlsx') else ""
                    # Wyświetlany typ eksportu
                    display_type = export_type.capitalize() if export_type else ""
                    opis = f"{display_type} - {fmt}" if fmt else display_type
            
            self.table.setItem(i, 0, QTableWidgetItem(str(e.get('ts', '') or '')))
            self.table.setItem(i, 1, QTableWidgetItem(locker_id))
            self.table.setItem(i, 2, QTableWidgetItem(dzial))
            self.table.setItem(i, 3, QTableWidgetItem(miejsce))
            self.table.setItem(i, 4, QTableWidgetItem(plec))
            self.table.setItem(i, 5, QTableWidgetItem(nr_sz))
            self.table.setItem(i, 6, QTableWidgetItem(kod_prac))
            self.table.setItem(i, 7, QTableWidgetItem(typ))
            self.table.setItem(i, 8, QTableWidgetItem(performed_by))
            self.table.setItem(i, 9, QTableWidgetItem(cofniete))
            self.table.setItem(i, 10, QTableWidgetItem(opis))

    def _selected_event_id(self) -> int | None:
        r = self.table.currentRow()
        if r < 0:
            return None
        it = self.table.item(r, 0)
        if not it:
            return None
        # Pierwsza kolumna to Ts, ID pobieramy z cache
        try:
            events = getattr(self, '_events_cache', None)
            if events is None:
                events = get_events(200)
            return events[r]['id']
        except Exception:
            return None

    def on_undo(self):
        eid = self._selected_event_id()
        if not eid:
            QMessageBox.warning(self, "Brak zaznaczenia", "Wybierz wydarzenie.")
            return
        u = get_current_user() or {}
        if u.get('role') != 'admin':
            QMessageBox.warning(self, "Brak uprawnień", "Tylko administrator może cofać zdarzenia.")
            return

        ok = undo_event(eid, undone_by=u.get('login'))
        if not ok:
            QMessageBox.warning(self, "Błąd", "Cofnięcie nie powiodło się (być może zdarzenie już jest cofnięte lub nieobsługiwane)")
            return
        QMessageBox.information(self, "Sukces", "Zdarzenie cofnięte")
        self.reload()
        
        # Odświeżenie tabel w głównym oknie
        try:
            main_window = self.parent_window
            while main_window and not hasattr(main_window, 'reload_all'):
                main_window = getattr(main_window, 'parent', None)
            if main_window and hasattr(main_window, 'reload_all'):
                main_window.reload_all()
        except Exception:
            pass