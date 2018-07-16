import subprocess
from PyQt5.QtCore import QObject
from export_xlsx import export_to_excel


class UiFacade(QObject):

    def __init__(self, parent=None, domainModel=None):
        super().__init__(parent)
        self._domainModel = domainModel

    def initFacade(self):
        print('init ui facade')

    def requestFindInstruments(self):
        return self._domainModel.findInstruments()

    def requestMeasure(self):
        self._domainModel.measure()

    def requestExportToPng(self):
        print('request export to .png')

    def requestExportToExcel(self):
        print('request export to .xlsx')
        to_export = [('cutoff_freq.xlsx', 'Код', 'Частота среза', self.parent()._plotWidget.cutoff_freq_x, self.parent()._plotWidget.cutoff_freq_y),
                     ('cutoff_delta.xlsx', 'Код', 'Дельта', self.parent()._plotWidget.cutoff_freq_delta_x, self.parent()._plotWidget.cutoff_freq_delta_y)]

        for ex in to_export:
            export_to_excel(ex)

        subprocess.call('explorer ' + '.\\excel\\', shell=True)



