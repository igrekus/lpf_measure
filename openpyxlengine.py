import os
from PyQt5.QtCore import QObject
import openpyxl


class OpenpyxlEngine(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def export(self):
        pass
