import subprocess
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QAction
from PyQt5.QtCore import Qt

from domainmodel import DomainModel
from export_xlsx import export_to_excel
from plotwidget import PlotWidget
from uifacade import UiFacade


class MainWindowMeasure(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('./mw_measure.ui', self)

        self._domainModel = DomainModel(self)
        self._uiFacade = UiFacade(self, self._domainModel)
        self._plotWidget = PlotWidget(self, self._domainModel)

        self.actExportPng = QAction('Экспорт в .png', self)
        self.actExportExcel = QAction('Экспорт в Excel', self)
        self.actMeasure = QAction('Запустить измерение', self)
        self.actFindInstruments = QAction('Поиск оборудования', self)

        self.initDialog()

    def createActions(self):
        self.actFindInstruments.setStatusTip('Подключиться к оборудованию')
        self.actFindInstruments.triggered.connect(self.procActFindInstruments)

        self.actMeasure.setStatusTip('Экспортировать графики Excel-таблицу')
        self.actMeasure.triggered.connect(self.procActMeasure)

        self.actExportPng.setStatusTip('Экспортировать графики в изображение в формате PNG')
        self.actExportPng.triggered.connect(self.procActExportPng)

        self.actExportExcel.setStatusTip('Экспортировать графики Excel-таблицу')
        self.actExportExcel.triggered.connect(self.procActExportExcel)

    def setupSignals(self):
        # plot
        self._domainModel.measurementFinished.connect(self._plotWidget.processMeasurement)

        # ui
        # buttons
        self._ui.btnMeasure.clicked.connect(self.onBtnMeasureClicked)
        self._ui.btnFindInstruments.clicked.connect(self.onBtnFindInstrumentsClicked)
        self._ui.btnExportPng.clicked.connect(self.onBtnExportPngClicked)
        self._ui.btnExportExcel.clicked.connect(self.onBtnExportExcelClicked)

        # input widgets
        self._ui.spinCutoffMagnitude.valueChanged.connect(self.onSpinCutoffMagnitudeValueChanged)

    def initDialog(self):
        self.createActions()
        self.setupSignals()

        self._plotWidget.cutoffMag = -6
        self._plotWidget.initPlots()

        self.refreshView()

    # UI utility methods
    def refreshView(self):
        pass
        # twidth = self.ui.tableSuggestions.frameGeometry().width() - 30
        # self.ui.tableSuggestions.setColumnWidth(0, twidth * 0.05)
        # self.ui.tableSuggestions.setColumnWidth(1, twidth * 0.10)
        # self.ui.tableSuggestions.setColumnWidth(2, twidth * 0.55)
        # self.ui.tableSuggestions.setColumnWidth(3, twidth * 0.10)
        # self.ui.tableSuggestions.setColumnWidth(4, twidth * 0.15)
        # self.ui.tableSuggestions.setColumnWidth(5, twidth * 0.05)

    # event handlers
    def resizeEvent(self, event):
        self.refreshView()

    def onBtnExportPngClicked(self):
        self.actExportPng.trigger()

    def onBtnExportExcelClicked(self):
        self.actExportExcel.trigger()

    def onBtnFindInstrumentsClicked(self):
        self.actFindInstruments.trigger()

    def onBtnMeasureClicked(self):
        self.actMeasure.trigger()

    def onSpinCutoffMagnitudeValueChanged(self, value):
        self._plotWidget.cutoffMag = value

    # action processing
    def procActFindInstruments(self):
        if self._uiFacade.requestFindInstruments():
            self._ui.editArduino.setText(str(self._domainModel._arduino))
            self._ui.editAnalyzer.setText(str(self._domainModel._analyzer))
            self._ui.btnMeasure.setEnabled(True)
            self._ui.btnFindInstruments.setEnabled(False)
            self._ui.spinCutoffMagnitude.setEnabled(False)
            self._plotWidget.clearFigures()

    def procActMeasure(self):
        if self._domainModel.instrumentsReady:
            self._uiFacade.requestMeasure()
            self._ui.btnMeasure.setEnabled(False)
            self._ui.btnFindInstruments.setEnabled(True)
            self._ui.spinCutoffMagnitude.setEnabled(True)

    def procActExportPng(self):
        self._uiFacade.requestExportToPng()

    def procActExportExcel(self):
        self._uiFacade.requestExportToExcel()
