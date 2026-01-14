from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QDialog, QLabel, QLineEdit, QComboBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from auth import list_users, create_user, update_user, set_one_time_password


class AddEditUserDialog(QDialog):
    def __init__(self, parent=None, user: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj użytkownika" if user is None else "Edytuj użytkownika")
        self.resize(420, 260)
        self.user = user

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Login:"))
        self.login = QLineEdit()
        layout.addWidget(self.login)

        layout.addWidget(QLabel("Hasło (tylko przy tworzeniu):"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        # Checkbox hasła jednorazowego (tylko przy tworzeniu)
        self.one_time_cb = QCheckBox("Hasło jednorazowe")
        if user is None:
            self.one_time_cb.setChecked(True)
        layout.addWidget(self.one_time_cb)
        if user is not None:
            self.one_time_cb.setEnabled(False)  # Nie można zmieniać przy edycji

        layout.addWidget(QLabel("Imię:"))
        self.first = QLineEdit()
        layout.addWidget(self.first)

        layout.addWidget(QLabel("Nazwisko:"))
        self.last = QLineEdit()
        layout.addWidget(self.last)

        layout.addWidget(QLabel("Rola:"))
        self.role = QComboBox()
        self.role.addItems(["user", "admin"])
        layout.addWidget(self.role)

        layout.addWidget(QLabel("Dział:"))
        self.dzial = QLineEdit()
        layout.addWidget(self.dzial)

        btns = QHBoxLayout()
        ok = QPushButton("Zapisz")
        ok.clicked.connect(self.on_ok)
        cancel = QPushButton("Anuluj")
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        if user:
            self.login.setText(user['login'])
            self.login.setEnabled(False)
            self.first.setText(user.get('first_name') or '')
            self.last.setText(user.get('last_name') or '')
            self.role.setCurrentText(user.get('role') or 'user')
            self.dzial.setText(user.get('dzial') or '')
            self.one_time_cb.setChecked(user.get('one_time', False))

    def on_ok(self):
        login = self.login.text().strip()
        if not login:
            QMessageBox.warning(self, "Błąd", "Podaj login")
            return
        if self.user is None and not self.password.text():
            QMessageBox.warning(self, "Błąd", "Podaj hasło dla nowego użytkownika")
            return
        # Walidacja i zamknięcie przy edycji
        self.accept()


class UsersPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Login", "Imię", "Nazwisko", "Rola", "Dział", "One-time"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        row = QHBoxLayout()
        self.add_btn = QPushButton("Dodaj")
        self.edit_btn = QPushButton("Edytuj")
        self.reset_btn = QPushButton("Resetuj hasło (one-time)")
        row.addWidget(self.add_btn)
        row.addWidget(self.edit_btn)
        row.addWidget(self.reset_btn)
        row.addStretch(1)
        layout.addLayout(row)

        self.add_btn.clicked.connect(self.on_add)
        self.edit_btn.clicked.connect(self.on_edit)
        self.reset_btn.clicked.connect(self.on_reset)

        self.reload()

    def reload(self):
        users = list_users()
        self.table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(u['login']))
            self.table.setItem(i, 1, QTableWidgetItem(u.get('first_name') or ''))
            self.table.setItem(i, 2, QTableWidgetItem(u.get('last_name') or ''))
            self.table.setItem(i, 3, QTableWidgetItem(u.get('role') or 'user'))
            self.table.setItem(i, 4, QTableWidgetItem(u.get('dzial') or ''))
            self.table.setItem(i, 5, QTableWidgetItem("Tak" if u.get('one_time') else "Nie"))

    def _selected_login(self) -> str | None:
        r = self.table.currentRow()
        if r < 0:
            return None
        it = self.table.item(r, 0)
        if not it:
            return None
        return it.text().strip()

    def on_add(self):
        dlg = AddEditUserDialog(self, user=None)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        login = dlg.login.text().strip()
        pw = dlg.password.text()
        first = dlg.first.text().strip()
        last = dlg.last.text().strip()
        role = dlg.role.currentText()
        dz = dlg.dzial.text().strip()
        one_time = dlg.one_time_cb.isChecked()

        ok = create_user(login, pw, first_name=first, last_name=last, role=role, dzial=dz, one_time=one_time)
        if not ok:
            QMessageBox.warning(self, "Błąd", "Użytkownik o tym loginie już istnieje lub hasło nie spełnia wymagań")
            return
        QMessageBox.information(self, "Sukces", "Utworzono użytkownika")
        self.reload()

    def on_edit(self):
        login = self._selected_login()
        if not login:
            QMessageBox.warning(self, "Brak zaznaczenia", "Wybierz użytkownika")
            return
        from auth import get_user
        u = get_user(login)
        dlg = AddEditUserDialog(self, user=u)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        update_user(login, first_name=dlg.first.text().strip(), last_name=dlg.last.text().strip(), role=dlg.role.currentText(), dzial=dlg.dzial.text().strip())
        QMessageBox.information(self, "Sukces", "Zapisano zmiany")
        self.reload()

    def on_reset(self):
        login = self._selected_login()
        if not login:
            QMessageBox.warning(self, "Brak zaznaczenia", "Wybierz użytkownika")
            return
        
        # Dialog hasła jednorazowego
        dlg = QDialog(self)
        dlg.setWindowTitle("Resetuj hasło (one-time)")
        dlg.resize(340, 150)
        layout = QVBoxLayout(dlg)
        
        layout.addWidget(QLabel("Wybierz opcję:"))
        gen_btn = QPushButton("Wygeneruj losowe hasło")
        manual_btn = QPushButton("Ustaw hasło ręcznie")
        
        def on_generate():
            pw = set_one_time_password(login)
            if pw is None:
                QMessageBox.warning(dlg, "Błąd", "Nie udało się zresetować hasła (użytkownik nie istnieje)")
                return
            QMessageBox.information(dlg, "Hasło tymczasowe", f"Nowe hasło jednorazowe dla {login}: {pw}")
            self.reload()
            dlg.accept()
        
        def on_manual():
            pwd_dlg = QDialog(dlg)
            pwd_dlg.setWindowTitle("Ustaw hasło jednorazowe")
            pwd_dlg.resize(320, 120)
            pwd_layout = QVBoxLayout(pwd_dlg)
            pwd_layout.addWidget(QLabel("Nowe hasło jednorazowe:"))
            pwd_edit = QLineEdit()
            pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
            pwd_layout.addWidget(pwd_edit)
            
            pwd_btns = QHBoxLayout()
            pwd_ok = QPushButton("Ustaw")
            pwd_cancel = QPushButton("Anuluj")
            pwd_btns.addWidget(pwd_ok)
            pwd_btns.addWidget(pwd_cancel)
            pwd_layout.addLayout(pwd_btns)
            
            def on_pwd_ok():
                pw = pwd_edit.text()
                result = set_one_time_password(login, pw)
                if result is None:
                    QMessageBox.warning(pwd_dlg, "Błąd", "Hasło nie spełnia wymagań (min 6 znaków, 1 cyfra, 1 litera)")
                    return
                QMessageBox.information(pwd_dlg, "Sukces", f"Hasło jednorazowe ustawione dla {login}")
                self.reload()
                pwd_dlg.accept()
                dlg.accept()
            
            pwd_ok.clicked.connect(on_pwd_ok)
            pwd_cancel.clicked.connect(pwd_dlg.reject)
            pwd_dlg.exec()
        
        gen_btn.clicked.connect(on_generate)
        manual_btn.clicked.connect(on_manual)
        
        layout.addWidget(gen_btn)
        layout.addWidget(manual_btn)
        dlg.exec()