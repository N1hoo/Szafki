from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QMessageBox, QSpinBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt

from database import (
    pobierz_wszystkie_miejsca, pobierz_wszystkie_plci, 
    pobierz_max_nr_szafki, dodaj_szafke_dla_miejsca
)
from session import get_current_user, is_admin


class DodajSzafkiDialog(QDialog):
    """Dialog dodawania nowych szafek"""
    
    def __init__(self, parent=None, lockers_data=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj szafki")
        self.setModal(True)
        self.setMinimumWidth(900)
        self.setMinimumHeight(500)
        
        self.lockers_data = lockers_data or []
        
        # Dane użytkownika
        self.user = get_current_user()
        self.is_admin_user = bool(self.user and self.user.get('role') == 'admin')
        
        # Dostępne wartości z DB
        self.wszystkie_miejsca = pobierz_wszystkie_miejsca()
        self.wszystkie_plci = pobierz_wszystkie_plci()
        if not self.wszystkie_plci:
            self.wszystkie_plci = ["Kobieta", "Mężczyzna", "Neutralna"]
        
        # Selektor działu (tylko dla adminów)
        phys_depts = sorted({str(x[14]).strip() for x in self.lockers_data if x and len(x) > 14 and x[14]})
        self.wszystkie_dzialy = phys_depts if phys_depts else []
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Sekcja górna - selektory
        top_layout = QHBoxLayout()
        
        # Miejsce
        top_layout.addWidget(QLabel("Miejsce:"))
        self.miejsce_cb = QComboBox()
        self.miejsce_cb.addItems([""] + self.wszystkie_miejsca)
        self.miejsce_cb.setMinimumWidth(120)
        self.miejsce_cb.currentTextChanged.connect(self._on_selectors_changed)
        self.miejsce_cb.currentTextChanged.connect(self._on_miejsce_changed)
        top_layout.addWidget(self.miejsce_cb)
        
        # Przycisk dodawania miejsca
        btn_new_place = QPushButton("Nowe miejsce")
        btn_new_place.setMaximumWidth(100)
        btn_new_place.clicked.connect(self._add_new_place)
        top_layout.addWidget(btn_new_place)
        
        # Płeć
        top_layout.addWidget(QLabel("Płeć:"))
        self.plec_cb = QComboBox()
        self.plec_cb.addItems([""] + self.wszystkie_plci)
        self.plec_cb.setMinimumWidth(120)
        self.plec_cb.currentTextChanged.connect(self._on_selectors_changed)
        top_layout.addWidget(self.plec_cb)
        
        # Dział fizyczny (tylko admin)
        if self.is_admin_user:
            top_layout.addWidget(QLabel("Dział:"))
            self.dzial_cb = QComboBox()
            self.dzial_cb.addItems([""] + self.wszystkie_dzialy)
            self.dzial_cb.setMinimumWidth(120)
            self.dzial_cb.currentTextChanged.connect(self._on_selectors_changed)
            top_layout.addWidget(self.dzial_cb)
        else:
            self.dzial_cb = None
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Tabela wierszy
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Nr szafki", "Nr zamka"])
        self.table_widget.setMinimumHeight(300)
        layout.addWidget(self.table_widget, 1)
        
        # Przyciski zarządzania wierszami
        btns_layout = QHBoxLayout()
        
        btn_minus = QPushButton("-")
        btn_minus.setMaximumWidth(40)
        btn_minus.clicked.connect(self._remove_row)
        btns_layout.addWidget(btn_minus)
        
        btn_plus = QPushButton("+")
        btn_plus.setMaximumWidth(40)
        btn_plus.clicked.connect(self._add_single_row)
        btns_layout.addWidget(btn_plus)
        
        btn_add_multiple = QPushButton("Dodaj wiele")
        btn_add_multiple.clicked.connect(self._add_multiple_rows_dialog)
        btns_layout.addWidget(btn_add_multiple)
        
        btns_layout.addStretch()
        layout.addLayout(btns_layout)
        
        # Przyciski dolne
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        btn_ok = QPushButton("Dodaj szafki")
        btn_ok.clicked.connect(self._on_ok)
        btn_cancel = QPushButton("Anuluj")
        btn_cancel.clicked.connect(self.reject)
        
        bottom_layout.addWidget(btn_ok)
        bottom_layout.addWidget(btn_cancel)
        layout.addLayout(bottom_layout)
        
        # Automatyczne dodanie pierwszego wiersza
        self._add_single_row()
    
    def _on_selectors_changed(self):
        """Aktualizacja numerów po zmianie selektorów"""
        self._update_all_nr_szafki()
    
    def _on_miejsce_changed(self):
        """Automatyczny wybór płci na podstawie miejsca"""
        miejsce = self.miejsce_cb.currentText().strip()
        
        if not miejsce:
            return
        
        # Automatyczny wybór na podstawie prefiksu miejsca
        if miejsce.startswith("Damska"):
            self.plec_cb.blockSignals(True)
            self.plec_cb.setCurrentText("Damska")
            self.plec_cb.blockSignals(False)
        elif miejsce.startswith("Męska"):
            self.plec_cb.blockSignals(True)
            self.plec_cb.setCurrentText("Męska")
            self.plec_cb.blockSignals(False)
        elif miejsce == "Stołówka":
            self.plec_cb.blockSignals(True)
            self.plec_cb.setCurrentText("Neutralna")
            self.plec_cb.blockSignals(False)
    
    def _update_all_nr_szafki(self):
        """Aktualizacja wszystkich numerów szafek"""
        miejsce = self.miejsce_cb.currentText().strip()
        plec = self.plec_cb.currentText().strip()
        dzial = self.dzial_cb.currentText().strip() if self.is_admin_user else (self.user.get('dzial') if self.user else '')
        
        if not miejsce or not plec or not dzial:
            return
        
        max_nr = pobierz_max_nr_szafki(miejsce, plec, dzial)
        
        # Aktualizacja wszystkich wierszy z auto-inkrementacją
        for i in range(self.table_widget.rowCount()):
            nr_item = self.table_widget.item(i, 0)
            if nr_item:
                nr_item.setText(str(max_nr + i + 1))
    
    def _add_new_place(self):
        """Wyświetla dialog dodawania miejsca"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nowe miejsce szafek")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Nazwa nowego miejsca:"))
        
        text_edit = QLineEdit()
        layout.addWidget(text_edit)
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel = QPushButton("Anuluj")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_place = text_edit.text().strip()
            if new_place:
                # Potwierdzenie utworzenia nowego miejsca
                reply = QMessageBox.question(
                    self, "Potwierdzenie",
                    f"Czy na pewno chcesz utworzyć nowe miejsce '{new_place}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Dodanie do listy i wybranie
                    if new_place not in self.wszystkie_miejsca:
                        self.wszystkie_miejsca.append(new_place)
                        self.wszystkie_miejsca.sort()
                    
                    # Aktualizacja combobox
                    self.miejsce_cb.blockSignals(True)
                    self.miejsce_cb.clear()
                    self.miejsce_cb.addItems([""] + self.wszystkie_miejsca)
                    self.miejsce_cb.setCurrentText(new_place)
                    self.miejsce_cb.blockSignals(False)
                    
                    # Aktualizacja tabeli z nowymi numerami
                    self._update_all_nr_szafki()
    
    def _add_single_row(self):
        """Dodaje pojedynczy wiersz"""
        self._add_rows(1)
    
    def _remove_row(self):
        """Usuwa ostatni wiersz"""
        if self.table_widget.rowCount() > 0:
            self.table_widget.removeRow(self.table_widget.rowCount() - 1)
    
    def _add_multiple_rows_dialog(self):
        """Dialog wyboru liczby wierszy"""
        current_rows = self.table_widget.rowCount()
        max_additional = 25 - current_rows
        
        if max_additional <= 0:
            QMessageBox.warning(self, "Limit", "Nie można dodać więcej niż 25 wierszy łącznie.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Dodaj wiele szafek")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Ile szafek chcesz dodać? (1-{max_additional})"))
        
        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setMaximum(max_additional)
        spin.setValue(min(5, max_additional))
        layout.addWidget(spin)
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel = QPushButton("Anuluj")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._add_rows(spin.value())
    
    def _add_rows(self, count: int):
        """Dodaje wiele wierszy do tabeli"""
        start_row = self.table_widget.rowCount()
        
        # Dodanie nowych wierszy
        for i in range(count):
            row = start_row + i
            self.table_widget.insertRow(row)
            
            # Nr szafki - tylko odczyt
            nr_item = QTableWidgetItem("")
            nr_item.setFlags(nr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 0, nr_item)
            
            # Nr zamka - edytowalny
            zamka_item = QTableWidgetItem("")
            self.table_widget.setItem(row, 1, zamka_item)
        
        # Aktualizacja numerów
        self._update_all_nr_szafki()
    
    def _validate_inputs(self):
        """Walidacja selektorów i tabeli"""
        if not self.miejsce_cb.currentText().strip():
            QMessageBox.warning(self, "Błąd", "Pole 'Miejsce' jest wymagane.")
            return False
        
        if not self.plec_cb.currentText().strip():
            QMessageBox.warning(self, "Błąd", "Pole 'Płeć' jest wymagane.")
            return False
        
        if self.is_admin_user and not self.dzial_cb.currentText().strip():
            QMessageBox.warning(self, "Błąd", "Pole 'Dział' jest wymagane.")
            return False
        
        if self.table_widget.rowCount() == 0:
            QMessageBox.warning(self, "Błąd", "Dodaj przynajmniej jeden wiersz.")
            return False
        
        # Walidacja danych tabeli
        for i in range(self.table_widget.rowCount()):
            nr_item = self.table_widget.item(i, 0)
            if not nr_item or not nr_item.text().strip():
                QMessageBox.warning(self, "Błąd", f"Wiersz {i+1}: Numer szafki jest pusty.")
                return False
            
            try:
                int(nr_item.text())
            except ValueError:
                QMessageBox.warning(self, "Błąd", f"Wiersz {i+1}: Numer szafki musi być liczbą.")
                return False
            
            zamka_item = self.table_widget.item(i, 1)
            if zamka_item and zamka_item.text().strip():
                try:
                    int(zamka_item.text().strip())
                except ValueError:
                    QMessageBox.warning(self, "Błąd", f"Wiersz {i+1}: Numer zamka musi być liczbą lub puste.")
                    return False
        
        return True
    
    def _on_ok(self):
        """Walidacja i dodanie szafek"""
        if not self._validate_inputs():
            return
        
        # Potwierdzenie
        reply = QMessageBox.question(
            self, "Potwierdź",
            f"Czy na pewno chcesz dodać {self.table_widget.rowCount()} szafkę/szafek?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Dodanie szafek do bazy
        try:
            from history import log_event
            from session import get_current_user
            
            performed_by = (get_current_user() or {}).get('login')
            
            miejsce = self.miejsce_cb.currentText().strip()
            plec = self.plec_cb.currentText().strip()
            dzial = self.dzial_cb.currentText().strip() if self.is_admin_user else (self.user.get('dzial') if self.user else '')
            
            for i in range(self.table_widget.rowCount()):
                nr_sz = int(self.table_widget.item(i, 0).text())
                zamka_item = self.table_widget.item(i, 1)
                nr_zamka = int(zamka_item.text()) if zamka_item and zamka_item.text().strip() else None
                
                new_id = dodaj_szafke_dla_miejsca(
                    miejsce=miejsce,
                    nr_szafki=nr_sz,
                    nr_zamka=nr_zamka,
                    plec_szatni=plec,
                    dzial=dzial,
                    status="Wolna"
                )
                
                # Logowanie zdarzenia utworzenia
                try:
                    from database import pobierz_szafki
                    new_rows = pobierz_szafki()
                    new_row = next((r for r in new_rows if r and r[0] == new_id), None)
                    if new_row:
                        from services.lockers_service import LockersService
                        svc = LockersService()
                        after_dict = svc._row_to_dict(new_row)
                        log_event("create", new_id, None, after_dict, performed_by)
                except Exception:
                    pass
            
            QMessageBox.information(self, "Sukces", f"Dodano {self.table_widget.rowCount()} szafkę/szafek.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd przy dodawaniu szafek: {str(e)}")
