from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from auth import get_user, verify_password, change_password, validate_password
from session import set_current_user

# Dialog nowego hasła
class SetNewPasswordDialog(QDialog):
    """Dialog ustawiania nowego hasła po jednorazowym haśle."""
    def __init__(self, login: str, parent=None):
        super().__init__(parent)
        self.login = login
        self.setWindowTitle("Ustaw nowe hasło")
        self.setModal(True)

        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pw2 = QLineEdit()
        self.new_pw2.setEchoMode(QLineEdit.EchoMode.Password)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Nowe hasło:"))
        layout.addWidget(self.new_pw)
        layout.addWidget(QLabel("Powtórz nowe hasło:"))
        layout.addWidget(self.new_pw2)

        btns = QHBoxLayout()
        ok = QPushButton("Ustaw")
        ok.clicked.connect(self._on_set)
        cancel = QPushButton("Anuluj")
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def _on_set(self):
        if self.new_pw.text() != self.new_pw2.text():
            QMessageBox.critical(self, "Błąd", "Nowe hasła nie są identyczne")
            return
        # Sprawdzanie wymagań nowego hasła
        valid, err = validate_password(self.new_pw.text())
        if not valid:
            QMessageBox.critical(self, "Błąd", err)
            return

        ok = change_password(self.login, self.new_pw.text())
        if ok:
            QMessageBox.information(self, "Sukces", "Hasło zmienione")
            self.accept()
        else:
            QMessageBox.critical(self, "Błąd", "Zmiana hasła nie powiodła się")

# Dialog zmiany hasła
class ChangePasswordDialog(QDialog):
    def __init__(self, login: str, parent=None, require_old: bool = True):
        super().__init__(parent)
        self.login = login
        self.require_old = require_old
        self.setWindowTitle("Zmień hasło")
        self.setModal(True)

        self.old_pw = QLineEdit()
        self.old_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pw2 = QLineEdit()
        self.new_pw2.setEchoMode(QLineEdit.EchoMode.Password)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Stare hasło:"))
        layout.addWidget(self.old_pw)
        layout.addWidget(QLabel("Nowe hasło:"))
        layout.addWidget(self.new_pw)
        layout.addWidget(QLabel("Powtórz nowe hasło:"))
        layout.addWidget(self.new_pw2)

        btns = QHBoxLayout()
        ok = QPushButton("Zmień")
        ok.clicked.connect(self._on_change)
        cancel = QPushButton("Anuluj")
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def _on_change(self):
        if self.new_pw.text() != self.new_pw2.text():
            QMessageBox.critical(self, "Błąd", "Nowe hasła nie są identyczne")
            return
        # Sprawdzanie wymagań nowego hasła
        valid, err = validate_password(self.new_pw.text())
        if not valid:
            QMessageBox.critical(self, "Błąd", err)
            return
        # Jeśli wymagane, sprawdzenie starego hasła
        if self.require_old:
            u = get_user(self.login)
            if not u or not verify_password(u.get('password_hash', ''), self.old_pw.text()):
                QMessageBox.critical(self, "Błąd", "Stare hasło nieprawidłowe")
                return

        ok = change_password(self.login, self.new_pw.text())
        if ok:
            QMessageBox.information(self, "Sukces", "Hasło zmienione")
            self.accept()
        else:
            QMessageBox.critical(self, "Błąd", "Zmiana hasła nie powiodła się")


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logowanie")
        self.setModal(True)
        self.resize(320, 140)

        self.login_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Login:"))
        layout.addWidget(self.login_edit)
        layout.addWidget(QLabel("Hasło:"))
        layout.addWidget(self.password_edit)

        btns = QHBoxLayout()
        login_btn = QPushButton("Zaloguj")
        login_btn.clicked.connect(self._on_login)
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(login_btn)
        btns.addWidget(cancel_btn)

        layout.addLayout(btns)
        self.setLayout(layout)

        self.user = None

    def _on_login(self):
        user = get_user(self.login_edit.text().strip())
        if not user:
            QMessageBox.critical(self, "Błąd", "Nieprawidłowy login lub hasło")
            return
        if not verify_password(user['password_hash'], self.password_edit.text()):
            QMessageBox.critical(self, "Błąd", "Nieprawidłowy login lub hasło")
            return

        # Jeśli hasło jednorazowe, wymuś zmianę
        if user.get('one_time'):
            dlg = SetNewPasswordDialog(user['login'], self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                QMessageBox.information(self, "Info", "Wymagana zmiana hasła")
                return
            # Przeładuj dane użytkownika po zmianie hasła
            user = get_user(user['login'])

        # Ustaw sesję i zaakceptuj
        set_current_user(user)
        self.user = user
        self.accept()
