from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from pracownicy import DF_PRACOWNICY


class PrzydzielSzafkeDialog(QDialog):
    """Dialog przypisywania szafki do pracownika"""
    
    def __init__(self, locker_info: dict, parent=None):
        super().__init__(parent)
        self.locker_info = locker_info
        self.selected_employee = None
        self.setup_ui()
        self.load_employees()
    
    def setup_ui(self):
        """Konfiguracja UI dialogu"""
        self.setWindowTitle("Przydziel szafkę")
        self.setGeometry(100, 100, 600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Sekcja informacji o szafce
        info_layout = QHBoxLayout()
        info_text = (
            f"Szatnia: <b>{self.locker_info.get('Miejsce', '')}</b> | "
            f"Nr: <b>{self.locker_info.get('Nr_szafki', '')}</b> | "
            f"Płeć: <b>{self.locker_info.get('Płeć_szatni', '')}</b>"
        )
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-size: 11pt; padding: 10px; background-color: white; color: black; border-radius: 5px;")
        info_layout.addWidget(info_label)
        main_layout.addLayout(info_layout)
        
        # Sekcja wyszukiwania
        search_layout = QHBoxLayout()
        search_label = QLabel("Wyszukaj pracownika:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Kod, nazwisko, imię...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        main_layout.addLayout(search_layout)
        
        # Tabela pracowników
        table_label = QLabel("Dostępni pracownicy (zatrudnieni):")
        main_layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Kod", "Nazwisko", "Imię", "Dział", "Stanowisko"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 150)
        self.table.itemSelectionChanged.connect(self.on_employee_selected)
        main_layout.addWidget(self.table, 1)
        
        # Info o wybranym pracowniku
        self.selected_label = QLabel("Wybrany pracownik: brak")
        self.selected_label.setStyleSheet("font-size: 10pt; color: #555;")
        main_layout.addWidget(self.selected_label)
        
        # Przyciski
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.assign_btn = QPushButton("Przydziel")
        self.assign_btn.setMinimumWidth(100)
        self.assign_btn.clicked.connect(self.accept)
        self.assign_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("Anuluj")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.assign_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)
    
    def load_employees(self):
        """Załaduj pracowników do tabeli"""
        try:
            df = DF_PRACOWNICY.copy().reset_index()
            
            # Tylko zatrudnieni (bez daty zwolnienia)
            employed = []
            for _, row in df.iterrows():
                data_zwol = str(row.get('Data_zwolnienia', '')).strip()
                if not data_zwol:  # Zatrudniony
                    employed.append(row)
            
            self.all_employees = employed
            self.refresh_table(employed)
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się załadować pracowników:\n{str(e)}")
    
    def refresh_table(self, employees):
        """Odśwież tabelę z podanymi pracownikami"""
        self.table.setRowCount(0)
        
        for row_idx, emp in enumerate(employees):
            self.table.insertRow(row_idx)
            
            kod = str(emp.get('Kod', '')).strip()
            nazw = str(emp.get('Nazwisko', '')).strip()
            im = str(emp.get('Imię', '')).strip()
            dz = str(emp.get('Dział', '')).strip()
            stan = str(emp.get('Stanowisko', '')).strip()
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(kod))
            self.table.setItem(row_idx, 1, QTableWidgetItem(nazw))
            self.table.setItem(row_idx, 2, QTableWidgetItem(im))
            self.table.setItem(row_idx, 3, QTableWidgetItem(dz))
            self.table.setItem(row_idx, 4, QTableWidgetItem(stan))
    
    def on_search_changed(self, text):
        """Filtruj pracowników wg tekstu"""
        search_text = text.strip().lower()
        
        if not search_text:
            self.refresh_table(self.all_employees)
            return
        
        filtered = []
        for emp in self.all_employees:
            kod = str(emp.get('Kod', '')).strip().lower()
            nazw = str(emp.get('Nazwisko', '')).strip().lower()
            im = str(emp.get('Imię', '')).strip().lower()
            dz = str(emp.get('Dział', '')).strip().lower()
            stan = str(emp.get('Stanowisko', '')).strip().lower()
            
            if (search_text in kod or search_text in nazw or 
                search_text in im or search_text in dz or search_text in stan):
                filtered.append(emp)
        
        self.refresh_table(filtered)
    
    def on_employee_selected(self):
        """Obsługa wyboru pracownika"""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.selected_label.setText("Wybrany pracownik: brak")
            self.assign_btn.setEnabled(False)
            self.selected_employee = None
            return
        
        row_idx = selected_rows[0].row()
        kod = self.table.item(row_idx, 0).text()
        nazw = self.table.item(row_idx, 1).text()
        im = self.table.item(row_idx, 2).text()
        
        self.selected_label.setText(f"Wybrany pracownik: <b>{kod}</b> — {nazw} {im}")
        self.assign_btn.setEnabled(True)
        
        # Zapisanie danych wybranego pracownika
        self.selected_employee = {
            'Kod': kod,
            'Nazwisko': nazw,
            'Imię': im,
            'Dział': self.table.item(row_idx, 3).text(),
            'Stanowisko': self.table.item(row_idx, 4).text(),
        }
    
    def get_selected_employee(self):
        """Pobiera dane wybranego pracownika"""
        return self.selected_employee
