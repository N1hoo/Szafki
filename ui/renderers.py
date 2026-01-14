from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

LOCKERS_HEADERS = [
    "ID", "Miejsce", "Nr szafki", "Nr zamka", "Płeć szatni", "Kod prac.", "Nazwisko",
    "Imię", "Dział", "Stanowisko", "Płeć", "Zmiana", "Status", "Komentarz"
]

EMP_HEADERS = [
    "Kod","Nazwisko","Imię","Płeć","Dział","Stanowisko","Data zatr.","Data zwol.","Szafki"
]

from datetime import datetime


def parse_date(s: str):
    """Parsuje datę z różnych formatów."""
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    # last resort: try pandas if available
    try:
        import pandas as pd
        dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if pd.isna(dt):
            return None
        return dt.date()
    except Exception:
        return None


from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

class SortableItem(QTableWidgetItem):
    """Element tabeli z własnym kluczem sortowania."""
    def __init__(self, text: str = "", sort_key = None):
        super().__init__(text)
        self._sort_key = sort_key

    def __lt__(self, other):
        # Porównanie preferujące sort_key
        try:
            a = getattr(self, '_sort_key', None)
            b = getattr(other, '_sort_key', None)
            if a is not None and b is not None:
                return a < b
            if a is None and b is not None:
                # Brak klucza = na koniec listy
                return False
            if a is not None and b is None:
                return True
        except Exception:
            pass
        # Fallback na domyślne porównanie
        try:
            return super().__lt__(other)
        except Exception:
            return False

def render_lockers_table(table: QtWidgets.QTableWidget, rows: list[tuple], *, filter_callback=None, filter_values: dict | None = None, current_user: dict | None = None, employees_data: dict | None = None):
    """Renderuje tabelę szafek z filtrowaniem kolumn."""
    table.setSortingEnabled(False)

    # Dodatkowa kolumna dla admina
    is_admin = bool(current_user and current_user.get('role') == 'admin')
    ncols = 14 + (1 if is_admin else 0)

    headers = LOCKERS_HEADERS.copy()
    if is_admin:
        headers.append("Dział szafki")

    table.setColumnCount(ncols)
    table.setHorizontalHeaderLabels(headers)

    fv = filter_values or {}

    # Filtry w osobnej tabeli nad główną
    if hasattr(table, "filter_table") and table.filter_table is not None:
        ft = table.filter_table
        ft.setColumnCount(ncols)
        ft.setRowCount(1)
        ft.verticalHeader().setVisible(False)
        ft.horizontalHeader().setVisible(False)

        # Użycie istniejących lub tworzenie nowych QLineEdit
        from functools import partial
        from PyQt6.QtCore import QSignalBlocker
        for j in range(ncols):
            w = ft.cellWidget(0, j)
            if w is None or not isinstance(w, QtWidgets.QLineEdit):
                le = QtWidgets.QLineEdit()
                if callable(filter_callback):
                    le.textChanged.connect(partial(filter_callback, j))
                ft.setCellWidget(0, j, le)
                w = le
            # Update text without emitting
            with QSignalBlocker(w):
                w.setText(str(fv.get(j, "")))

        # Wiersze danych w głównej tabeli
        expected = len(rows)
        while table.rowCount() > expected:
            table.removeRow(table.rowCount() - 1)
        while table.rowCount() < expected:
            table.insertRow(table.rowCount())

        for i, r in enumerate(rows):
            row_idx = i
            
            # Sprawdzenie czy pracownik został zwolniony
            kod_prac = str(r[5] or '').strip() if len(r) > 5 else ''
            is_dismissed = False
            data_zwol = ""
            
            if kod_prac:
                # Próba pobrania z employees_data
                if employees_data and kod_prac in employees_data:
                    data_zwol = str(employees_data[kod_prac].get('Data_zwolnienia', '')).strip()
                    is_dismissed = bool(data_zwol)
                else:
                    # Fallback na DF_PRACOWNICY
                    try:
                        from pracownicy import DF_PRACOWNICY
                        emp = DF_PRACOWNICY[DF_PRACOWNICY['Kod'] == kod_prac]
                        if not emp.empty:
                            data_zwol = str(emp.iloc[0]['Data_zwolnienia'] if 'Data_zwolnienia' in emp.columns else '').strip()
                            is_dismissed = bool(data_zwol)
                    except Exception:
                        pass
            
            for j in range(ncols):
                val = r[j] if j < len(r) else ""
                item = QtWidgets.QTableWidgetItem("" if val is None else str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                # Color dismissed employees in red and bold
                if is_dismissed:
                    from PyQt6 import QtGui
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QtGui.QColor("red"))
                    # Tooltip z datą zwolnienia
                    if data_zwol:
                        item.setToolTip(f"Pracownik zakończył współpracę dnia: {data_zwol}")
                
                table.setItem(row_idx, j, item)

        # Auto-dopasowanie szerokości kolumn przy pierwszym wyświetleniu
        try:
            if not getattr(table, '_autosized', False):
                from PyQt6.QtCore import QTimer
                def _do_autosize():
                    try:
                        from PyQt6.QtWidgets import QHeaderView
                        header = table.horizontalHeader()
                        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                        table.resizeColumnsToContents()
                        # capture widths and lock them as fixed so they don't auto-resize later
                        widths = [table.columnWidth(i) for i in range(table.columnCount())]
                        for idx, w in enumerate(widths):
                            # Tryb interaktywny po autosizing
                            header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)
                            table.setColumnWidth(idx, w)
                        table._autosized = True
                    except Exception:
                        pass
                if table.isVisible():
                    _do_autosize()
                else:
                    QTimer.singleShot(0, _do_autosize)
        except Exception:
            pass

        for i in range(ncols):
            try:
                ft.setColumnWidth(i, table.columnWidth(i))
            except Exception:
                pass

        ft.setColumnHidden(0, True)
        table.setColumnHidden(0, True)
        table.setSortingEnabled(True)
        return

    # --- Fallback: pojedyncza tabela (legacy) ---
    # Keep header/column setup; don't call table.clear() because it removes cell widgets
    table.setRowCount(len(rows) + 1)

    existing_filter = True
    if not table.cellWidget(0, 0) or not isinstance(table.cellWidget(0, 0), QtWidgets.QLineEdit):
        existing_filter = False

    for j in range(ncols):
        placeholder_item = QtWidgets.QTableWidgetItem("")
        placeholder_item.setFlags(Qt.ItemFlag(0))
        table.setItem(0, j, placeholder_item)

    if not existing_filter:
        from functools import partial
        for j in range(ncols):
            le = QtWidgets.QLineEdit()
            le.setPlaceholderText("")
            le.setText(str(fv.get(j, "")))
            if callable(filter_callback):
                le.textChanged.connect(partial(filter_callback, j))
            table.setCellWidget(0, j, le)
    else:
        from PyQt6.QtCore import QSignalBlocker
        for j in range(ncols):
            w = table.cellWidget(0, j)
            if isinstance(w, QtWidgets.QLineEdit):
                with QSignalBlocker(w):
                    w.setText(str(fv.get(j, "")))

    # Wiersze danych (od wiersza 1)
    expected = len(rows) + 1
    while table.rowCount() > expected:
        table.removeRow(table.rowCount() - 1)
    while table.rowCount() < expected:
        table.insertRow(table.rowCount())

    for i, r in enumerate(rows):
        row_idx = i + 1
        
        # Sprawdzenie czy pracownik został zwolniony
        kod_prac = str(r[5] or '').strip() if len(r) > 5 else ''
        is_dismissed = False
        data_zwol = ""
        
        if kod_prac:
            # Próba pobrania z employees_data
            if employees_data and kod_prac in employees_data:
                data_zwol = str(employees_data[kod_prac].get('Data_zwolnienia', '')).strip()
                is_dismissed = bool(data_zwol)
            else:
                # Fallback na DF_PRACOWNICY
                try:
                    from pracownicy import DF_PRACOWNICY
                    emp = DF_PRACOWNICY[DF_PRACOWNICY['Kod'] == kod_prac]
                    if not emp.empty:
                        data_zwol = str(emp.iloc[0]['Data_zwolnienia'] if 'Data_zwolnienia' in emp.columns else '').strip()
                        is_dismissed = bool(data_zwol)
                except Exception:
                    pass
        
        for j in range(ncols):
            val = r[j] if j < len(r) else ""
            item = QtWidgets.QTableWidgetItem("" if val is None else str(val))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Zwolnieni na czerwono z pogrubieniem
            if is_dismissed:
                from PyQt6 import QtGui
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QtGui.QColor("red"))
                # Tooltip z datą zwolnienia
                if data_zwol:
                    item.setToolTip(f"Pracownik zakończył współpracę dnia: {data_zwol}")
            
            table.setItem(row_idx, j, item)

    # Pomiar i zablokowanie szerokości
    try:
        from PyQt6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.resizeColumnsToContents()
        widths = [table.columnWidth(i) for i in range(table.columnCount())]
        for idx, w in enumerate(widths):
            # Tryb interaktywny po pomiarze
            header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)
            table.setColumnWidth(idx, w)
    except Exception:
        pass
    table.setColumnHidden(0, True)
    table.setSortingEnabled(True)
def render_employees_table(table: QtWidgets.QTableWidget, employees: list[dict], *, filter_callback=None, filter_values: dict | None = None):
    """Renderuje tabelę pracowników z filtrowaniem."""
    table.setSortingEnabled(False)
    table.setColumnCount(len(EMP_HEADERS))
    table.setHorizontalHeaderLabels(EMP_HEADERS)

    fv = filter_values or {}

    # Jeśli jest osobna tabela filtrów
    if hasattr(table, "filter_table") and table.filter_table is not None:
        ft = table.filter_table
        ft.setColumnCount(len(EMP_HEADERS))
        ft.setRowCount(1)
        ft.verticalHeader().setVisible(False)
        ft.horizontalHeader().setVisible(False)

        from functools import partial
        from PyQt6.QtCore import QSignalBlocker
        for j in range(len(EMP_HEADERS)):
            w = ft.cellWidget(0, j)
            if w is None or not isinstance(w, QtWidgets.QLineEdit):
                le = QtWidgets.QLineEdit()
                if callable(filter_callback):
                    le.textChanged.connect(partial(filter_callback, j))
                ft.setCellWidget(0, j, le)
                w = le
            with QSignalBlocker(w):
                w.setText(str(fv.get(j, "")))

        expected = len(employees)
        while table.rowCount() > expected:
            table.removeRow(table.rowCount() - 1)
        while table.rowCount() < expected:
            table.insertRow(table.rowCount())

        for i, e in enumerate(employees):
            values = [
                e.get("Kod",""), e.get("Nazwisko",""), e.get("Imię",""), e.get("Płeć",""),
                e.get("Dział",""), e.get("Stanowisko",""),
                e.get("Data_zatrudnienia",""), e.get("Data_zwolnienia",""),
                str(e.get("Szafki_count", 0)),
            ]
            
            # Sprawdzenie czy pracownik został zwolniony
            data_zwolnienia = str(e.get("Data_zwolnienia", "")).strip()
            is_dismissed = bool(data_zwolnienia)
            
            for j, val in enumerate(values):
                text = "" if val is None else str(val)
                # Use SortableItem with date ordinal for date columns (6, 7) and numeric for count (8)
                if j in (6, 7):
                    pd = parse_date(text)
                    item = SortableItem(text, pd.toordinal() if pd else None)
                elif j == 8:
                    try:
                        num = int(text)
                    except Exception:
                        num = None
                    item = SortableItem(text, num)
                else:
                    item = SortableItem(text, None)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                # Zwolnieni na czerwono z pogrubieniem
                if is_dismissed:
                    from PyQt6 import QtGui
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QtGui.QColor("red"))
                
                table.setItem(i, j, item)

        # Auto-dopasowanie kolumn przy pierwszym wyświetleniu
        try:
            if not getattr(table, '_autosized', False):
                from PyQt6.QtCore import QTimer
                def _do_autosize():
                    try:
                        from PyQt6.QtWidgets import QHeaderView
                        header = table.horizontalHeader()
                        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                        table.resizeColumnsToContents()
                        # Zablokowanie szerokości po autosizing
                        widths = [table.columnWidth(i) for i in range(table.columnCount())]

                        for idx, w in enumerate(widths):
                            # Tryb interaktywny po autosizing
                            header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)
                            table.setColumnWidth(idx, w)
                        table._autosized = True
                    except Exception:
                        pass
                if table.isVisible():
                    _do_autosize()
                else:
                    QTimer.singleShot(0, _do_autosize)
        except Exception:
            pass

        # Spójność widoczności kolumn
        ft.setColumnHidden(0, False)
        table.setColumnHidden(0, False)
        table.setSortingEnabled(True)
        # Klikalny nagłówek z przełączaniem sortowania
        try:
            header = table.horizontalHeader()
            header.setSectionsClickable(True)
            def _on_emp_header_clicked(idx, tbl=table):
                try:
                    prev = getattr(tbl, '_emp_sorted_col', None)
                    if prev != idx:
                        tbl._emp_sorted_col = idx
                        tbl._emp_sort_order = Qt.SortOrder.AscendingOrder
                    else:
                        tbl._emp_sort_order = Qt.SortOrder.DescendingOrder if getattr(tbl, '_emp_sort_order', Qt.SortOrder.AscendingOrder) == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
                    tbl.sortItems(idx, tbl._emp_sort_order)
                except Exception:
                    pass
            header.sectionClicked.connect(_on_emp_header_clicked)
        except Exception:
            pass
        return

    # Fallback: pojedyncza tabela
    table.setRowCount(len(employees))
    for i, e in enumerate(employees):
        values = [
            e.get("Kod",""), e.get("Nazwisko",""), e.get("Imię",""), e.get("Płeć",""),
            e.get("Dział",""), e.get("Stanowisko",""),
            e.get("Data_zatrudnienia",""), e.get("Data_zwolnienia",""),
            str(e.get("Szafki_count", 0)),
        ]
        
        # Sprawdzenie czy pracownik został zwolniony
        data_zwolnienia = str(e.get("Data_zwolnienia", "")).strip()
        is_dismissed = bool(data_zwolnienia)
        
        for j, val in enumerate(values):
            text = "" if val is None else str(val)
            if j in (6, 7):
                pd = parse_date(text)
                if pd:
                    item = SortableItem(text, pd.toordinal())
                else:
                    item = SortableItem(text, None)
            elif j == 8:
                try:
                    num = int(text)
                except Exception:
                    num = None
                item = SortableItem(text, num)
            else:
                item = SortableItem(text, None)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Zwolnieni na czerwono z pogrubieniem
            if is_dismissed:
                from PyQt6 import QtGui
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QtGui.QColor("red"))
            
            table.setItem(i, j, item)

    # Pomiar i zablokowanie szerokości
    try:
        from PyQt6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.resizeColumnsToContents()
        widths = [table.columnWidth(i) for i in range(table.columnCount())]

        for idx, w in enumerate(widths):
            # Tryb interaktywny po pomiarze
            header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)
            table.setColumnWidth(idx, w)
    except Exception:
        pass
    table.setSortingEnabled(True)

def render_employee_lockers_panel(table: QtWidgets.QTableWidget, lockers: list[dict]):
    table.setRowCount(len(lockers))
    for i, s in enumerate(lockers):
        table.setItem(i, 0, QtWidgets.QTableWidgetItem(s.get("miejsce","")))
        table.setItem(i, 1, QtWidgets.QTableWidgetItem(s.get("nr_szafki","")))
        table.setItem(i, 2, QtWidgets.QTableWidgetItem(s.get("nr_zamka","")))
        table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(s.get("id",""))))
    table.resizeColumnsToContents()