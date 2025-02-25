# main.py
import sys
from PyQt6.QtWidgets import QApplication
from MainWindow import OknoGlowne

if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = OknoGlowne()
    okno.show()
    sys.exit(app.exec())