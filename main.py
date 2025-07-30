import sys
from PyQt6.QtWidgets import QApplication
from MainWindow import OknoGlowne
from database import inicjuj_baze
from pracownicy import DF_PRACOWNICY  # załadowanie CSV na starcie aplikacji

if __name__ == "__main__":
    inicjuj_baze()  # inicjalizacja bazy danych
    app = QApplication(sys.argv)
    okno = OknoGlowne()
    okno.show()
    sys.exit(app.exec())