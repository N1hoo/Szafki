# Form implementation generated from reading ui file 'DodawanieSzafek.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_DodajSzafki(object):
    def setupUi(self, DodajSzafki):
        DodajSzafki.setObjectName("DodajSzafki")
        DodajSzafki.resize(556, 111)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=DodajSzafki)
        self.buttonBox.setGeometry(QtCore.QRect(500, 70, 51, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.MiejsceDS = QtWidgets.QComboBox(parent=DodajSzafki)
        self.MiejsceDS.setGeometry(QtCore.QRect(10, 30, 151, 31))
        self.MiejsceDS.setAccessibleName("")
        self.MiejsceDS.setEditable(True)
        self.MiejsceDS.setObjectName("MiejsceDS")
        self.NrSzDS = QtWidgets.QLineEdit(parent=DodajSzafki)
        self.NrSzDS.setGeometry(QtCore.QRect(310, 30, 71, 31))
        self.NrSzDS.setMaxLength(3)
        self.NrSzDS.setObjectName("NrSzDS")
        self.KodZDS = QtWidgets.QLineEdit(parent=DodajSzafki)
        self.KodZDS.setGeometry(QtCore.QRect(390, 30, 71, 31))
        self.KodZDS.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)
        self.KodZDS.setText("")
        self.KodZDS.setMaxLength(5)
        self.KodZDS.setObjectName("KodZDS")
        self.label_6 = QtWidgets.QLabel(parent=DodajSzafki)
        self.label_6.setGeometry(QtCore.QRect(10, 10, 40, 16))
        self.label_6.setObjectName("label_6")
        self.label_8 = QtWidgets.QLabel(parent=DodajSzafki)
        self.label_8.setGeometry(QtCore.QRect(310, 10, 45, 16))
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(parent=DodajSzafki)
        self.label_9.setGeometry(QtCore.QRect(390, 10, 58, 16))
        self.label_9.setWordWrap(True)
        self.label_9.setObjectName("label_9")
        self.PlecDS = QtWidgets.QComboBox(parent=DodajSzafki)
        self.PlecDS.setGeometry(QtCore.QRect(170, 30, 131, 31))
        self.PlecDS.setEditable(False)
        self.PlecDS.setObjectName("PlecDS")
        self.label_10 = QtWidgets.QLabel(parent=DodajSzafki)
        self.label_10.setGeometry(QtCore.QRect(170, 10, 76, 16))
        self.label_10.setWordWrap(True)
        self.label_10.setObjectName("label_10")
        self.DodajBtDS = QtWidgets.QPushButton(parent=DodajSzafki)
        self.DodajBtDS.setGeometry(QtCore.QRect(420, 70, 75, 31))
        self.DodajBtDS.setObjectName("DodajBtDS")
        self.StatusSzDS = QtWidgets.QComboBox(parent=DodajSzafki)
        self.StatusSzDS.setGeometry(QtCore.QRect(470, 30, 81, 31))
        self.StatusSzDS.setEditable(False)
        self.StatusSzDS.setObjectName("StatusSzDS")
        self.label_11 = QtWidgets.QLabel(parent=DodajSzafki)
        self.label_11.setGeometry(QtCore.QRect(470, 10, 64, 16))
        self.label_11.setObjectName("label_11")

        self.retranslateUi(DodajSzafki)
        self.buttonBox.accepted.connect(DodajSzafki.accept) # type: ignore
        self.buttonBox.rejected.connect(DodajSzafki.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(DodajSzafki)

    def retranslateUi(self, DodajSzafki):
        _translate = QtCore.QCoreApplication.translate
        DodajSzafki.setWindowTitle(_translate("DodajSzafki", "Dodawanie szafek"))
        self.MiejsceDS.setWhatsThis(_translate("DodajSzafki", "Wybór miejsca, w którym znajdować się mają szafki"))
        self.NrSzDS.setWhatsThis(_translate("DodajSzafki", "Wprowadź numer początkowej szafki (tej, od której numeru będą tworzyć się kolejne, np. 1 w przypadku, gdy tworzymy szafki od zera)"))
        self.KodZDS.setWhatsThis(_translate("DodajSzafki", "Wproszadź ilość szafek, która ma zostać dodana"))
        self.label_6.setText(_translate("DodajSzafki", "Miejsce"))
        self.label_8.setText(_translate("DodajSzafki", "Nr szafki"))
        self.label_9.setText(_translate("DodajSzafki", "Kod zamka"))
        self.PlecDS.setWhatsThis(_translate("DodajSzafki", "Typ dodawanych szafek"))
        self.label_10.setText(_translate("DodajSzafki", "Płeć docelowa"))
        self.DodajBtDS.setText(_translate("DodajSzafki", "Dodaj"))
        self.StatusSzDS.setWhatsThis(_translate("DodajSzafki", "Typ dodawanych szafek"))
        self.label_11.setText(_translate("DodajSzafki", "Status szafki"))
