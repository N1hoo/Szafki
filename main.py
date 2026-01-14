# Punkt wejścia aplikacji
import sys
from PyQt6.QtWidgets import QApplication, QDialog
from ui.main_window import OknoGlowne
from ui.dialogs.login_dialog import LoginDialog
from session import get_current_user

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Logowanie użytkownika
    dlg = LoginDialog()
    if dlg.exec() != QDialog.DialogCode.Accepted:
        # Anulowano
        sys.exit(0)

    # Sesja aktywna
    w = OknoGlowne()
    w.showMaximized()
    sys.exit(app.exec())