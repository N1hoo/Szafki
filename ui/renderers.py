from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

LOCKERS_HEADERS = [
    "ID", "Miejsce", "Nr szafki", "Nr zamka", "Płeć szatni", "Kod prac.", "Nazwisko",
    "Imię", "Dział", "Stanowisko", "Płeć", "Zmiana", "Status", "Komentarz"
]

EMP_HEADERS = [
    "Kod","Nazwisko","Imię","Płeć","Dział","Stanowisko","Data zatr.","Data zwol.","Szafki"
]

def render_lockers_table(table: QtWidgets.QTableWidget, rows: list[tuple]):
    table.setSortingEnabled(False)
    table.clear()
    table.setColumnCount(14)
    table.setRowCount(len(rows))
    table.setHorizontalHeaderLabels(LOCKERS_HEADERS)

    for i, r in enumerate(rows):
        for j in range(14):
            val = r[j] if j < len(r) else ""
            item = QtWidgets.QTableWidgetItem("" if val is None else str(val))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(i, j, item)

    table.resizeColumnsToContents()
    table.setColumnHidden(0, True)
    table.setSortingEnabled(True)

def render_employees_table(table: QtWidgets.QTableWidget, employees: list[dict]):
    table.setSortingEnabled(False)
    table.clearContents()
    table.setColumnCount(len(EMP_HEADERS))
    table.setRowCount(len(employees))
    table.setHorizontalHeaderLabels(EMP_HEADERS)

    for i, e in enumerate(employees):
        values = [
            e.get("Kod",""), e.get("Nazwisko",""), e.get("Imię",""), e.get("Płeć",""),
            e.get("Dział",""), e.get("Stanowisko",""),
            e.get("Data_zatrudnienia",""), e.get("Data_zwolnienia",""),
            str(e.get("Szafki_count", 0)),
        ]
        for j, val in enumerate(values):
            item = QtWidgets.QTableWidgetItem("" if val is None else str(val))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(i, j, item)

    table.resizeColumnsToContents()
    table.setSortingEnabled(True)

def render_employee_lockers_panel(table: QtWidgets.QTableWidget, lockers: list[dict]):
    table.setRowCount(len(lockers))
    for i, s in enumerate(lockers):
        table.setItem(i, 0, QtWidgets.QTableWidgetItem(s.get("miejsce","")))
        table.setItem(i, 1, QtWidgets.QTableWidgetItem(s.get("nr_szafki","")))
        table.setItem(i, 2, QtWidgets.QTableWidgetItem(s.get("nr_zamka","")))
        table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(s.get("id",""))))
    table.resizeColumnsToContents()