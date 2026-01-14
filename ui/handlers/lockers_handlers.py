from PyQt6.QtWidgets import QDialog, QMessageBox, QComboBox, QLabel
from PyQt6 import QtGui

from ui_generated.ui_dodaj_szafki import Ui_DodajSzafki
from database import dodaj_szafke, edytuj_szafke, usun_szafke
from session import get_current_user, is_admin


class LockersHandlersMixin:
    def on_dodaj_szafke(self):
        """Otwiera dialog dodawania szafek"""
        from ui.dialogs.dodaj_szafki_dialog import DodajSzafkiDialog
        dialog = DodajSzafkiDialog(self, lockers_data=self._wszystkie_szafki)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.reload_all()

    def on_edytuj_szafke(self):
        """Obsługuje dodawanie i edycję szafek"""
        row = self.TabelaSzafek.currentRow()
        
        # Brak zaznaczenia - otwórz dialog dodawania
        if row < 0:
            self.on_dodaj_szafke()
            return
        
        # Zaznaczony wiersz - dialog edycji
        id_item = self.TabelaSzafek.item(row, 0)
        if not id_item or not id_item.text().strip().isdigit():
            QMessageBox.warning(self, "Błąd", "Nie mogę odczytać ID szafki.")
            return
        id_sz = int(id_item.text().strip())

        dialog = QDialog(self)
        ui = Ui_DodajSzafki()
        ui.setupUi(dialog)

        # Sprawdzenie uprawnień: admin lub właściwy dział
        id_item = self.TabelaSzafek.item(row, 0)
        id_sz = int(id_item.text().strip()) if id_item and id_item.text().strip().isdigit() else None
        orig = next((x for x in getattr(self, '_wszystkie_szafki', []) if x and x[0] == id_sz), None)
        db_dzial = orig[14] if orig and len(orig) >= 15 else ''
        u = get_current_user()
        if not is_admin() and u and (u.get('dzial') or '').strip() != (db_dzial or '').strip():
            QMessageBox.warning(self, "Brak uprawnień", "Nie możesz edytować szafki z innego działu.")
            return

        # Wypełnienie pól z zaznaczonego wiersza
        if self.TabelaSzafek.item(row, 1):
            ui.MiejsceDS.setEditText(self.TabelaSzafek.item(row, 1).text())
        if self.TabelaSzafek.item(row, 2):
            ui.NrSzDS.setText(self.TabelaSzafek.item(row, 2).text())
        if self.TabelaSzafek.item(row, 3):
            ui.KodZDS.setText(self.TabelaSzafek.item(row, 3).text())
        # Kod właściciela (kolumna 5)
        if self.TabelaSzafek.item(row, 5):
            ui.KodWlascicelaDS.setText(self.TabelaSzafek.item(row, 5).text())
        # Uwagi (kolumna 13)
        if self.TabelaSzafek.item(row, 13):
            ui.UwagiDS.setText(self.TabelaSzafek.item(row, 13).text())

        # Fizyczna lokalizacja szafki z cache
        orig = next((x for x in getattr(self, '_wszystkie_szafki', []) if x and x[0] == id_sz), None)
        db_dzial = orig[14] if orig and len(orig) >= 15 else ''

        # Selektor działu dla adminów
        phys_cb = QComboBox()
        phys_list = sorted({str(x[14]).strip() for x in getattr(self, '_wszystkie_szafki', []) if x and len(x) > 14 and x[14]})
        if db_dzial and db_dzial not in phys_list:
            phys_list.insert(0, db_dzial)
        if phys_list:
            phys_cb.addItem("")
            phys_cb.addItems(phys_list)
        u = get_current_user()
        is_admin_user = bool(u and u.get('role') == 'admin')
        if is_admin_user:
            phys_cb.setEnabled(True)
        else:
            phys_cb.addItem(db_dzial)
            phys_cb.setCurrentText(db_dzial)
            phys_cb.setEnabled(False)
        # Layout dialogu
        from PyQt6.QtWidgets import QVBoxLayout
        if dialog.layout() is None:
            dialog.setLayout(QVBoxLayout())
        try:
            dialog.layout().insertWidget(dialog.layout().count() - 1, QLabel("Dział szafki:"))
            dialog.layout().insertWidget(dialog.layout().count() - 1, phys_cb)
        except Exception:
            dialog.layout().addWidget(QLabel("Dział szafki:"))
            dialog.layout().addWidget(phys_cb)

        ui.PlecDS.clear()
        ui.PlecDS.addItems(["Kobieta", "Mężczyzna", "Neutralna"])
        if self.TabelaSzafek.item(row, 4):
            ui.PlecDS.setCurrentText(self.TabelaSzafek.item(row, 4).text())

        ui.StatusSzDS.clear()
        ui.StatusSzDS.addItems(["Wolna", "Nieczynna"])
        if self.TabelaSzafek.item(row, 12):
            ui.StatusSzDS.setCurrentText(self.TabelaSzafek.item(row, 12).text())

        from PyQt6 import QtGui
        validator = QtGui.QIntValidator(0, 999999, self)
        ui.NrSzDS.setValidator(validator)
        ui.KodZDS.setValidator(validator)
        
        # Nr szafki tylko do odczytu dla zwykłych użytkowników
        ui.NrSzDS.setReadOnly(not is_admin_user)

        def klik_edytuj():
            miejsce = ui.MiejsceDS.currentText().strip()
            nr_sz = int(ui.NrSzDS.text()) if ui.NrSzDS.text() else None
            nr_zamka = int(ui.KodZDS.text()) if ui.KodZDS.text() else None
            plec_szatni = ui.PlecDS.currentText().strip()
            kod_prac = ui.KodWlascicelaDS.text().strip()
            status = ui.StatusSzDS.currentText().strip()
            komentarz = ui.UwagiDS.text().strip()

            # Zachowanie lub zmiana fizycznej lokalizacji
            db_choice = phys_cb.currentText().strip() if is_admin_user else db_dzial
            # Użycie serwisu do edycji z logowaniem
            from services.lockers_service import LockersService
            svc = LockersService()
            svc.edit_locker(
                id_szafki=id_sz,
                miejsce=miejsce,
                nr_szafki=nr_sz,
                nr_zamka=nr_zamka,
                plec_szatni=plec_szatni,
                kod_pracownika=kod_prac,
                dzial=db_choice,
                status=status,
                komentarz=komentarz,
            )
            dialog.accept()

        def klik_usun():
            reply = QMessageBox.question(
                dialog, "Potwierdzenie usunięcia",
                "Czy na pewno chcesz usunąć szafkę?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Log zdarzenia przed usunięciem
                try:
                    from history import log_event
                    from session import get_current_user
                    from services.lockers_service import LockersService
                    
                    performed_by = (get_current_user() or {}).get('login')
                    svc = LockersService()
                    before_dict = svc._row_to_dict(orig) if orig else {}
                    
                    usun_szafke(id_sz)
                    
                    # Log z migawką przed (after puste dla usunięcia)
                    log_event("delete", id_sz, before_dict, {}, performed_by)
                except Exception:
                    # Jeśli log się nie uda, usuń mimo to
                    usun_szafke(id_sz)
                
                dialog.accept()

        # Podłączenie przycisków
        ui.buttonBox.button(ui.buttonBox.StandardButton.Ok).clicked.connect(klik_edytuj)
        ui.buttonBox.button(ui.buttonBox.StandardButton.Cancel).clicked.connect(dialog.reject)
        ui.UsunBtDS.clicked.connect(klik_usun)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.reload_all()

    def on_zwolnij_szafke(self):
        row = self.TabelaSzafek.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Brak zaznaczenia", "Zaznacz szafkę.")
            return
        id_item = self.TabelaSzafek.item(row, 0)
        if not id_item or not id_item.text().strip().isdigit():
            QMessageBox.warning(self, "Błąd", "Nie mogę odczytać ID szafki.")
            return
        locker_id = int(id_item.text().strip())
        potw = QMessageBox.question(
            self, "Potwierdź",
            f"Zwolnić szafkę (ID={locker_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if potw != QMessageBox.StandardButton.Yes:
            return

        # Sprawdzenie uprawnień: admin lub właściwy dział
        id_item = self.TabelaSzafek.item(row, 0)
        id_sz = int(id_item.text().strip()) if id_item and id_item.text().strip().isdigit() else None
        orig = next((x for x in getattr(self, '_wszystkie_szafki', []) if x and x[0] == id_sz), None)
        db_dzial = orig[14] if orig and len(orig) >= 15 else ''
        u = get_current_user()
        if not is_admin() and u and (u.get('dzial') or '').strip() != (db_dzial or '').strip():
            QMessageBox.warning(self, "Brak uprawnień", "Nie możesz zwolnić szafki z innego działu.")
            return

        self.lockers.release_locker_by_id(locker_id, rows=self._wszystkie_szafki, current_user=u)
        self.reload_all()