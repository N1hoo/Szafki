# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import OknoGlowne

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OknoGlowne()
    w.show()
    sys.exit(app.exec())