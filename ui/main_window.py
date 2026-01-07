# ui/main_window.py
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox
from PyQt6.QtCore import Qt

from ui_generated.ui_mainwindow import Ui_MainWindow

from ui.dialogs.nowi_pracownicy_dialog import NowiPracownicyDialog
from ui.renderers import render_lockers_table, render_employees_table, render_employee_lockers_panel

from services.lockers_service import LockersService
from services.employees_service import EmployeesService
from services.assignment_service import AssignmentService

from pracownicy import DF_PRACOWNICY

from DodawanieSzafek import Ui_DodajSzafki
from DodajPracownika import Ui_Dialog

from database import dodaj_szafke, edytuj_szafke, usun_szafke

class OknoGlowne(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Serwisy
        self.lockers = LockersService()
        self.employees = EmployeesService(self.lockers)
        self.assignment = AssignmentService()

        # Cache
        self._wszystkie_szafki = []
        self._szafki_by_kod = {}

        # Dodatkowe UI elementy
        self._init_panel_szafek_pracownika()
        self._init_nowi_pracownicy_button()

        # Responsywne layouty
        self._apply_responsive_layouts()

        # Teksty przycisków (bez dotykania generatora)
        self.UsunPr.setText("Zwolnij wszystkie szafki pracownika")

        self._connect_signals()

        # Start
        self.reload_all()

    # ---------- UI INIT ----------
    def _init_nowi_pracownicy_button(self):
        self.NowiPracownicyBt = QtWidgets.QPushButton(self.PracownicyTab)
        self.NowiPracownicyBt.setText("Nowi pracownicy")
        self.NowiPracownicyBt.clicked.connect(lambda: self.sprawdz_nowych_pracownikow(pokaz_zawsze=True))

    def _init_panel_szafek_pracownika(self):
        self.PanelSzafekPr = QtWidgets.QGroupBox(self.PracownicyTab)
        self.PanelSzafekPr.setTitle("Szafki pracownika")
        lay = QtWidgets.QVBoxLayout(self.PanelSzafekPr)

        self.LblPracownikInfo = QtWidgets.QLabel("Wybierz pracownika z tabeli po lewej.")
        self.LblPracownikInfo.setWordWrap(True)
        lay.addWidget(self.LblPracownikInfo)

        self.TabelaSzafekPr = QtWidgets.QTableWidget(self.PanelSzafekPr)
        self.TabelaSzafekPr.setColumnCount(4)
        self.TabelaSzafekPr.setHorizontalHeaderLabels(["Miejsce", "Nr szafki", "Nr zamka", "ID"])
        self.TabelaSzafekPr.setColumnHidden(3, True)
        self.TabelaSzafekPr.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.TabelaSzafekPr.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.TabelaSzafekPr.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        lay.addWidget(self.TabelaSzafekPr, 1)

        btn_row = QtWidgets.QHBoxLayout()
        self.BtnZwolnijWybranaSz = QtWidgets.QPushButton("Zwolnij zaznaczoną szafkę")
        self.BtnSkoczDoSzafki = QtWidgets.QPushButton("Pokaż w zakładce Szafki")
        btn_row.addWidget(self.BtnZwolnijWybranaSz)
        btn_row.addWidget(self.BtnSkoczDoSzafki)
        lay.addLayout(btn_row)

        self.BtnZwolnijWybranaSz.clicked.connect(self._zwolnij_szafke_z_panelu)
        self.BtnSkoczDoSzafki.clicked.connect(self._skocz_do_szafki_w_zakladce)

    def _apply_responsive_layouts(self):
        # central: TabWidget na cały obszar
        cw = self.centralwidget
        if cw.layout() is None:
            lay = QtWidgets.QVBoxLayout(cw)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(self.SzafkiWidget)

        self._layout_szafki_tab()
        self._layout_pracownicy_tab()

    def _layout_szafki_tab(self):
        tab = self.SzafkiTab
        if tab.layout() is not None:
            return
        root = QtWidgets.QVBoxLayout(tab)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(8)

        top.addWidget(self.groupBox)
        top.addStretch(1)

        btns = QtWidgets.QHBoxLayout()
        btns.setSpacing(8)
        btns.addWidget(self.DodajSz)
        btns.addWidget(self.PrzydzielSz)
        btns.addWidget(self.EdytujSz)
        btns.addWidget(self.ZwolnijSz)
        top.addLayout(btns)

        root.addLayout(top)
        root.addWidget(self.TabelaSzafek, 1)

    def _layout_pracownicy_tab(self):
        tab = self.PracownicyTab
        if tab.layout() is not None:
            return
        root = QtWidgets.QVBoxLayout(tab)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(8)

        top.addWidget(self.groupBox_2)
        top.addStretch(1)

        btns = QtWidgets.QHBoxLayout()
        btns.setSpacing(8)
        btns.addWidget(self.PrzydzielSzPr)
        btns.addWidget(self.UsunPr)
        btns.addWidget(self.NowiPracownicyBt)
        top.addLayout(btns)

        root.addLayout(top)

        split = QtWidgets.QSplitter(Qt.Orientation.Horizontal, tab)
        split.addWidget(self.TabelaPracownikow)
        split.addWidget(self.PanelSzafekPr)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)

        root.addWidget(split, 1)

    # ---------- SIGNALS ----------
    def _connect_signals(self):
        # Szafki
        self.DodajSz.clicked.connect(self.on_dodaj_szafke)
        self.EdytujSz.clicked.connect(self.on_edytuj_szafke)
        self.ZwolnijSz.clicked.connect(self.on_zwolnij_szafke)
        self.PrzydzielSz.clicked.connect(self.on_przydziel_szafke)

        self.SortWolne.stateChanged.connect(self.filtruj_tabele_szafek)
        self.MiejsceCB.currentIndexChanged.connect(self.filtruj_tabele_szafek)
        self.NrSz.textChanged.connect(self.filtruj_tabele_szafek)

        # Pracownicy
        self.PrzydzielSzPr.clicked.connect(self.on_przydziel_szafke_pracownikowi)
        self.UsunPr.clicked.connect(self._zwolnij_wszystkie_szafki_pracownika)

        self.NazwiskoPr.textChanged.connect(self.filtruj_tabele_pracownikow)
        self.ImiePr.textChanged.connect(self.filtruj_tabele_pracownikow)
        self.PlecPr.textChanged.connect(self.filtruj_tabele_pracownikow)
        self.DzialPr.textChanged.connect(self.filtruj_tabele_pracownikow)
        self.StanowiskoPr.textChanged.connect(self.filtruj_tabele_pracownikow)

        self.TabelaPracownikow.itemSelectionChanged.connect(self._odswiez_panel_szafek_pracownika)

    # ---------- RELOAD ----------
    def reload_all(self):
        self._wszystkie_szafki = self.lockers.get_all()
        self._szafki_by_kod = self.lockers.map_by_employee_code(self._wszystkie_szafki)

        self._reload_miejsca_combobox()
        self.filtruj_tabele_szafek()
        self.filtruj_tabele_pracownikow()
        self._odswiez_panel_szafek_pracownika()
        self.sprawdz_nowych_pracownikow(pokaz_zawsze=False)

    def _reload_miejsca_combobox(self):
        miejsca = sorted(set(r[1] for r in self._wszystkie_szafki if r and len(r) >= 2 and r[1]))
        self.MiejsceCB.blockSignals(True)
        self.MiejsceCB.clear()
        self.MiejsceCB.addItem("")
        self.MiejsceCB.addItems(miejsca)
        self.MiejsceCB.setEnabled(True)
        self.MiejsceCB.blockSignals(False)

    # ---------- HELPERS ----------
    def _selected_employee_code(self) -> str:
        row = self.TabelaPracownikow.currentRow()
        if row < 0:
            return ""
        item = self.TabelaPracownikow.item(row, 0)
        return (item.text() if item else "").strip()

    # ---------- PANEL ----------
    def _odswiez_panel_szafek_pracownika(self):
        kod = self._selected_employee_code()
        if not kod:
            self.LblPracownikInfo.setText("Wybierz pracownika z tabeli po lewej.")
            self.TabelaSzafekPr.setRowCount(0)
            return

        nazw = self.TabelaPracownikow.item(self.TabelaPracownikow.currentRow(), 1).text()
        im = self.TabelaPracownikow.item(self.TabelaPracownikow.currentRow(), 2).text()

        szafki = self._szafki_by_kod.get(kod, [])
        self.LblPracownikInfo.setText(f"<b>{kod}</b> — {nazw} {im}<br>Przypisane szafki: <b>{len(szafki)}</b>")
        render_employee_lockers_panel(self.TabelaSzafekPr, szafki)

    def _zwolnij_szafke_z_panelu(self):
        r = self.TabelaSzafekPr.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Brak zaznaczenia", "Zaznacz szafkę w panelu po prawej.")
            return
        id_item = self.TabelaSzafekPr.item(r, 3)
        if not id_item or not id_item.text().strip().isdigit():
            return
        locker_id = int(id_item.text().strip())

        potw = QMessageBox.question(
            self, "Potwierdź",
            f"Zwolnić szafkę (ID={locker_id}) z tego pracownika?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if potw != QMessageBox.StandardButton.Yes:
            return

        self.lockers.release_locker_by_id(locker_id, rows=self._wszystkie_szafki)
        self.reload_all()

    def _zwolnij_wszystkie_szafki_pracownika(self):
        kod = self._selected_employee_code()
        if not kod:
            QMessageBox.warning(self, "Brak pracownika", "Wybierz pracownika z tabeli po lewej.")
            return

        count = len(self._szafki_by_kod.get(kod, []))
        if count == 0:
            QMessageBox.information(self, "Brak szafek", "Ten pracownik nie ma przypisanych szafek.")
            return

        potw = QMessageBox.question(
            self, "Potwierdź",
            f"Zwolnić WSZYSTKIE szafki pracownika {kod}? (liczba: {count})",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if potw != QMessageBox.StandardButton.Yes:
            return

        self.lockers.release_all_for_employee(kod, rows=self._wszystkie_szafki)
        self.reload_all()

    def _skocz_do_szafki_w_zakladce(self):
        r = self.TabelaSzafekPr.currentRow()
        if r < 0:
            return
        id_item = self.TabelaSzafekPr.item(r, 3)
        if not id_item:
            return
        id_sz = id_item.text().strip()
        if not id_sz:
            return

        self.SzafkiWidget.setCurrentIndex(0)
        for i in range(self.TabelaSzafek.rowCount()):
            it = self.TabelaSzafek.item(i, 0)
            if it and it.text().strip() == id_sz:
                self.TabelaSzafek.selectRow(i)
                self.TabelaSzafek.scrollToItem(self.TabelaSzafek.item(i, 1))
                break

    # ---------- FILTRY + RENDER ----------
    def filtruj_tabele_szafek(self):
        miejsce_filtr = self.MiejsceCB.currentText().strip()
        nr_filtr = self.NrSz.text().strip()
        tylko_wolne = self.SortWolne.isChecked()

        filtered = []
        for r in self._wszystkie_szafki:
            if not r or len(r) < 14:
                continue

            miejsce = str(r[1] or "").strip()
            nr_sz = str(r[2] or "").strip()
            status = str(r[12] or "").strip()

            if miejsce_filtr and miejsce_filtr != miejsce:
                continue
            if nr_filtr and not nr_sz.startswith(nr_filtr):
                continue
            if tylko_wolne and status != "Wolna":
                continue

            filtered.append(r)

        render_lockers_table(self.TabelaSzafek, filtered)

    def on_kod_changed(self, ui):
        kod = ui.KodPracDP.text().strip()
        if not kod or kod not in DF_PRACOWNICY.index:
            if hasattr(ui, "NazwiskoDP"): ui.NazwiskoDP.setText("")
            if hasattr(ui, "ImieDP"): ui.ImieDP.setText("")
            return

        p = DF_PRACOWNICY.loc[kod]
        if hasattr(ui, "NazwiskoDP"): ui.NazwiskoDP.setText(str(p.get("Nazwisko","")))
        if hasattr(ui, "ImieDP"): ui.ImieDP.setText(str(p.get("Imię","")))
        
    def filtruj_tabele_pracownikow(self):
        nazwisko_f = self.NazwiskoPr.text().strip().lower()
        imie_f = self.ImiePr.text().strip().lower()
        plec_f = self.PlecPr.text().strip().lower()
        dzial_f = self.DzialPr.text().strip().lower()
        stan_f = self.StanowiskoPr.text().strip().lower()

        df = DF_PRACOWNICY.copy().reset_index()

        def s(x): return "" if x is None else str(x)

        lista = []
        for _, r in df.iterrows():
            kod  = s(r.get("Kod")).strip()
            nazw = s(r.get("Nazwisko")).strip()
            im   = s(r.get("Imię")).strip()
            dz   = s(r.get("Dział")).strip()
            stan = s(r.get("Stanowisko")).strip()
            plec = s(r.get("Płeć")).strip()
            dzatr = s(r.get("Data_zatrudnienia")).strip()
            dzw   = s(r.get("Data_zwolnienia")).strip()

            if nazwisko_f and nazwisko_f not in nazw.lower(): continue
            if imie_f and imie_f not in im.lower():           continue
            if plec_f and plec_f not in plec.lower():         continue
            if dzial_f and dzial_f not in dz.lower():         continue
            if stan_f and stan_f not in stan.lower():         continue

            sz_list = self._szafki_by_kod.get(kod, [])
            lista.append({
                "Kod": kod,
                "Nazwisko": nazw,
                "Imię": im,
                "Płeć": plec,
                "Dział": dz,
                "Stanowisko": stan,
                "Data_zatrudnienia": dzatr,
                "Data_zwolnienia": dzw,
                "Szafki_count": len(sz_list),
            })

        render_employees_table(self.TabelaPracownikow, lista)

    # ---------- NOWI PRACOWNICY ----------
    def sprawdz_nowych_pracownikow(self, *, pokaz_zawsze=False):
        new_codes = self.employees.find_new_active_without_lockers(self._wszystkie_szafki)

        if not new_codes:
            if pokaz_zawsze:
                QMessageBox.information(self, "Nowi pracownicy", "Nie znaleziono nowych aktywnych pracowników bez szafki.")
            return

        df_new = DF_PRACOWNICY.loc[new_codes].reset_index()
        dlg = NowiPracownicyDialog(df_new, parent=self)
        dlg.exec()

    def on_przydziel_szafke(self):
        wiersz = self.TabelaSzafek.currentRow()
        if wiersz < 0:
            QMessageBox.warning(self, "Brak zaznaczenia", "Zaznacz szafkę.")
            return

        locker_id_txt = self.TabelaSzafek.item(wiersz, 0).text().strip()
        if not locker_id_txt.isdigit():
            QMessageBox.warning(self, "Błąd", "Nie mogę odczytać ID szafki.")
            return
        locker_id = int(locker_id_txt)

        dialog = QDialog(self)
        ui = Ui_Dialog()
        ui.setupUi(dialog)

        # (opcjonalnie) wypełnij numer szafki w dialogu
        nr_szafki = self.TabelaSzafek.item(wiersz, 2).text()
        if hasattr(ui, "NrSzSzDP1"):
            ui.NrSzSzDP1.setText(nr_szafki)

        ui.PlecDP.clear()
        ui.PlecDP.addItems(["Kobieta", "Mężczyzna"])

        stanowiska = sorted(set(DF_PRACOWNICY["Stanowisko"].dropna()))
        ui.StanowiskoDP.clear()
        ui.StanowiskoDP.addItems(stanowiska)

        dzialy = sorted(set(DF_PRACOWNICY["Dział"].dropna()))
        ui.DzialDP.clear()
        ui.DzialDP.addItems(dzialy)

        miejsca = sorted(set(row[1] for row in self._wszystkie_szafki if row[1]))
        ui.MiejsceDP.clear()
        ui.MiejsceDP.addItems(miejsca)

        ui.KodPracDP.textChanged.connect(lambda _: self.on_kod_changed(ui))

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        kod = ui.KodPracDP.text().strip()
        nazw = ui.NazwiskoDP.text().strip() if hasattr(ui, "NazwiskoDP") else ""
        imie = ui.ImieDP.text().strip() if hasattr(ui, "ImieDP") else ""
        dzial = ui.DzialDP.currentText().strip() if hasattr(ui, "DzialDP") else ""
        stan = ui.StanowiskoDP.currentText().strip() if hasattr(ui, "StanowiskoDP") else ""
        plec = ui.PlecDP.currentText().strip() if hasattr(ui, "PlecDP") else ""

        if not kod:
            QMessageBox.warning(self, "Brak kodu", "Wpisz kod pracownika.")
            return

        ok = self.assignment.assign_locker_to_employee(
            locker_id,
            kod_pracownika=kod,
            nazwisko=nazw,
            imie=imie,
            dzial=dzial,
            stanowisko=stan,
            plec=plec,
            status="Zajęta",
        )

        if not ok:
            QMessageBox.warning(self, "Błąd", "Nie udało się przypisać szafki.")
            return

        self.reload_all()