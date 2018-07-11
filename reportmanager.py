from PyQt5.QtCore import QObject


class ReportManager(QObject):
    def __init__(self, parent=None, reportEngine=None):
        super().__init__(parent)

        self._engine = reportEngine

