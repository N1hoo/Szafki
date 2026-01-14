from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from ui.renderers import SortableItem, parse_date

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
                # Kolumny dat jako sortowalne
                if col in ("Data_zatrudnienia", "Data_zwolnienia"):
                    pd = parse_date(val)
                    if pd:
                        item = SortableItem(val, pd.toordinal())
                    else:
                        item = SortableItem(val, None)
                else:
                    item = SortableItem(val, None)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)

        table.setSortingEnabled(True)

        # Klikalne nagłówki z przełączaniem sortowania
        try:
            header = table.horizontalHeader()
            header.setSectionsClickable(True)
            def _on_new_emp_header_clicked(idx, tbl=table):
                try:
                    prev = getattr(tbl, '_new_emp_sorted_col', None)
                    if prev != idx:
                        tbl._new_emp_sorted_col = idx
                        tbl._new_emp_sort_order = Qt.SortOrder.AscendingOrder
                    else:
                        tbl._new_emp_sort_order = Qt.SortOrder.DescendingOrder if getattr(tbl, '_new_emp_sort_order', Qt.SortOrder.AscendingOrder) == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
                    tbl.sortItems(idx, tbl._new_emp_sort_order)
                except Exception:
                    pass
            header.sectionClicked.connect(_on_new_emp_header_clicked)
        except Exception:
            pass

        # Dopasowanie szerokości kolumn
        try:
            from PyQt6.QtWidgets import QHeaderView
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            table.resizeColumnsToContents()
            widths = [table.columnWidth(i) for i in range(table.columnCount())]
            for idx, w in enumerate(widths):
                header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)
                table.setColumnWidth(idx, w)
        except Exception:
            pass

        btn = QtWidgets.QPushButton("Zamknij")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)