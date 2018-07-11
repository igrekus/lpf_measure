from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar
import numpy

class PlotWidget(QObject):

    def __init__(self, parent=None, domainModel=None):
        super().__init__(parent)

        self._domainModel = domainModel

        self._cutoffMag = -6.0
        self._cutoffTickAdded = False

        self.figure11 = None
        self.canvas11 = None
        self.toolbar11 = None

    def initPlots(self):
        plt.figure(num=1)

        self.figure11 = plt.figure(1)
        self.canvas11 = FigureCanvas(self.figure11)
        self.toolbar11 = NavToolbar(canvas=self.canvas11, parent=None)
        self.parent()._ui.layoutMainPlot.addWidget(self.canvas11)
        self.parent()._ui.layoutMainPlot.addWidget(self.canvas11.toolbar)

        self.resetPlots()

    def resetPlots(self):
        plt.figure(1)
        plt.subplots_adjust(bottom=0.150)
        plt.axhline(self._cutoffMag, 0, 1, linewidth=0.8, color="0.3", linestyle="--")
        plt.title("Коэффициент преобразования")
        plt.xscale("log")
        plt.xlabel("F, Гц")
        plt.ylabel("К-т пр., дБ")
        plt.ylim([-60, 10])
        plt.grid(b=True, which="minor", color="0.7", linestyle='--')
        plt.grid(b=True, which="major", color="0.5", linestyle='-')
        # plt.autoscale(False)

    def clearFigures(self):
        plt.figure(1).axes.clear()
        plt.figure(1).lines.clear()
        # self.resetPlots()

    def parseMeasurementStr(self, string):
        return [float(num) for num in string.split(',')]

    @property
    def cutoffMag(self):
        return self._cutoffMag

    @cutoffMag.setter
    def cutoffMag(self, value: float):
        self._cutoffMag = value
        self._cutoffTickAdded = False

    @pyqtSlot()
    def processMeasurement(self):
        print('processing measurement')
        freqs = self.parseMeasurementStr(self._domainModel._lastMeasurement[0])
        amps = self.parseMeasurementStr(self._domainModel._lastMeasurement[1])

        if not self._cutoffTickAdded:
            plt.yticks(list(plt.yticks())[0] + [self._cutoffMag])
            self._cutoffTickAdded = True

        plt.figure(1)
        plt.plot(freqs, amps, color="0.4")
        plt.ylim([-60, 10])
        plt.grid(b=True, which="minor", color="0.7", linestyle='--')
        plt.grid(b=True, which="major", color="0.5", linestyle='-')
        self.figure11.canvas.draw()

        # print(self._domainModel._lastMeasurement)

