# -*- coding: utf-8 -*-
# pdfrenamer/views.py

"""This module provides the PdfRenameWithView main window."""

from collections import deque
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox
from .ui.window import Ui_Window

FILTERS = ";;".join(
    (
        # "PNG Files (*.png)",
        # "JPEG Files (*.jpeg)",
        # "JPG Files (*.jpg)",
        # "GIF Files (*.gif)",
        # "Text Files (*.txt)",
        # "Python Files (*.py)",
        "PDF Files (*.pdf)",
    )
)
class Window(QWidget, Ui_Window):
    def __init__(self):
        super().__init__()
        self._files = deque()
        self._union = "_"
        self._filesCount = len(self._files)
        self._setupUI()
        self._connectSignalsSlots()

    def _setupUI(self):
        self.setupUi(self)
        self._updateStateWhenNoFiles()

    def _connectSignalsSlots(self):
        self.loadFilesButton.clicked.connect(self.loadFiles)
        self.nextButton.clicked.connect(self.nextFile)
        self.renameButton.clicked.connect(self.renameFiles)
        self.IdInput.textChanged.connect(self._updatePrefixEdit)
        self.DateInput.dateChanged.connect(self._updatePrefixEdit)
        self.TypeList.currentItemChanged.connect(self._updatePrefixEdit)
        self.newNameInput.textChanged.connect(self._updateStateWhenReady)
        self.DateCheckBox.clicked.connect(self._checkFecha)
        self.IdCheckBox.clicked.connect(self._checkDocumento)
        self.TypeCheckBox.clicked.connect(self._checkTipo)

    def _checkFecha(self):
        self.DateInput.setEnabled(self.DateCheckBox.isChecked())
        self._updatePrefixEdit()

    def _checkDocumento(self):
        self.IdInput.setEnabled(self.IdCheckBox.isChecked())
        self._updatePrefixEdit()

    def _checkTipo(self):
        self.TypeList.setEnabled(self.TypeCheckBox.isChecked())
        self._updatePrefixEdit()

    def _getDatos(self):
        lista = []
        if len(self.DateInput.text().strip()) and self.DateInput.isEnabled():
            lista.append(self.DateInput.text().strip())
        if len(self.IdInput.text().strip()) and self.IdInput.isEnabled():
            lista.append("ID%s%s" % (self._union, self.IdInput.text().strip()))
        if self.TypeList.currentItem() is not None and self.TypeList.isEnabled():
            if len(self.TypeList.currentItem().text().strip()):
                lista.append(self.TypeList.currentItem().text().strip())
        return lista

    def _updatePrefixEdit(self):
        nombre = self._getDatos()
        n = ""
        for i in nombre:
            n += "%s%s" % (self._union, i) if len(n) else i
        n += ".pdf"
        self.newNameInput.setText(n)
        if len(self.newNameInput.text()):
            self.newNameInput.setEnabled(True)

    def _updateStateWhenReady(self):
        if self.newNameInput.text() and self._filesCount:
            self.renameButton.setEnabled(True)
            self.nextButton.setEnabled(True)
        else:
            self.renameButton.setEnabled(False)
            self.nextButton.setEnabled(False)

    def _loadFirstFile(self):
        self._filesCount = len(self._files)
        self.fileDirectoryLabel.setText("(%s archivo/s) %s" % (self._filesCount, Path(self._files[0]).name))
        self.pdfViewer.load(QtCore.QUrl.fromLocalFile(str(Path(self._files[0]))))

    def loadFiles(self):
        if self.fileDirectoryInput.text():
            initDir = self.fileDirectoryInput.text()
        else:
            initDir = str(Path.home())
        files, filter = QFileDialog.getOpenFileNames(
            self, "Elegir archivos a renombrar", initDir, filter=FILTERS
        )
        if len(files) > 0:
            self.fileDirectoryInput.setText("%s_CI_%s_%s.pdf" % (self.DateInput, self.IdInput, self.TypeList.selectedItems()))
            self._files.clear()
            self.fileDirectoryInput.setText(str(Path(files[0]).parent))
            for file in files:
                self._files.append(Path(file))
            self._loadFirstFile()
            self._updateStateWhenFilesLoaded()

    def nextFile(self):
        try:
            self._files.popleft()
            self._loadFirstFile()
        except IndexError:
            self._updateStateWhenNoFiles()

    def renameFiles(self):
        prefix = self.newNameInput.text()
        newFile = self._files[0].parent.joinpath(
            f"{prefix}"
        )
        if Path.exists(newFile):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Archivo ya existe")
            dlg.setText("¿Desea sobreescribir el archivo?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()
            if button == QMessageBox.Yes:
                self._files[0].rename(newFile)
                self._updateStateWhenFileRenamed()
        else:
            self._files[0].rename(newFile)
            self._updateStateWhenFileRenamed()

    def _updateStateWhenNoFiles(self):
        print('No hay archivos')
        self._filesCount = len(self._files)
        self.loadFilesButton.setEnabled(True)
        self.loadFilesButton.setFocus(True)
        self.renameButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.newNameInput.clear()
        self.newNameInput.setEnabled(False)
        self.fileDirectoryLabel.setText("(0 archivo/s) nombre_original.pdf")
        self.pdfViewer.load(QtCore.QUrl(":pdf"))

    def _updateStateWhenFilesLoaded(self):
        self.newNameInput.setEnabled(True)
        self.newNameInput.setFocus(True)

    def _updateStateWhenFileRenamed(self):
        try:
            self._files.popleft()
            self._loadFirstFile()
        except IndexError:
            print('Fin de archivos')
            self._updateStateWhenNoFiles()