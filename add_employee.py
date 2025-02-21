from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from excel_reader import znajdz_pracownika

class DodajPracownika(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dodawanie pracownika")
        self.setGeometry(300, 200, 400, 300)

        layout = QVBoxLayout()

        self.label_id = QLabel("Kod pracownika:")
        self.input_id = QLineEdit()
        self.input_id.textChanged.connect(self.wyszukaj_pracownika)

        self.label_imie = QLabel("Imię:")
        self.input_imie = QLineEdit()

        self.label_nazwisko = QLabel("Nazwisko:")
        self.input_nazwisko = QLineEdit()

        self.label_dzial = QLabel("Dział:")
        self.input_dzial = QLineEdit()

        self.label_stanowisko = QLabel("Stanowisko:")
        self.input_stanowisko = QLineEdit()

        self.btn_dodaj = QPushButton("Dodaj")
        self.btn_dodaj.clicked.connect(self.dodaj_pracownika)

        layout.addWidget(self.label_id)
        layout.addWidget(self.input_id)
        layout.addWidget(self.label_imie)
        layout.addWidget(self.input_imie)
        layout.addWidget(self.label_nazwisko)
        layout.addWidget(self.input_nazwisko)
        layout.addWidget(self.label_dzial)
        layout.addWidget(self.input_dzial)
        layout.addWidget(self.label_stanowisko)
        layout.addWidget(self.input_stanowisko)
        layout.addWidget(self.btn_dodaj)

        self.setLayout(layout)

    def wyszukaj_pracownika(self):
        """Automatycznie uzupełnia pola po wpisaniu kodu pracownika"""
        kod = self.input_id.text().strip()
        if len(kod) == 6 and kod.isdigit():  # Sprawdzamy, czy kod ma 6 cyfr
            pracownik = znajdz_pracownika(kod, "pracownicy.xlsx", "TwojeHaslo")
            if pracownik:
                self.input_imie.setText(pracownik["Imię"])
                self.input_nazwisko.setText(pracownik["Nazwisko"])
                self.input_dzial.setText(pracownik["Dział"])
                self.input_stanowisko.setText(pracownik["Stanowisko"])
            else:
                self.input_imie.clear()
                self.input_nazwisko.clear()
                self.input_dzial.clear()
                self.input_stanowisko.clear()

    def dodaj_pracownika(self):
        """Tutaj zapisujemy pracownika do bazy"""
        kod = self.input_id.text()
        imie = self.input_imie.text()
        nazwisko = self.input_nazwisko.text()
        dzial = self.input_dzial.text()
        stanowisko = self.input_stanowisko.text()

        print(f"Dodano pracownika: {kod}, {imie} {nazwisko}, {dzial}, {stanowisko}")