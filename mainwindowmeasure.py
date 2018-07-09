import subprocess
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QAction
from PyQt5.QtCore import Qt

from export_xlsx import export_to_excel


class MainWindowMeasure(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self.ui = uic.loadUi("./mw_measure.ui", self)

        self.actExportPng = QAction("Экспорт в .png", self)
        self.actExportXlsx = QAction("Экспорт в Excel", self)

        # data, make separate stat_processor class
        self.cutoff_freq_x = list()
        self.cutoff_freq_y = list()
        self.cutoff_freq_delta_x = list()
        self.cutoff_freq_delta_y = list()

        self.initDialog()

    def createActions(self):
        self.actExportPng.setStatusTip("Экспортировать графики в изображение в формате PNG")
        self.actExportPng.triggered.connect(self.procActExportPng)

        self.actExportXlsx.setStatusTip("Экспортировать графики Excel-таблицу")
        self.actExportXlsx.triggered.connect(self.procActExportXlsx)

    def setupUiSignals(self):
        self.ui.btnExportPng.clicked.connect(self.onBtnExportPngClicked)
        self.ui.btnExportXlsx.clicked.connect(self.onBtnExportXlsxClicked)

    def initDialog(self):
        self.createActions()
        self.setupUiSignals()
        # init instances
        # self._data_mapper.setModel(self._model_search_proxy)

        # init UI
        # self.ui.comboAuthorFilter.setModel(self._model_authors)
        # self.ui.tableSuggestions.setModel(self._model_search_proxy)

        # setup signals
        # table
        # self.ui.tableSuggestions.selectionModel().currentChanged.connect(self.onSelectionChanged)
        # self.ui.tableSuggestions.clicked.connect(self.onTableClicked)
        # buttons
        # self.ui.btnAdd.clicked.connect(self.onBtnAddClicked)
        # self.ui.btnDel.clicked.connect(self.onBtnDelClicked)
        # self.ui.btnSave.clicked.connect(self.onBtnSaveClicked)
        # self.ui.btnApprove.clicked.connect(self.onBtnApproveClicked)
        # self.ui.btnReject.clicked.connect(self.onBtnRejectClicked)

        # update UI depending on user level
        self.setupControls()
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

    def setupControls(self):
        pass

    def updateUiControls(self):
        pass
        # self._model_search_proxy.invalidate()
        # if self._model_suggestions.has_dirty_data:
        #     self.ui.btnSave.setEnabled(True)
        # else:
        #     self.ui.btnSave.setEnabled(False)

    # event handlers
    def resizeEvent(self, event):
        self.refreshView()

    def onBtnExportPngClicked(self):
        print("png click")
        self.actExportPng.trigger()

    def onBtnExportXlsxClicked(self):
        print("xlsx click")
        self.actExportXlsx.trigger()

    def procActExportPng(self):
        print("png act")

    def procActExportXlsx(self):
        print("Пишем .xlsx файлы.")
        to_export = [("cutoff_freq.xlsx", "Код", "Частота среза", self.cutoff_freq_x, self.cutoff_freq_y),
                     ("cutoff_delta.xlsx", "Код", "Дельта", self.cutoff_freq_delta_x, self.cutoff_freq_delta_y)]

        for ex in to_export:
            export_to_excel(ex)

        subprocess.call("explorer " + '.\\excel\\', shell=True)
