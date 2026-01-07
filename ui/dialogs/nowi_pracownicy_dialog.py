from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

class NowiPracownicyDialog(QtWidgets.QDialog):
    def __init__(self, df_new, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nowi pracownicy (bez szafki)")
        self.resize(900, 500)

        layout = QtWidgets.QVBoxLayout(self)

        info = QtWidgets.QLabel(f"Znaleziono: {len(df_new)} aktywnych pracowników bez przypisanej szafki.")
        layout.addWidget(info)

        table = QtWidgets.QTableWidget(self)
        layout.addWidget(table)

        cols = ["Kod", "Nazwisko", "Imię", "Dział", "Stanowisko", "Płeć", "Data_zatrudnienia", "Data_zwolnienia"]
        table.setColumnCount(len(cols))
        table.setHorizontalHeaderLabels(cols)
        table.setRowCount(len(df_new))

        for r in range(len(df_new)):
            row = df_new.iloc[r]
            for c, col in enumerate(cols):
                val = "" if col not in row or row[col] is None else str(row[col])
                item = QtWidgets.QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)

        table.resizeColumnsToContents()

        btn = QtWidgets.QPushButton("Zamknij")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)