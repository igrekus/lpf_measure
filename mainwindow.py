import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt


# TODO record commentaries from other users
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self.ui = uic.loadUi("mainwindow.ui", self)

        self.initDialog()

    def initDialog(self):
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
        twidth = self.ui.tableSuggestions.frameGeometry().width() - 30
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

    def onBtnAddClicked(self):
        pass

    def onBtnSaveClicked(self):
        pass

    def onBtnDelClicked(self):
        pass

    def onBtnApproveClicked(self):
        pass

    def onBtnRejectClicked(self):
        pass
